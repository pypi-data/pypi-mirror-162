"""
``terminalui.async`` provides types and functions to create terminal
based user-interfaces in async applications.
"""

import asyncio
import os
import typing
from contextlib import asynccontextmanager
from functools import partial

from termapp._symbols import RUNNING_INDICATOR_MOVING_DOTS, PROGRESS_BAR_CHARS
from termapp.styles import (BG_RED, DEFAULT, DISABLE_CURSOR, ENABLE_CURSOR,
                            FG_CYAN, FG_GREEN, FG_RED, FG_YELLOW, RESET,
                            activate_styles)
from termapp.stream import OutputStream, default_output_stream


class AsyncOutputStream:
    """
    A wrapper for an ``OutputStream`` that runs all operations asynchroniuously
    in the default executor.
    """

    def __init__(self, out: OutputStream):
        self._out = out

    async def flush(self):
        """
        flushes the output stream forcing any unwritten output to the
        underlying sink.
        """
        return await asyncio.get_event_loop()\
            .run_in_executor(None, self._out.flush)

    async def isatty(self) -> bool:
        """
        returns whether the underlying sink is a tty supporting styled output.
        """
        return await asyncio.get_event_loop()\
            .run_in_executor(None, self._out.isatty)

    async def write(self, s: typing.AnyStr) -> int:
        """
        Writes the given string-like ``s`` to the underlying sink and returns
        the number of bytes written.
        """
        return await asyncio.get_event_loop()\
            .run_in_executor(None, partial(self._out.write, s))


class AppProtocol (typing.Protocol):
    """
    ``AppProtocol`` defines a protocol for async applications. This protocol
    defines the methods that should be implemented by classes providing async
    apps. This modules defines two such classes for styled and unstyled output.
    This protocol defines the base line of functionality.
    """
    async def start_progress(
        self, show_completion: bool = False, message: str = None): ...

    async def stop_progress(self): ...

    async def update_progress(
        self,
        completion: typing.Optional[float] = None,
        message: typing.Optional[str] = None): ...

    async def details(self, s: str): ...

    async def info(self, s: str): ...

    async def warn(self, s: str): ...

    async def danger(self, s): ...

    async def success(self, s): ...

    async def failure(self, s): ...

    async def write(self, s: typing.AnyStr): ...

    async def write_line(self, line=''): ...


