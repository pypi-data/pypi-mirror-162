"""
```termapp.stream``` provides types and functions to represent streams as well
as getting default streams.
"""

import sys
import typing


class OutputStream(typing.Protocol):
    """
    OutputStream defines the protocol for types that can be used to output a
    colored UI for a command line application.

    Types, such as ``sys.TextIO`` are conformant to this protocol, so 
    ``sys.stdout`` is safe to use.
    """

    def flush(self) -> None: ...
    def isatty(self) -> bool: ...
    def write(self, s: typing.AnyStr) -> int: ...


def default_output_stream(out: typing.Optional[OutputStream] = None) -> OutputStream:
    """
    Either returns ``out`` or ``sys.stdout`` but with a "lazy" resolving. That
    means, that `sys.stdout`` will not be resolved during import time but
    during runtime of each invocation. This allows reassigning of 
    ``sys.stdout`` to take effect on later calls.
    """
    return out or sys.stdout
