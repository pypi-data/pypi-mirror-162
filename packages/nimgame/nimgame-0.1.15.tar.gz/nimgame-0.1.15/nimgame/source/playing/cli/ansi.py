"""ANSI codes for manipulating console display

These functions are used for cleaning lines after an input is taken or an error
is displayed.
"""


# An empty command seems to make the Windows cmd terminal capable of ANSI.
import os; os.system('')


ESC = '\033'
CURSOR_UP = ESC + '[A'
CURSOR_BACK = ESC + '[200D'
DELETE_LINE = ESC + '[K'


def clean_this_line():
    """Clean the input prompt inline"""
    print(
        CURSOR_BACK + DELETE_LINE, 
        end='' #supress line feed
    )


def clean_prev_line():
    """Clean the input prompt and the answer"""
    print(
        CURSOR_UP + DELETE_LINE, 
        end='' #supress line feed
    )