class StyledApp(AppProtocol):
    """
    ``StyledApplication`` implements an application class compatible with the
    application protocol defined above. This application outputs styled 
    messages and animated progress indicators for tty compatible streams.
    """

    def __init__(self,
                 out: OutputStream = None,
                 terminal_width: typing.Optional[int] = None,
                 refresh_interval: float = 0.2,
                 running_indicator_chars: str = RUNNING_INDICATOR_MOVING_DOTS,
                 progress_bar_chars: str = PROGRESS_BAR_CHARS,
                 details_prefix: str = '\u2026 ',
                 details_styles: typing.Iterable[str] = (DEFAULT,),
                 info_prefix: str = '',
                 info_styles: typing.Iterable[str] = (FG_CYAN,),
                 warn_prefix: str = '\u26A0 ',
                 warn_styles: typing.Iterable[str] = (FG_YELLOW,),
                 danger_prefix: str = '\u26A0 ',
                 danger_styles: typing.Iterable[str] = (BG_RED,),
                 success_prefix: str = '\u2713 ',
                 success_styles: typing.Iterable[str] = (FG_GREEN,),
                 failure_prefix: str = '\u2716 ',
                 failure_styles: typing.Iterable[str] = (FG_RED,),
                 ):
        self._out = AsyncOutputStream(default_output_stream(out))
        self._details_prefix = details_prefix
        self._details_styles = tuple(details_styles)
        self._info_prefix = info_prefix
        self._info_styles = tuple(info_styles)
        self._warn_prefix = warn_prefix
        self._warn_styles = tuple(warn_styles)
        self._danger_prefix = danger_prefix
        self._danger_styles = tuple(danger_styles)
        self._success_prefix = success_prefix
        self._success_styles = tuple(success_styles)
        self._failure_prefix = failure_prefix
        self._failure_styles = tuple(failure_styles)

        self._terminal_width = terminal_width or os.get_terminal_size()[0]

        self._refresh_interval = refresh_interval

        self._running_indicator_chars = running_indicator_chars
        self._progress_bar_chars = progress_bar_chars
        if len(self._progress_bar_chars) != 2:
            raise ValueError(
                f"progress_bar_chars must be a string of length 2")

        self._lock = asyncio.Lock()
        self._completion = 0.0
        self._progress_message = ''
        self._show_completion = False
        self._running = False
        self._stop_requested = False
        self._indicator_char_index = 0

        self._progress_task = None

    async def start_progress(self, show_completion: bool = False, message: str = ''):
        async with self._lock:
            if self._running:
                return
            self._stop_requested = False
            self._running = True
            self._indicator_char_index = 0
            self._show_completion = show_completion
            self._completion = 0.0
            self._progress_message = message
            await self._out.write(DISABLE_CURSOR)

        self._progress_task = asyncio.create_task(self._run_progress_loop())

    async def _run_progress_loop(self):
        while True:
            async with self._lock:
                if self._stop_requested:
                    self._running = False
                    self._stop_requested = False
                    await self._clear_progress_view()
                    await self._out.write(ENABLE_CURSOR)
                    return

                await self._draw_progress_view()

                self._indicator_char_index = (
                    self._indicator_char_index + 1) % len(self._running_indicator_chars)

            await asyncio.sleep(self._refresh_interval)

    async def stop_progress(self):
        async with self._lock:
            self._stop_requested = True
        await self._progress_task

    async def update_progress(self, completion: typing.Optional[float] = None,
                              message: typing.Optional[str] = None):
        if completion is not None:
            completion = float(completion)
            if completion < 0 or completion > 1:
                raise ValueError(
                    f'Invalid completion: {completion:f} is not between 0.0 and 1.0')

        async with self._lock:
            self._completion = completion if completion is not None else self._completion
            self._progress_message = message if message is not None else self._progress_message

    async def _clear_progress_view(self):
        await self._out.write('\b' * self._terminal_width)
        await self._out.write(' ' * self._terminal_width)
        await self._out.write('\b' * self._terminal_width)

    async def _draw_progress_view(self):
        await self._clear_progress_view()
        async with self.apply_styles(*self._info_styles):
            await self._out.write(
                f" {self._running_indicator_chars[self._indicator_char_index]} ")

        width = self._terminal_width - 2
        progress_bar_width = 0
        message_width = width

        if self._show_completion:
            progress_bar_width = int(0.6 * width)
            message_width = width - progress_bar_width - 1

            completed = int(progress_bar_width * self._completion)
            uncompleted = progress_bar_width - completed
            await self._out.write(self._progress_bar_chars[0] * completed)
            await self._out.write(self._progress_bar_chars[1] * uncompleted)
            await self._out.write(' ')

        message = self._progress_message
        if len(self._progress_message) > message_width:
            message = message[:message_width - 1] + '\u2026'

        await self._out.write(message)

        await self._out.flush()

    async def details(self, s: str):
        async with self.apply_styles(*self._details_styles):
            await self.write_line(self._details_prefix + s)

    async def info(self, s: str):
        async with self.apply_styles(*self._info_styles):
            await self.write_line(self._info_prefix + s)

    async def warn(self, s: str):
        async with self.apply_styles(*self._warn_styles):
            await self.write_line(self._warn_prefix + s)

    async def danger(self, s):
        async with self.apply_styles(*self._danger_styles):
            await self.write_line(self._danger_prefix + s)

    async def success(self, s):
        async with self.apply_styles(*self._success_styles):
            await self.write_line(self._success_prefix + s)

    async def failure(self, s):
        async with self.apply_styles(*self._failure_styles):
            await self.write_line(self._failure_prefix + s)

    async def write(self, s: typing.AnyStr):
        async with self._lock:
            if self._running:
                await self._clear_progress_view()
            await self._out.write(s)
            if self._running and not s.endswith('\n'):
                await self._out.write('\n')

    async def write_line(self, line=''):
        await self.write(line + '\n')

    @asynccontextmanager
    async def no_cursor(self):
        await self._out.write(DISABLE_CURSOR)
        yield self
        await self._out.write(ENABLE_CURSOR)

    @asynccontextmanager
    async def apply_styles(self, *styles: str):
        await self._out.write(activate_styles(*styles))
        yield self
        await self._out.write(activate_styles(RESET))


class UnstyledApp(AppProtocol):
    def __init__(self,
                 out: OutputStream = None,
                 details_prefix: str = '\u2026 ',
                 info_prefix: str = '',
                 warn_prefix: str = '\u26A0 ',
                 danger_prefix: str = '\u26A0 ',
                 success_prefix: str = '\u2713 ',
                 failure_prefix: str = '\u2716 ',
                 ):
        self._out = AsyncOutputStream(default_output_stream(out))
        self._details_prefix = details_prefix
        self._info_prefix = info_prefix
        self._warn_prefix = warn_prefix
        self._danger_prefix = danger_prefix
        self._success_prefix = success_prefix
        self._failure_prefix = failure_prefix

    async def start_progress(self, show_completion: bool = False, message: str = None):
        pass

    async def stop_progress(self):
        pass

    async def update_progress(self, completion: typing.Optional[float] = None,
                              message: typing.Optional[str] = None):
        pass

    async def details(self, s: str):
        await self.write_line(self._details_prefix + s)

    async def info(self, s: str):
        await self.write_line(self._info_prefix + s)

    async def warn(self, s: str):
        await self.write_line(self._warn_prefix + s)

    async def danger(self, s):
        await self.write_line(self._danger_prefix + s)

    async def success(self, s):
        await self.write_line(self._success_prefix + s)

    async def failure(self, s):
        await self.write_line(self._failure_prefix + s)

    async def write(self, s: typing.AnyStr):
        await self._out.write(s)
        await self._out.flush()

    async def write_line(self, line=''):
        await self.write(line + '\n')


def create_app(out: typing.Optional[OutputStream] = None, **kwargs) -> AppProtocol:
    out = default_output_stream(out)
    if out.isatty():
        return StyledApp(**kwargs)
    return UnstyledApp(**kwargs)
