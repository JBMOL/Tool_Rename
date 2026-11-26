"""
rename_tool.constants

Constants for the Rename Tool.
"""
from __future__ import annotations

# Quick prefix buttons
PREFIXES = ['l_', 'c_', 'r_', 'L_', 'C_', 'R_']

# Extra suffixes shown in the "More..." window
EXTRA_SUFFIXES = [
    '_low', '_mid', '_rig', '_temp',
    '_proxy', '_high', '_mesh', '_delete',
    '_LOD0', '_LOD1', '_LOD2', '_grp',
    '_lod0', '_lod1', '_lod2', '_GRP'
]

# Suffixes to detect (sorted by length, longest-first)
SUFFIXES = sorted(
    set([
        '_ctrl', '_CTRL', '_jnt', '_JNT', '_geo', '_GEO',
        '_null', '_NULL', '_loc', '_LOC', '_old', '_OLD'
    ] + EXTRA_SUFFIXES),
    key=len,
    reverse=True
)

TOOL_VERSION = "V3.8"
TOOL_DATE = "26/11/2026"
