import curses
import os
import random
import string
import time

from sys import platform
from skabenclient.device import BaseDevice

from config import BoilerplateConfig


class BoilerplateDevice(BaseDevice):
    """Test device should be able to generate all kind of messages

    state_reload -> загрузить текущий конфиг из файла
    state_update(data) -> записать конфиг в файл (и послать на сервер)
    send_message(data) -> отправить сообщение от имени девайса во внутреннюю очередь
    """

    config_class = BoilerplateConfig

    rows_count = 16

    _screen_path = os.path.join(os.getcwd(), "resources/screens/")
    _text_path = os.path.join(os.getcwd(), "resources/text/")
    _audio_path = os.path.join(os.getcwd(), "resources/audio/")
    _img_path = os.path.join(os.getcwd(), "resources/images/")
    _video_path = os.path.join(os.getcwd(), "resources/video/")
    _word_path = os.path.join(os.getcwd(), "resources/wordsets/")

    def __init__(self, system_config, device_config):
        super().__init__(system_config, device_config)
        self.running = None
        main_conf = dict()
        main_conf["forceClose"] = False
        main_conf["is_db_updating"] = False
        main_conf["db_updated"] = False
        main_conf["previousState"] = ""
        main_conf["dbCheckInterval"] = 2
        main_conf["delayTime"] = 40
        main_conf["lockTimeOutStart"] = 0

    def run(self):
        """Main device run routine

        в супере он создает сообщение во внутренней очереди что девайс запущен.
        """
        super().run()
        self.running = True
        while self.running:
            self.start_terminal()

    def check_status(self) -> bool:
        conditions = [
            self.main_conf["previousState"] != "Unpowered" and not self.config.get("isPowerOn"),
            self.config.get("isLocked") and self.main_conf["previousState"] != "Locked",
            self.config.get("isHacked") and self.main_conf["previousState"] != "Hacked",
        ]
        if all(conditions):
            return all(conditions)
        if self.main_conf["db_updated"]:
            self.main_conf["db_updated"] = False
        return False

    @staticmethod
    def init_curses():
        curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.noecho()
        curses.raw()
        curses.curs_set(2)

    def load_words(self, word_len: int) -> list[str]:
        with open(os.path.join(self.main_conf["word_path"], f"words{word_len}.txt")) as fh:
            words = [word.strip("\r\n\t ") for word in fh.readlines()]
        return words

    @staticmethod
    def get_str_pos(x: int, y: int):
        if x < 32:
            y_new = y
            x_new = x - 8
        else:
            y_new = y + 17
            x_new = x - 32
        return y_new * 12 + x_new

    @staticmethod
    def get_str_coords(str_pos: int) -> tuple[int, int]:
        if str_pos < 204:
            y = int(str_pos / 12)
            x = str_pos % 12 + 8
        else:
            y = int(str_pos / 12) - 17
            x = str_pos % 12 + 32
        return x, y

    @staticmethod
    def check_word_position(char_index: int, word_str: str) -> tuple[str, int, int]:  # Символ проверим на всякий случай
        if not word_str[char_index].isalpha():
            return "", -1, -1
        i = char_index
        while word_str[i].isalpha():
            if i == 0:
                i = -1
                break
            i -= 1
        start_pos = i + 1
        i = char_index
        while word_str[i].isalpha():
            if i == len(word_str) - 1:
                i = len(word_str)
                break
            i += 1
        end_pos = i - 1
        sel_word = word_str[start_pos : end_pos + 1]
        return sel_word, start_pos, end_pos

    @staticmethod
    def check_cheat_position(char_index: int, word_str: str) -> tuple[str, int, int]:
        left_par = ["[", "(", "{", "<"]
        right_par = ["]", ")", "}", ">"]
        direct = 0
        start_pos = -1
        end_pos = -1
        control_char = 0

        if word_str[char_index] in left_par:
            direct = 1
            start_pos = char_index
            control_char = right_par[left_par.index(word_str[char_index])]

        if word_str[char_index] in right_par:
            direct = -1
            end_pos = char_index - 1
            control_char = left_par[right_par.index(word_str[char_index])]

        if direct == 0:
            return "", -1, -1

        i = char_index + direct
        if i > (len(word_str) - 1) or i < 0:
            return "", -1, -1
        start_sub_str = int(char_index / 12) * 12
        end_sub_str = start_sub_str + 11
        i = char_index

        if not control_char:
            raise ValueError("missing control char")

        while word_str[i] != control_char:
            if word_str[i].isalpha():
                return "", -1, -1
            i += direct
            if i <= start_sub_str or i > end_sub_str:
                return "", -1, -1
        if start_pos == -1:
            start_pos = i
        if end_pos == -1:
            end_pos = i - 1
        cheat_str = word_str[start_pos : end_pos + 2]
        return cheat_str, start_pos, end_pos

    @staticmethod
    def del_from_str(all_str: str, start_pos: int, end_pos: int) -> str:
        new_str = all_str[0:start_pos] + "." * (end_pos - start_pos) + all_str[end_pos:]
        return new_str

    def gen_string(self, word_quan: int, str_len: int, dictionary: list[str]) -> tuple[str, list[str], str]:
        """
        Функция формирует строку для вывода в терминал. Строка представляет собой 'мусорные' символы,
        между которыми вставлены слова для подбора пароля.
        """
        password = dictionary[random.randint(0, len(dictionary) - 1)]
        word_len = len(dictionary[0])
        word_list = self.words_select(dictionary, password, word_quan)
        screen_str = ""
        len_area = int(str_len / word_quan)
        i = 0
        while i < word_quan:
            start_pos = random.randint(i * len_area, i * len_area + (len_area - word_len - 1))
            j = i * len_area
            while j < start_pos:
                screen_str += random.choice(string.punctuation)
                j += 1
            screen_str += word_list[i]
            screen_str += random.choice(string.punctuation)
            j += word_len + 1
            while j < (i + 1) * len_area:
                screen_str += random.choice(string.punctuation)
                j += 1
            i += 1
        i = len(screen_str)
        while i < str_len:
            screen_str += random.choice(string.punctuation)
            i += 1
        word_list.remove(password)
        return password, word_list, screen_str

    @staticmethod
    def compare_words(f_word: str, s_word: str) -> int:
        i = 0
        count = 0
        for char in f_word:
            if char == s_word[i]:
                count += 1
            i += 1
        return count

    def words_select(self, words: str, pwd: str, word_quan: int) -> list[str]:
        word_len = len(pwd)
        word_list_max = []  # Слова, максимально похожие по расположению букв на слово-пароль
        word_list_zero = []  # Слова, совершенно не имеющие одинаково расположенных букв с паролем
        word_list_other = []  # Все прочие слова из списка
        word_list_selected = []  # Слова, которые будут использоваться непосредственно в игре
        word_delta = 1
        while len(word_list_max) == 0:
            for word in words:
                if word != pwd:
                    c = self.compare_words(word, pwd)
                    if c == 0:
                        word_list_zero.append(word)
                    elif c == (word_len - word_delta):
                        word_list_max.append(word)
                    else:
                        word_list_other.append(word)
            word_delta += 1
        word_list_selected.append(pwd)  # Пароль
        if len(word_list_max) > 0:  # Одно слово, максимально близкое к паролю
            word_list_selected.append(word_list_max[random.randint(0, len(word_list_max) - 1)])
        if len(word_list_zero) > 0:  # Одно слово, которое совершенно не похоже на пароль
            word_list_selected.append(word_list_zero[random.randint(0, len(word_list_zero) - 1)])
        i = 0
        while i < word_quan - 3:  # Добавляем ещё слов из общего списка
            word = word_list_other[random.randint(0, len(word_list_other) - 1)]
            if word not in word_list_selected:
                word_list_selected.append(word)
                i += 1
        random.shuffle(word_list_selected)  # Перемешиваем.
        return word_list_selected

    @staticmethod
    def del_random_word(word_list: list[str], all_str: str) -> tuple[int, list[str], str]:
        word_num = random.randint(0, len(word_list) - 1)
        word = word_list[word_num]
        start_pos = all_str.index(word)
        word_list.remove(word)
        all_str = all_str.replace(word, "." * len(word))
        return start_pos, word_list, all_str

    def out_screen(self, par_name: str, delay_after=2) -> bool:
        curses.curs_set(2)
        full_screen_win = curses.newwin(24, 80, 0, 0)
        full_screen_win.clear()
        full_screen_win.refresh()
        full_screen_win.nodelay(True)
        _par_name: str = self.config.get(par_name)
        if not _par_name:
            raise ValueError("missing par_name")

        with open(os.path.join(self.main_conf["screen_path"], _par_name)) as fh:
            out_txt_str = fh.read()
        status = self.out_header(out_txt_str, full_screen_win)
        if delay_after > 0:
            time.sleep(delay_after)
        return status

    def out_header(self, out_str: str, win: curses.window) -> bool:
        win.clear()
        win.refresh()
        win.nodelay(True)
        my_delay = self.main_conf["delayTime"]
        y = 0
        x = 0
        for ch in out_str:
            key = win.getch()
            if (key == curses.KEY_ENTER or key == ord(" ")) and my_delay == self.main_conf["delayTime"]:
                my_delay = self.main_conf["delayTime"] / 4
            if ch == "\n":
                y += 1
                x = 0
                continue
            win.addstr(y, x, ch, curses.color_pair(1) | curses.A_BOLD)
            time.sleep(my_delay / 1000)
            win.refresh()
            x += 1
            if self.check_status():
                return True
        return False

    @staticmethod
    def clear_screen():
        full_screen = curses.newwin(24, 80, 0, 0)
        full_screen.clear()
        full_screen.refresh()

    def hack_screen(self):
        self.clear_screen()
        curses.curs_set(2)
        word_dict = self.load_words(self.config.get("wordLength"))
        (pwd, w_list, full_str) = self.gen_string(self.config.get("wordsPrinted"), 408, word_dict)

        aux_str = [[" " * 32] for _ in range(self.rows_count)]
        x = 0
        y = 1
        my_delay = self.main_conf["delayTime"]

        hack_serv_win = curses.newwin(7, 80, 0, 0)
        hack_main_win = curses.newwin(18, 44, 7, 0)
        hack_cursor_win = curses.newwin(18, 3, 7, 44)
        hack_aux_win = curses.newwin(17, 33, 7, 47)
        hack_HL_win = curses.newwin(1, 33, 23, 47)
        hack_serv_win.clear()
        hack_serv_win.nodelay(True)
        hack_main_win.clear()
        hack_main_win.nodelay(True)

        tries_ast = "* " * self.config.get("attempts", 0)
        num_tries = self.config.get("attempts", 0)

        hack_header = self.config.get("hackHeader")
        if not hack_header:
            raise ValueError("missing hack_header")
        with open(os.path.join(self.main_conf["screen_path"], hack_header)) as fh:
            out_txt_str = fh.read()

        if self.out_header(out_txt_str.format(num_tries, tries_ast), hack_serv_win):
            return

        start_hex = random.randint(0x1A00, 0xFA00)
        col_str = 0
        while col_str < 2:
            y = 0
            while y < 17:
                x = 0
                hex_out = "{0:#4X}  ".format(start_hex + y * 12 + col_str * 204)
                for ch in hex_out:
                    key = hack_main_win.getch()
                    if (key == curses.KEY_ENTER or key == ord(" ")) and my_delay == self.main_conf["delayTime"]:
                        my_delay = self.main_conf["delayTime"] / 4
                    hack_main_win.addstr(y, (col_str * 24) + x, ch, curses.color_pair(1) | curses.A_BOLD)
                    time.sleep(my_delay / 1000)
                    hack_main_win.refresh()
                    x += 1
                    if self.check_status():
                        return
                i = 0
                for ch in full_str[(y + col_str * 17) * 12 : (y + col_str * 17) * 12 + 12]:
                    key = hack_main_win.getch()
                    if (key == curses.KEY_ENTER or key == ord(" ")) and my_delay == self.main_conf["delayTime"]:
                        my_delay = self.main_conf["delayTime"] / 4
                    hack_main_win.addstr(y, (col_str * 24) + x, ch, curses.color_pair(1) | curses.A_BOLD)
                    time.sleep(my_delay / 1000)
                    hack_main_win.refresh()
                    x += 1
                    i += 10
                    if self.check_status():
                        return
                y += 1
            col_str += 1
        hack_cursor_win.addstr(16, 1, ">", curses.color_pair(1) | curses.A_BOLD)
        hack_cursor_win.refresh()
        x = 8
        y = 0
        hack_main_win.move(y, x)
        hack_main_win.nodelay(False)
        hack_main_win.keypad(True)
        word_flag = False
        cheat_flag = False
        mss_time = int(time.monotonic_ns() / 1000000)
        while self.running:  # Основной цикл
            msc_time = int(time.monotonic_ns() / 1000000)
            if msc_time >= (mss_time + 3000):
                mss_time = msc_time
                # Читаем базу
                if self.check_status():
                    return
            f = False
            key = hack_main_win.getch()
            if key == curses.KEY_LEFT or key == 260 or key == ord("A") or key == ord("a"):
                f = True
                if x == 8:
                    x = 43
                elif x == 32:
                    x = 19
                else:
                    x -= 1
            if key == curses.KEY_RIGHT or key == 261 or key == ord("D") or key == ord("d"):
                f = True
                if x == 19:
                    x = 32
                elif x == 43:
                    x = 8
                else:
                    x += 1
            if key == curses.KEY_UP or key == 259 or key == ord("W") or key == ord("w"):
                f = True
                if y == 0:
                    y = 16
                else:
                    y -= 1
            if key == curses.KEY_DOWN or key == 258 or key == ord("S") or key == ord("s"):
                f = True
                if y == 16:
                    y = 0
                else:
                    y += 1

            if key == curses.KEY_ENTER or key == 10 or key == 13:  # Enter
                if word_flag:
                    d_word = self.compare_words(sel_group, pwd)
                    if d_word < self.config.get("wordLength"):
                        aux_str.pop(0)
                        aux_str.append(
                            sel_group + " [" + str(d_word) + " OF " + str(self.config.get("wordLength")) + "]"
                        )
                        y_aux = 0
                        for t_str in aux_str:
                            hack_aux_win.addstr(y_aux, 0, t_str + "\n", curses.color_pair(1) | curses.A_BOLD)
                            y_aux += 1
                        hack_aux_win.refresh()
                        num_tries -= 1
                        if num_tries > 0:
                            tries_ast = "* " * num_tries
                            y_s = 1
                            x_s = 0
                            hack_serv_win.clear()
                            for ch in out_txt_str.format(num_tries, tries_ast):
                                if ch == "\n":
                                    y_s += 1
                                    x_s = 0
                                    continue
                                hack_serv_win.addstr(y_s, x_s, ch, curses.color_pair(1) | curses.A_BOLD)
                                x_s += 1
                            hack_serv_win.refresh()
                            hack_main_win.move(y, x)
                        else:  # Блокировка
                            self.state_update('{"isLocked":True}')
                            time.sleep(1)
                            return
                    else:  # Терминал успешно взломан
                        self.state_update('{"isHacked":True}')
                        hack_main_win.clear()
                        hack_main_win.refresh()
                        return
                elif cheat_flag:  # Был найден чит
                    full_str = self.del_from_str(full_str, start_pos + 1, end_pos + 1)
                    (x_s_c, y_s_c) = self.get_str_coords(start_pos + 1)
                    i = 0
                    hack_main_win.addstr(y_s_c, x_s_c - 1, full_str[start_pos], curses.color_pair(1) | curses.A_BOLD)
                    while i < len(sel_group) - 1:
                        hack_main_win.addstr(y_s_c, x_s_c + i, ".", curses.color_pair(1) | curses.A_BOLD)
                        i += 1
                    r = random.randint(1, 10)
                    if r > 1:  # 9 из 10 случаев - удаляем слово
                        (d_pos, w_list, full_str) = self.del_random_word(w_list, full_str)
                        i = d_pos
                        while i < d_pos + self.config.get("wordLength"):
                            (dl_x, dl_y) = self.get_str_coords(i)
                            hack_main_win.addstr(dl_y, dl_x, ".", curses.color_pair(1) | curses.A_BOLD)
                            i += 1
                        aux_str.pop(0)
                        aux_str.append("DUMMY REMOVED")
                        y_aux = 0
                        for t_str in aux_str:
                            hack_aux_win.addstr(y_aux, 0, t_str + "\n", curses.color_pair(1) | curses.A_BOLD)
                            y_aux += 1
                        hack_aux_win.refresh()
                        hack_main_win.move(y, x)
                    else:
                        num_tries = self.config.get("attempts")
                        tries_ast = "* " * num_tries
                        y_s = 1
                        x_s = 0
                        hack_serv_win.clear()
                        for ch in out_txt_str.format(num_tries, tries_ast):
                            if ch == "\n":
                                y_s += 1
                                x_s = 0
                                continue
                            hack_serv_win.addstr(y_s, x_s, ch, curses.color_pair(1) | curses.A_BOLD)
                            x_s += 1
                        hack_serv_win.refresh()
                        aux_str.pop(0)
                        aux_str.append("ATTEMPTS RESTORED")
                        y_aux = 0
                        for t_str in aux_str:
                            hack_aux_win.addstr(y_aux, 0, t_str + "\n", curses.color_pair(1) | curses.A_BOLD)
                            y_aux += 1
                        hack_aux_win.refresh()
                    cheat_flag = False
                    hack_main_win.move(y, x)
            if f:
                if word_flag or cheat_flag:
                    i = start_pos
                    xHL = 0
                    while i <= end_pos:
                        (hlX, hlY) = self.get_str_coords(i)
                        hack_main_win.addstr(hlY, hlX, full_str[i], curses.color_pair(1) | curses.A_BOLD)
                        hack_HL_win.addstr(0, xHL, " ", curses.color_pair(1) | curses.A_BOLD)
                        i += 1
                        xHL += 1
                    cheat_flag = False
                    word_flag = False
                    hack_main_win.refresh()
                    hack_HL_win.refresh()
                str_pos = self.get_str_pos(x, y)
                (sel_w_group, start_w_pos, end_w_pos) = self.check_word_position(str_pos, full_str)
                (sel_c_group, start_c_pos, end_c_pos) = self.check_cheat_position(str_pos, full_str)
                if start_w_pos >= 0:
                    word_flag = True
                    cheat_flag = False
                    start_pos = start_w_pos
                    end_pos = end_w_pos
                    sel_group = sel_w_group
                if start_c_pos >= 0:
                    cheat_flag = True
                    word_flag = False
                    start_pos = start_c_pos
                    end_pos = end_c_pos + 1
                    sel_group = sel_c_group
                if word_flag or cheat_flag:
                    i = start_pos
                    while i <= end_pos:
                        (hl_x, hl_y) = self.get_str_coords(i)
                        hack_main_win.addstr(hl_y, hl_x, full_str[i], curses.color_pair(1) | curses.A_REVERSE)
                        i += 1
                    hack_HL_win.addstr(0, 0, sel_group, curses.color_pair(1) | curses.A_BOLD)
                    hack_main_win.refresh()
                    hack_HL_win.refresh()
                hack_main_win.move(y, x)

    def read_screen(self, file_name: str):
        curses.curs_set(2)
        read_serv_win = curses.newwin(4, 80, 0, 0)
        read_serv_win.clear()
        read_serv_win.nodelay(True)
        main_header = self.config.get("mainHeader")
        if not main_header:
            raise ValueError("main_header not defined")
        with open(os.path.join(self.main_conf["screen_path"], main_header)) as fh:
            out_txt_str = fh.read()
        if self.out_header(out_txt_str, read_serv_win):
            return

        if platform == "linux" or platform == "linux2":
            with open(file_name) as fh:
                out_txt_str = fh.read()
        else:
            with open(file_name) as fh:
                out_txt_str = fh.read()

        out_txt_list = out_txt_str.split("\n")
        read_text_pad = curses.newpad(int(len(out_txt_list) / 20 + 1) * 20, 80)

        for _str in out_txt_list:
            read_text_pad.addstr(_str + "\n", curses.color_pair(1) | curses.A_BOLD)

        read_text_pad.refresh(0, 0, 4, 0, 23, 78)
        curses.curs_set(0)
        read_serv_win.nodelay(False)
        read_serv_win.keypad(True)
        row_pos = 0
        mss_time = int(time.monotonic_ns() / 1000000)
        while self.running:
            msc_time = int(time.monotonic_ns() / 1000000)
            if msc_time >= (mss_time + 3000):
                mss_time = msc_time
                # Читаем базу
                if self.check_status():
                    return
            f = False
            read_serv_win.move(0, 0)
            key = read_serv_win.getch()
            if key == curses.KEY_NPAGE or key == 338 or key == ord("S") or key == ord("s"):
                if row_pos < int(len(out_txt_list) / 20) * 20:
                    row_pos += 20
                    f = True
            if key == curses.KEY_PPAGE or key == 339 or key == ord("W") or key == ord("w"):
                if row_pos > 0:
                    row_pos -= 20
                    f = True
            if key == curses.KEY_BACKSPACE or key == 27:
                read_serv_win.clear()
                read_serv_win.refresh()
                self.menu_screen()
            if f:
                read_text_pad.refresh(row_pos, 0, 4, 0, 23, 78)
                f = False

    def menu_screen(self):
        curses.curs_set(2)
        menu_sel = []
        menu_full_win = curses.newwin(25, 80, 0, 0)
        menu_serv_win = curses.newwin(4, 80, 0, 0)
        menu_main_win = curses.newwin(21, 80, 4, 0)
        menu_main_win.clear()
        menu_main_win.refresh()
        x = 0
        y = 0
        menu_header = self.config.get("menuHeader")
        if not menu_header:
            raise ValueError("menu_header not defined")
        with open(os.path.join(self.main_conf["screen_path"], menu_header)) as fh:
            out_txt_str = fh.read()

        if self.out_header(out_txt_str, menu_serv_win):
            return
        max_len = 0
        rows = 0
        for menu_item in self.config.get("textMenu").keys():
            if max_len < len(menu_item):
                max_len = len(menu_item)
            rows += 1
        y = int((21 - rows * 2) / 2)
        x = int((80 - max_len) / 2)
        for menu_item in self.config.get("textMenu").keys():
            menu_main_win.addstr(y, x, menu_item, curses.color_pair(1) | curses.A_BOLD)
            menu_sel.append(menu_item)
            y += 2
        menu_pos = 0
        y = int((21 - rows * 2) / 2)
        menu_main_win.addstr(y, x, menu_sel[0], curses.color_pair(1) | curses.A_REVERSE)
        menu_main_win.refresh()
        menu_main_win.keypad(True)
        curses.curs_set(0)
        while self.running:
            f = False
            key = menu_main_win.getch()
            if key == curses.KEY_UP or key == 259 or key == ord("W") or key == ord("w"):
                menu_main_win.addstr(y, x, menu_sel[menu_pos], curses.color_pair(1) | curses.A_BOLD)
                f = True
                if menu_pos == 0:
                    menu_pos = len(menu_sel) - 1
                else:
                    menu_pos -= 1
            if key == curses.KEY_DOWN or key == 258 or key == ord("S") or key == ord("s"):
                menu_main_win.addstr(y, x, menu_sel[menu_pos], curses.color_pair(1) | curses.A_BOLD)
                f = True
                if menu_pos == len(menu_sel) - 1:
                    menu_pos = 0
                else:
                    menu_pos += 1
            if key == curses.KEY_ENTER or key == 10 or key == 13:  # Enter
                # Выбор позиции
                if self.config.get("textMenu")[menu_sel[menu_pos]]["type"] == "text":
                    menu_main_win.clear()
                    menu_serv_win.clear()
                    menu_main_win.refresh()
                    menu_serv_win.refresh()
                    menu = self.config.get("textMenu", {})[menu_sel[menu_pos]]["name"]
                    self.read_screen(str(os.path.join(self.main_conf["text_path"], menu)))
                elif self.config.get("textMenu")[menu_sel[menu_pos]]["type"] == "command":
                    os.system(self.config.get("textMenu")[menu_sel[menu_pos]]["name"])
                    menu_full_win.clear()
                    menu_main_win.refresh()
                    menu_serv_win.refresh()
            if f:
                y = int((21 - rows * 2) / 2) + 2 * menu_pos
                menu_main_win.addstr(y, x, menu_sel[menu_pos], curses.color_pair(1) | curses.A_REVERSE)
                menu_main_win.refresh()
                f = False

    def start_terminal(self):
        """
        Основной игровой цикл.
        Предыдущее состояние терминала. Если не совпадает с текущим - будет выполнена очистка и перерисовка экрана.
        Unpowered - нет питания.
        Locked - заблокирован.
        Hacked - взломан.
        Normal - запитан, ждет взлома.
        Broken - сломан.
        """
        self.init_curses()
        while self.running:
            self.main_conf["db_updated"] = False
            if self.main_conf["forceClose"]:
                break
            while self.main_conf["is_db_updating"]:  # Ожидаем, пока обновится состояние из БД.
                pass
            lock_timeout_start = self.main_conf.get("lockTimeOutStart", 0)
            if lock_timeout_start != 0:
                if int(time.monotonic_ns() / 1000000 - lock_timeout_start) >= self.config.get("lockTimeOut", 0) * 1000:
                    self.main_conf["lockTimeOutStart"] = 0
                    self.state_update('{"isLocked":False}')
            if not self.config.get("isPowerOn"):
                if self.main_conf["previousState"] != "Unpowered":
                    self.main_conf["previousState"] = "Unpowered"
                    self.out_screen("unPowerHeader", 0)
                    time.sleep(self.main_conf["dbCheckInterval"])
            elif self.config.get("isLocked"):
                if self.main_conf["previousState"] != "Locked":
                    self.main_conf["lockTimeOutStart"] = int(time.monotonic_ns() / 1000000)
                    self.main_conf["previousState"] = "Locked"
                    self.out_screen("lockHeader", 0)
            elif self.config.get("isHacked"):
                if self.main_conf["previousState"] != "Hacked":
                    self.main_conf["previousState"] = "Hacked"
                    self.menu_screen()  # Здесь вызываем функцию после взлома
                    # main_conf['forceClose'] = True   # Закрываем всё
            else:
                # Взлом.
                self.main_conf["previousState"] = "Normal"
                self.out_screen("startHeader", 3)
                self.hack_screen()
