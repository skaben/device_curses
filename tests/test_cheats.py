import pytest

from f3termCurses import checkCheatPosition


@pytest.mark.parametrize(
    "row, pos, expected",
    [
        ("[#@_$!]##_!-", 0, ("[#@_$!]", 0, 6)),
        ("<#@_$!>##_!-", 0, ("<#@_$!>", 0, 6)),
        ("{#@_$!}##_!-", 0, ("{#@_$!}", 0, 6)),
        ("[#@_$!]##_!-", 6, ("[#@_$!]", 0, 6)),
        ("##_!-[#@_$!]", 0, ("", -1, -1)),
        ("##_!-{#@_$!}", 0, ("", -1, -1)),
        ("[{<#@_$!>}])", 0, ("[{<#@_$!>}]", 0, 10)),
        ("[{<#@_$!>}])", 1, ("[{<#@_$!>}]", 0, 9)),
        ("[{<#@_$!>}])", 11, ("", -1, -1)),
        ("#@_$!", 1, ("", -1, -1)),
        ("[word]", 0, ("", -1, -1)),
    ],
)
def test_cheat_parenthesis(row, pos, expected):
    assert checkCheatPosition(pos, row) == expected
