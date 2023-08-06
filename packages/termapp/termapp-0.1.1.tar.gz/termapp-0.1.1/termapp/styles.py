"""
This modules provides base definitions and functions to render styled output on
compatible devides.
"""


_START_MARKER = '\033['
_END_MARKER = 'm'
_SEPARATOR = ';'

DISABLE_CURSOR = '\033[?25l'
ENABLE_CURSOR = '\033[?25h'

RESET = '0'

BOLD = '1'

DEFAULT = '22'

FG_BLACK = '30'
FG_RED = '31'
FG_GREEN = '32'
FG_YELLOW = '33'
FG_BLUE = '34'
FG_MAGENTA = '35'
FG_CYAN = '36'
FG_WHITE = '37'

BG_BLACK = '40'
BG_RED = '41'
BG_GREEN = '42'
BG_YELLOW = '43'
BG_BLUE = '44'
BG_MAGENTA = '45'
BG_CYAN = '46'
BG_WHITE = '47'


def apply_styles(s: str, *styles: str) -> str:
    """
    applies the given ``styles`` to ``s`` and returns the resulting string.
    """
    return activate_styles(*styles) + s + activate_styles(RESET)


def activate_styles(*styles: str) -> str:
    """
    Activates the given styles by assembling an escape sequence to start the
    given styles.
    """
    return _START_MARKER + _SEPARATOR.join(styles) + _END_MARKER
