from skabenclient.config import DeviceConfigExtended

ESSENTIAL = {
    "is_power_on": False,
    "is_locked": False,
    "is_hacked": False,
    "lock_timeout": 30,
    "word_length": 8,
    "words_printed": 16,
    "attempts": 4,
    "start_header": "startScreen.txt",
    "hack_header": "hackScreen.txt",
    "unpower_header": "powerScreen.txt",
    "lock_header": "lockScreen.txt",
    "main_header": "readScreen.txt",
    "menu_header": "menuScreen.txt",
    "text_menu": {
        "����� ������� �� ������!": {"type": "text", "name": "f3Doc.txt"},
    },
}


class CursesConfig(DeviceConfigExtended):
    def __init__(self, config):
        self.minimal_essential_conf = ESSENTIAL
        super().__init__(config)
