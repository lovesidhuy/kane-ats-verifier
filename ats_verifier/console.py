"""Terminal colors without escape sequences in pipes, logs, or NO_COLOR output."""
from __future__ import annotations
import builtins
import os
import re
import sys

ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")

def print(*values, **kwargs):
    stream = kwargs.get("file") or sys.stdout
    if not getattr(stream, "isatty", lambda: False)() or "NO_COLOR" in os.environ:
        values = tuple(ANSI.sub("", str(value)) for value in values)
    kwargs.setdefault("flush", True)
    builtins.print(*values, **kwargs)
