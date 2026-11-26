"""
Single-file Launcher for Rename Tool V3.5 (modular, cmds-only)

Usage (from Maya Script Editor / Shelf):
---------------------------------------
import importlib.util, sys
p = r"E:/00_Programas/AutodeskMaya/Maya2026/Tools/00_Tools/2026/Tool_Rename V2/RenameTool_Launcher.py"

spec = importlib.util.spec_from_file_location("RenameTool_Launcher", p)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
mod.launch()
---------------------------------------
"""

from __future__ import annotations

import os
import sys


def _ensure_package_on_syspath():
    """Add this file's directory to sys.path so 'rename_tool' can be imported."""
    tool_dir = os.path.dirname(os.path.abspath(__file__))
    if tool_dir not in sys.path:
        sys.path.insert(0, tool_dir)
    return tool_dir


def launch():
    """Launch the Rename Tool UI."""
    _ensure_package_on_syspath()

    # Import here so reload workflows are possible
    from rename_tool import launcher as pkg_launcher
    pkg_launcher.launch()


if __name__ == "__main__":
    launch()
