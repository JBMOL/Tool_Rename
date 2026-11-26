"""
rename_tool.core

Core renaming operations (cmds-only).
No UI code here.
"""
from __future__ import annotations

from maya import cmds # type: ignore
from .constants import PREFIXES
from .utils import extract_suffixes, is_valid_name


def selected_transforms():
    return cmds.ls(sl=True, type="transform") or []


def short_name(node: str) -> str:
    return node.split("|")[-1]


def remove_any_start_prefix(name: str) -> str:
    for p in PREFIXES:
        if name.startswith(p):
            return name[len(p):]
    return name


def remove_any_end_prefix_block(core_rest: str) -> str:
    for p in PREFIXES:
        inv = '_' + p.strip('_')
        if core_rest.endswith(inv):
            return core_rest[:-len(inv)]
    return core_rest


def rename_with_preserved_parts(obj: str, name_base: str, index: int | None, name_first: bool):
    old = short_name(obj)

    if name_first:
        base_no_suffix, found_suffixes = extract_suffixes(old, 2)

        prefix = ""
        core = ""
        for p in PREFIXES:
            inv = '_' + p.strip('_')
            if base_no_suffix.endswith(inv):
                prefix = inv
                core = base_no_suffix[:-len(inv)]
                break
        else:
            core = base_no_suffix
            prefix = ""

        new_core = name_base
        if index is not None:
            new_core += f"{index:02d}"
        new_name = f"{new_core}{prefix}{''.join(found_suffixes)}"
    else:
        temp = old
        prefix = ""
        for p in PREFIXES:
            if temp.startswith(p):
                prefix = p
                temp = temp[len(p):]
                break

        core, found_suffixes = extract_suffixes(temp, 2)
        suffix1 = found_suffixes[0] if len(found_suffixes) > 0 else ""
        suffix2 = found_suffixes[1] if len(found_suffixes) > 1 else ""

        new_core = name_base
        if index is not None:
            new_core += f"{index:02d}"
        new_name = f"{prefix}{new_core}{suffix1}{suffix2}"

    if not is_valid_name(new_name):
        cmds.warning(f"'{new_name}' contains forbidden characters")
        return None

    try:
        return cmds.rename(obj, new_name)
    except RuntimeError as err:
        cmds.warning(f"Could not rename '{old}': {err}")
        return None


def add_prefix_to_objects(objs, prefix_val: str, name_first: bool):
    if not prefix_val:
        cmds.warning("Type a prefix to rename")
        return

    prefix_fmt = ('_' + prefix_val.strip('_')) if name_first else (prefix_val.strip('_') + '_')

    for obj in objs:
        name = short_name(obj)
        name_wo_start = remove_any_start_prefix(name)
        base_no_suffix, found_suffixes = extract_suffixes(name_wo_start, 2)
        core = remove_any_end_prefix_block(base_no_suffix)

        if name_first:
            new_name = f"{core}{prefix_fmt}{''.join(found_suffixes)}"
        else:
            new_name = prefix_fmt + (core + ''.join(found_suffixes))

        if is_valid_name(new_name):
            try:
                cmds.rename(obj, new_name)
            except RuntimeError:
                pass


def add_suffix_to_objects(objs, suffix_val: str, preserve_existing: bool):
    if suffix_val and not suffix_val.startswith('_'):
        suffix_val = '_' + suffix_val

    for obj in objs:
        name = short_name(obj)
        base, found_suffixes = extract_suffixes(name, 2)
        second_sfx = found_suffixes[1] if len(found_suffixes) > 1 else ""

        if preserve_existing and found_suffixes:
            continue

        new_name = f"{base}{suffix_val}{second_sfx}"
        if is_valid_name(new_name):
            try:
                cmds.rename(obj, new_name)
            except RuntimeError:
                pass


def add_second_suffix_to_objects(objs, suffix2_val: str, preserve_existing: bool):
    if preserve_existing:
        return

    if suffix2_val and not suffix2_val.startswith('_'):
        suffix2_val = '_' + suffix2_val

    for obj in objs:
        name = short_name(obj)
        core, found = extract_suffixes(name, 2)
        first_sfx = found[0] if len(found) >= 1 else ""
        new_name = f"{core}{first_sfx}{suffix2_val}"
        if is_valid_name(new_name):
            try:
                cmds.rename(obj, new_name)
            except RuntimeError:
                pass


def delete_prefix(objs):
    for obj in objs:
        name = short_name(obj)
        for p in PREFIXES:
            idx = name.find(p)
            if idx != -1:
                new_name = name[:idx] + name[idx + len(p):]
                try:
                    cmds.rename(obj, new_name)
                except RuntimeError:
                    pass
                break


def delete_suffix(objs, suffixes):
    for obj in objs:
        name = short_name(obj)
        for s in suffixes:
            if name.endswith(s):
                try:
                    cmds.rename(obj, name[:-len(s)])
                except RuntimeError:
                    pass
                break


def search_replace(scope: str, search_txt: str, replace_txt: str):
    if not search_txt:
        cmds.warning("Enter a search term")
        return

    if scope == 'selection':
        objs = selected_transforms()
    elif scope == 'hierarchy':
        objs = []
        for o in selected_transforms():
            kids = cmds.listRelatives(o, ad=True, type='transform', fullPath=False) or []
            objs.extend(kids)
            objs.append(o)
        seen = set()
        objs = [x for x in objs if not (x in seen or seen.add(x))]
    else:
        objs = cmds.ls(type='transform') or []

    for o in objs:
        name = short_name(o)
        if search_txt in name:
            new_name = name.replace(search_txt, replace_txt)
            if not cmds.objExists(new_name):
                try:
                    cmds.rename(o, new_name)
                except RuntimeError as err:
                    print(f"Could not rename node '{name}': {err}")
