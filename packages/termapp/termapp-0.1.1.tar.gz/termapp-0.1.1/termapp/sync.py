from contextlib import contextmanager

from termapp.styles import DISABLE_CURSOR, ENABLE_CURSOR, RESET, activate_styles
from termapp.stream import OutputStream, default_output_stream


@contextmanager
def apply_styles(*styles: str, out: OutputStream = None):
    out = default_output_stream(out)

    out.write(activate_styles(*styles))
    out.flush()

    yield out

    out.write(activate_styles(RESET))
    out.flush()


def disable_cursor(out: OutputStream = None):
    out = default_output_stream(out)
    out.write(DISABLE_CURSOR)


def enable_cursor(out: OutputStream = None):
    out = default_output_stream(out)
    out.write(ENABLE_CURSOR)
