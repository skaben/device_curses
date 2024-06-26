import curses
import os
import random
import time

from skabenclient.device import BaseDevice

from config import BoilerplateConfig


class BoilerplateDevice(BaseDevice):
    """Test device should be able to generate all kind of messages

    state_reload -> загрузить текущий конфиг из файла
    state_update(data) -> записать конфиг в файл (и послать на сервер)
    send_message(data) -> отправить сообщение от имени девайса во внутреннюю очередь
    """

    config_class = BoilerplateConfig

    _screen_path = os.path.join(os.getcwd(), "resources", "screens")
    _text_path = os.path.join(os.getcwd(), "resources", "texts")
    _words_path = os.path.join(os.getcwd(), "resources", "words")

    def __init__(self, system_config, device_config, **kwargs):
        super().__init__(system_config, device_config)
        self.running = None

    def run(self):
        """Main device run routine

        в супере он создает сообщение во внутренней очереди что девайс запущен.
        """
        super().run()
        self.running = True
        while self.running:
            # main routine
            time.sleep(100)

    def init_curses(self):
        """Initialize curses."""
        curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.noecho()
        curses.raw()
        curses.curs_set(2)

    def out_screen(self, param_name: str, delay_after: int = 2) -> bool:
        """Output screen text to curses window."""
        curses.curs_set(2)
        full_screen_win = curses.newwin(24, 80, 0, 0)
        full_screen_win.clear()
        full_screen_win.refresh()
        full_screen_win.nodelay(True)
        param = self.config.get(param_name)
        with open(self._screen_path + param, "r", encoding="utf-8") as fh:
            out_txt_str = fh.read()
        status = self.out_header(out_txt_str, full_screen_win)
        if delay_after > 0:
            time.sleep(delay_after)
        return status

    def out_header(self, out_text: str, window: curses.window) -> bool:
        """Output header text to curses window."""
        window.clear()
        window.refresh()
        window.nodelay(True)
        delay_time = self.system.get("delay_time")
        for ch in out_text:
            key = window.getch()
            if (key == curses.KEY_ENTER or key == ord(" ")) and int(round(my_delay, 0)) == delay_time:
                my_delay = int(round(delay_time / 4, 0))
            window.addstr(ch, curses.color_pair(1) | curses.A_BOLD)
            time.sleep(my_delay / 1000)
            window.refresh()
            # todo: rewrite to successfull get of device config?
            # if checkStatus():
            #    return True
        return False

    def clear_screen(self):
        """Clear curses screen."""
        window = curses.newwin(24, 80, 0, 0)
        window.clear()
        window.refresh()

    @staticmethod
    def get_row_position(x: int, y: int) -> int:
        """Get string position from x and y coordinates."""
        y_new = y + 17 if x >= 32 else y
        x_new = x - 32 if x >= 32 else x - 8
        return y_new * 12 + x_new

    @staticmethod
    def get_row_coords(str_pos: int) -> tuple[int, int]:
        """Get x and y coordinates from string position."""
        y = int(str_pos / 12) - 17 if str_pos >= 204 else int(str_pos / 12)
        x = str_pos % 12 + 32 if str_pos >= 204 else str_pos % 12 + 8
        return x, y

    @staticmethod
    def check_word_position(char_index, word_str):
        """Check if word is selected and return selected word and its start and end positions."""
        start_pos = word_str.rfind(" ", 0, char_index) + 1
        end_pos = word_str.find(" ", char_index)
        if end_pos == -1:
            end_pos = len(word_str)
        selected_word = word_str[start_pos:end_pos]
        return selected_word, start_pos, end_pos - 1

    @staticmethod
    def check_cheat_position(char_index: int, word_str: str) -> tuple[str, int, int]:
        """Check if cheat is possible and return selected word and its start and end positions."""
        brackets = {"[": "]", "(": ")", "{": "}", "<": ">"}
        bracket = word_str[char_index]
        if bracket not in brackets and bracket not in brackets.values():
            return "", -1, -1

        direction = 1 if bracket in brackets else -1
        control_char = brackets[bracket] if direction == 1 else {v: k for k, v in brackets.items()}[bracket]
        start_pos, end_pos = char_index, char_index - 1 if direction == -1 else -1

        for i in range(char_index + direction, len(word_str) if direction == 1 else -1, direction):
            if word_str[i].isalpha() or i % 12 == 0:
                return "", -1, -1
            if word_str[i] == control_char:
                end_pos = i - 1 if direction == -1 else i
                break

        return word_str[start_pos : end_pos + 2], start_pos, end_pos

    @staticmethod
    def del_from_str(all_str: str, start_pos: int, end_pos: int) -> str:
        """Delete characters from start_pos to end_pos in all_str."""
        return all_str[:start_pos] + "." * (end_pos - start_pos + 1) + all_str[end_pos + 1 :]

    @staticmethod
    def compare_words(first_word: str, second_word: str) -> int:
        """Compare two words and return number of equal characters."""
        return sum(a == b for a, b in zip(first_word, second_word))

    @staticmethod
    def delete_random_word(word_list: list[str], text_field: str) -> tuple[int, list[str], str]:
        """Delete random word from list and return start position of this word."""
        word = random.choice(word_list)
        start_pos = text_field.index(word)
        word_list.remove(word)
        all_str = text_field.replace(word, "." * len(word))
        return start_pos, word_list, text_field
