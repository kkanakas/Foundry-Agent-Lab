"""
_tee.py — Lightweight stdout/input logger.

Import this module to optionally tee all console output (and user input)
to a log file. Activated by the LOG_FILE environment variable.

Usage:
    Set LOG_FILE=path/to/output.txt before running, or pass --log to demo.bat.
    Then simply `import _tee` at the top of your script (after sys.path setup).
"""

import os
import sys
import builtins
from datetime import datetime

_log_file = os.environ.get("LOG_FILE")


class _Tee:
    """Write to both the original stream and a log file."""

    def __init__(self, stream, file_handle):
        self._stream = stream
        self._file = file_handle

    def write(self, data):
        self._stream.write(data)
        self._file.write(data)
        self._file.flush()

    def flush(self):
        self._stream.flush()
        self._file.flush()

    # Pass through any other attributes (encoding, isatty, etc.)
    def __getattr__(self, name):
        return getattr(self._stream, name)


if _log_file:
    _fh = open(_log_file, "a", encoding="utf-8")

    sys.stdout = _Tee(sys.__stdout__, _fh)
    # stderr is NOT tee'd — errors/warnings stay on the console only

    # Also capture user input so the log shows both sides of the conversation
    _original_input = builtins.input

    def _logged_input(prompt=""):
        # Write prompt to log explicitly — on Windows, input() writes the
        # prompt via WriteConsoleW, bypassing our _Tee.write() wrapper.
        if prompt:
            _fh.write(prompt)
            _fh.flush()
        result = _original_input(prompt)
        _fh.write(result + "\n")
        _fh.flush()
        return result

    builtins.input = _logged_input


def log_chat(sender: str, message: str):
    """Log a chat message for GUI/web demos where print()/input() aren't used.

    Call this from desktop (tkinter) and web (Gradio) chat functions to
    capture conversations to the log file. No-op when LOG_FILE is not set.
    """
    if not _log_file:
        return
    _fh.write(f"{sender}: {message}\n\n")
    _fh.flush()


def console_only(*args, **kwargs):
    """Print to the terminal only — never to the log file.

    Use for operational details (endpoints, IDs) that should not appear in
    the chat transcript.
    """
    sys.__stdout__.write(" ".join(str(a) for a in args) + kwargs.get("end", "\n"))
    sys.__stdout__.flush()
