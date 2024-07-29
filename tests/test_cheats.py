import pytest

from f3termCurses import checkCheatPosition


def test_check_cheat_position_with_left_parenthesis():
    assert checkCheatPosition(0, "(cheat)") == ("(cheat)", 0, 6)


def test_check_cheat_position_with_right_parenthesis():
    assert checkCheatPosition(6, "(cheat)") == ("(cheat)", 0, 6)


def test_check_cheat_position_with_no_parenthesis():
    assert checkCheatPosition(3, "cheat") == ("", -1, -1)


def test_check_cheat_position_with_alpha_inside_parenthesis():
    assert checkCheatPosition(0, "(c)heat") == ("", -1, -1)


def test_check_cheat_position_with_exceeding_index():
    assert checkCheatPosition(7, "(cheat)") == ("", -1, -1)


def test_check_cheat_position_with_negative_index():
    assert checkCheatPosition(-1, "(cheat)") == ("", -1, -1)


def test_check_cheat_position_with_empty_string():
    assert checkCheatPosition(0, "") == ("", -1, -1)
