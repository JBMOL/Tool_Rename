"""
rename_tool.utils

Small, reusable helpers for parsing/validating names.
"""
from __future__ import annotations

import re
from .constants import PREFIXES, SUFFIXES


def extract_suffixes(name: str, count: int = 2):
    """
    Extract up to `count` suffix blocks from the end of `name`.

    Returns:
        rest (str): name without extracted suffix blocks
        suffixes_found (list[str]): extracted suffix blocks, in display order
    """
    suffixes_found = []
    rest = name
    for _ in range(count):
        for s in SUFFIXES:
            pattern = re.escape(s) + r'(\d*)$'
            m = re.search(pattern, rest)
            if m:
                suffixes_found.insert(0, m.group(0))
                rest = rest[:m.start()]
                break
        else:
            break
    return rest, suffixes_found


def is_valid_name(name: str) -> bool:
    invalid_chars = set(' :;,/\\|\"\'"[]{}()*&^%$#@!~?<>=' + "\t\n")
    return not any(c in invalid_chars for c in name)


def strip_prefix(name: str, name_first: bool) -> str:
    """
    Remove the side prefix, depending on the chosen naming order.
    - Standard:  l_foo_bar  -> foo_bar
    - Name-first: foo_l_bar -> foo_bar   (treats _l/_r/_c as "prefix block")
    """
    core_rest, suffixes = extract_suffixes(name, 2)

    if name_first:
        for p in PREFIXES:
            inv = '_' + p.strip('_')  # 'C_' -> '_C'
            if core_rest.endswith(inv):
                new_core = core_rest[:-len(inv)]
                return new_core + ''.join(suffixes)
        return name
    else:
        for p in PREFIXES:
            if name.startswith(p):
                return name[len(p):]
        return name


def build_name(
    base: str,
    index: int | None,
    prefix: str,
    suffix: str,
    suffix2: str,
    name_first: bool
) -> str:
    """
    Compose a final name given parts and naming order.
    """
    name_core = base
    if index is not None:
        name_core += f"{index:02d}"

    if prefix:
        if name_first:
            prefix = '_' + prefix.strip('_')
        else:
            prefix = prefix.strip('_') + '_'
    else:
        prefix = ""

    if suffix and not suffix.startswith('_'):
        suffix = '_' + suffix
    if suffix2 and not suffix2.startswith('_'):
        suffix2 = '_' + suffix2

    if name_first:
        return f"{name_core}{prefix}{suffix}{suffix2}"
    else:
        return f"{prefix}{name_core}{suffix}{suffix2}"
