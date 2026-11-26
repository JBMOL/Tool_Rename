"""
rename_tool.launcher

Safe entrypoint for the Rename Tool.
"""
from __future__ import annotations

from .ui import RenameToolUI


def launch():
    """Launch the Rename Tool UI."""
    RenameToolUI()
