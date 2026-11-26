"""
rename_tool.ui

UI implementation (maya.cmds UI) for the Rename Tool.
"""
from __future__ import annotations

from maya import cmds # pyright: ignore[reportMissingImports]
from functools import partial

from .constants import PREFIXES, EXTRA_SUFFIXES, SUFFIXES, TOOL_VERSION, TOOL_DATE
from . import core
from .utils import extract_suffixes, is_valid_name, strip_prefix, build_name


class RenameToolUI:
    def __init__(self):
        self.window = 'RenameWin'
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        self._build_ui()
        cmds.showWindow(self.window)

        cmds.scriptJob(event=["SelectionChanged", self.preview_names], parent=self.window)
        self.preview_names()

    @staticmethod
    def _tf_get(ctrl):
        return cmds.textField(ctrl, q=True, text=True)

    @staticmethod
    def _tf_set(ctrl, val):
        cmds.textField(ctrl, e=True, text=val)

    @staticmethod
    def _cb_get(ctrl):
        return bool(cmds.checkBox(ctrl, q=True, v=True))

    @staticmethod
    def _cb_set(ctrl, val):
        cmds.checkBox(ctrl, e=True, v=bool(val))

    @staticmethod
    def _rb_get(ctrl):
        return int(cmds.radioButtonGrp(ctrl, q=True, sl=True))

    @staticmethod
    def _rb_set(ctrl, val):
        cmds.radioButtonGrp(ctrl, e=True, sl=int(val))

    @staticmethod
    def _sf_set(ctrl, text):
        cmds.scrollField(ctrl, e=True, text=text)

    @staticmethod
    def _sf_bgc(ctrl, rgb):
        cmds.scrollField(ctrl, e=True, bgc=rgb)

    def _build_ui(self):
        cmds.window(self.window, title=f"Rename {TOOL_VERSION}", widthHeight=(390, 725), sizeable=False)
        cmds.columnLayout(adj=True, rs=2)

        cmds.rowLayout(nc=2, adjustableColumn=1, columnAlign=(1, 'center'), columnWidth2=(280, 60))
        cmds.text(
            label=f"~ Rename Tool {TOOL_VERSION} ~",
            align='center', font='boldLabelFont',
            annotation=f"Tool by JaimeBM ~{TOOL_DATE}~",
            w=355
        )
        cmds.button(label="Reset Values", c=self.reset_values, w=80, bgc=(0.6, 0.2, 0.2), h=20)
        cmds.setParent('..')
        cmds.separator(h=5, style='in')

        cmds.frameLayout(label="Name", collapsable=False, mw=4, mh=2)
        cmds.rowLayout(nc=3, adj=2, cw3=(30, 110, 60))
        cmds.button(label='N', enable=True, w=30, h=20, c=self.get_name, bgc=(0.6, 0.6, 0.6))
        self.renameField = cmds.textField(w=110, placeholderText='name_type', cc=self.preview_names)
        cmds.button(label="Add", w=60, h=20, c=self.rename_objects, bgc=(0.6, 0.6, 0.6))
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.separator(h=5, style='in')

        cmds.frameLayout(label="Prefix", collapsable=False, mw=4, mh=2)
        cmds.rowLayout(nc=3, adj=2, cw3=(30, 110, 60))
        cmds.button(label='P', enable=True, w=30, h=20, c=self.get_prefix_from_sel, bgc=(0.6, 0.6, 0.6))
        self.prefixField = cmds.textField(w=110, placeholderText='prefix_', cc=self.preview_names)
        cmds.button(label="Add", w=60, h=20, c=self.add_prefix, bgc=(0.6, 0.6, 0.6))
        cmds.setParent('..')
        cmds.setParent('..')

        cmds.text(label="Quick Prefix Buttons:", align='center', font='boldLabelFont')
        cmds.rowLayout(nc=6, cw6=[58.33] * 6)
        for p in PREFIXES:
            cmds.button(label=p, w=63, h=20, bgc=(0.3, 0.0, 0.0), c=partial(self.set_prefix, p))
        cmds.setParent('..')
        cmds.separator(h=5, style='in')

        cmds.frameLayout(label="Suffix", collapsable=False, mw=4, mh=2)
        cmds.rowLayout(nc=3, adj=2, cw3=(30, 110, 60))
        cmds.button(label='S', enable=True, w=30, h=20, c=self.get_suffix_from_sel, bgc=(0.6, 0.6, 0.6))
        self.suffixField = cmds.textField(w=110, placeholderText='_suffix1', cc=self.preview_names)
        cmds.button(label="Add", w=60, h=20, c=self.add_suffix, bgc=(0.6, 0.6, 0.6))
        cmds.setParent('..')

        cmds.rowLayout(nc=2, adjustableColumn=2, columnAlign=(1, 'right'), columnWidth2=(130, 210))
        cmds.text(label="Quick Suffix Target:", align='right', font='boldLabelFont')
        self.quickSuffixTarget = cmds.radioButtonGrp(
            labelArray2=['Suffix', 'Second Suffix'], numberOfRadioButtons=2,
            select=1, cw2=(90, 110), sl=1, cc=self.preview_names
        )
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.separator(h=5, style='in')

        cmds.text(label="Quick Suffix Buttons:", align='center', font='boldLabelFont')
        cmds.rowLayout(nc=6, cw6=[63] * 6)
        for s in ['_ctrl', '_jnt', '_null', '_loc', '_geo', '_old']:
            cmds.button(label=s, w=63, h=20, bgc=(0.3, 0.0, 0.0), c=partial(self.quick_suffix, s))
        cmds.setParent('..')

        cmds.rowLayout(nc=6, cw6=[63] * 6)
        for s in ['_CTRL', '_JNT', '_NULL', '_LOC', '_GEO', '_OLD']:
            cmds.button(label=s, w=63, h=20, bgc=(0.3, 0.0, 0.0), c=partial(self.quick_suffix, s))
        cmds.setParent('..')

        cmds.button(label="More...", h=20, c=self.open_extra_suffix_window, bgc=(0.2, 0.2, 0.5))
        cmds.separator(h=5, style='in')

        cmds.frameLayout(label="Second Suffix", collapsable=False, mw=4, mh=2)
        cmds.rowLayout(nc=4, adj=3, cw4=(20, 30, 220, 60))
        self.enableSecondSuffixCheckbox = cmds.checkBox(v=False, cc=self.toggle_second_suffix_ui)
        cmds.button(label='S2', enable=True, w=30, h=20, c=self.get_second_suffix_from_sel, bgc=(0.6, 0.6, 0.6))
        self.secondSuffixField = cmds.textField(enable=False, placeholderText='_suffix2', cc=self.preview_names)
        self.secondSuffixAddBtn = cmds.button(label="Add", enable=False, w=60, h=20, c=self.add_second_suffix, bgc=(0.6, 0.6, 0.6))
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.separator(h=5, style='in')

        self.skipNumberCheckbox = cmds.checkBox(label="Do not add a number", v=True, cc=self.preview_names)
        self.preservePartsCheckbox = cmds.checkBox(label="Preserve existing suffix", v=False, cc=self.preview_names)
        self.nameFirstCheckbox = cmds.checkBox(
            label="Name-First Order (name_prefix_suffix1_suffix2)",
            v=False,
            cc=self.preview_names
        )

        cmds.separator(h=5, style='in')

        cmds.button(label="Apply PREFIX, NAME and a SUFFIX", bgc=(0.0, 0.3, 0.0), c=self.full_rename)
        cmds.separator(h=5, style='in')

        cmds.rowLayout(nc=2, adjustableColumn=2, columnAlign=(1, 'center'), columnWidth2=(195, 195))
        cmds.button(label="Delete Prefix", w=195, h=20, c=self.delete_prefix, bgc=(0.6, 0.6, 0.6))
        cmds.button(label="Delete Suffix", w=195, h=20, c=self.delete_suffix, bgc=(0.6, 0.6, 0.6))
        cmds.setParent('..')
        cmds.separator(h=5, style='in')

        cmds.frameLayout(label="Search & Replace", collapsable=False, mw=4, mh=2)
        cmds.rowLayout(nc=2, cw2=(190, 195), adjustableColumn=2)
        self.searchField = cmds.textField(w=190, placeholderText='Search...', cc=self.preview_names)
        self.replaceField = cmds.textField(w=195, placeholderText='Replace...', cc=self.preview_names)
        cmds.setParent('..')

        cmds.rowLayout(nc=3, cw3=(125, 125, 125))
        cmds.button(label="Selection", w=125, c=partial(self.search_replace, 'selection'))
        cmds.button(label="Hierarchy", w=125, c=partial(self.search_replace, 'hierarchy'))
        cmds.button(label="All", w=125, c=partial(self.search_replace, 'all'))
        cmds.setParent('..')
        cmds.setParent('..')

        cmds.separator(h=5, style='in')

        cmds.frameLayout(label="Preview", collapsable=False, mw=4, mh=2)
        self.previewField = cmds.scrollField(editable=False, wordWrap=False, h=30)
        cmds.button(label="Update Preview", c=self.preview_names, align='center', h=20)
        cmds.setParent('..')
        cmds.separator(h=5, style='in')

    def open_extra_suffix_window(self, *_):
        win_name = "ExtraSuffixWin"
        if cmds.window(win_name, exists=True):
            cmds.deleteUI(win_name, window=True)

        cmds.window(win_name, title="Extra Suffixes", widthHeight=(290, 55), sizeable=True)
        cmds.columnLayout(adj=True, rs=2)

        row = []
        for i, suf in enumerate(EXTRA_SUFFIXES, 1):
            row.append(suf)
            if i % 4 == 0 or i == len(EXTRA_SUFFIXES):
                cmds.rowLayout(nc=len(row))
                for s in row:
                    cmds.button(label=s, w=70, h=20, bgc=(0.3, 0.0, 0.0), c=partial(self.quick_suffix, s))
                cmds.setParent('..')
                row = []
        cmds.showWindow(win_name)

    def rename_objects(self, *_):
        name_base = self._tf_get(self.renameField)
        sel = core.selected_transforms()
        if not sel:
            cmds.warning("Select objects to rename")
            return
        if not name_base:
            cmds.warning("Enter a name to rename")
            return

        skip = self._cb_get(self.skipNumberCheckbox)
        name_first = self._cb_get(self.nameFirstCheckbox)

        for i, obj in enumerate(sel):
            index = None if (skip and len(sel) == 1) else i + 1
            core.rename_with_preserved_parts(obj, name_base, index, name_first)

        self.preview_names()

    def add_prefix(self, *_):
        prefix_val = self._tf_get(self.prefixField) or ""
        sel = core.selected_transforms()
        if not sel:
            cmds.warning("Select objects to rename")
            return
        if not prefix_val:
            cmds.warning("Type a prefix to rename")
            return

        name_first = self._cb_get(self.nameFirstCheckbox)
        core.add_prefix_to_objects(sel, prefix_val, name_first)
        self.preview_names()

    def add_suffix(self, *_):
        sel = core.selected_transforms()
        if not sel:
            cmds.warning("Select objects to add a suffix")
            return

        suffix_val = self._tf_get(self.suffixField) or ""
        if suffix_val and not suffix_val.startswith('_'):
            suffix_val = '_' + suffix_val
            self._tf_set(self.suffixField, suffix_val)

        preserve = self._cb_get(self.preservePartsCheckbox)
        core.add_suffix_to_objects(sel, suffix_val, preserve)
        self.preview_names()

    def add_second_suffix(self, *_):
        sel = core.selected_transforms()
        if not sel:
            cmds.warning("Select objects to add a second suffix")
            return

        preserve = self._cb_get(self.preservePartsCheckbox)
        suffix2_val = self._tf_get(self.secondSuffixField) or ""
        if suffix2_val and not suffix2_val.startswith('_'):
            suffix2_val = '_' + suffix2_val
            self._tf_set(self.secondSuffixField, suffix2_val)

        core.add_second_suffix_to_objects(sel, suffix2_val, preserve)
        self.preview_names()

    def delete_prefix(self, *_):
        core.delete_prefix(core.selected_transforms())
        self.preview_names()

    def delete_suffix(self, *_):
        core.delete_suffix(core.selected_transforms(), SUFFIXES)
        self.preview_names()

    def search_replace(self, scope, *_):
        core.search_replace(scope, self._tf_get(self.searchField), self._tf_get(self.replaceField))
        self.preview_names()

    def quick_suffix(self, suffix, *_):
        if not suffix.startswith('_'):
            suffix = '_' + suffix
        if self._rb_get(self.quickSuffixTarget) == 2:
            self._tf_set(self.secondSuffixField, suffix)
        else:
            self._tf_set(self.suffixField, suffix)
        self.preview_names()

    def toggle_second_suffix_ui(self, *_):
        state = self._cb_get(self.enableSecondSuffixCheckbox)
        cmds.textField(self.secondSuffixField, e=True, en=state)
        cmds.button(self.secondSuffixAddBtn, e=True, en=state)
        self.preview_names()

    def full_rename(self, *_):
        sel = core.selected_transforms()
        if not sel:
            cmds.warning("Select objects to rename")
            return

        base = self._tf_get(self.renameField)
        if not base:
            cmds.warning("Enter a base name to reenumerate")
            return

        raw_prefix = self._tf_get(self.prefixField) or ""
        raw_suffix = self._tf_get(self.suffixField) or ""
        raw_suffix2 = self._tf_get(self.secondSuffixField) or ""

        name_first = self._cb_get(self.nameFirstCheckbox)
        preserve = self._cb_get(self.preservePartsCheckbox)
        skip = self._cb_get(self.skipNumberCheckbox)

        for i, obj in enumerate(sel):
            old = obj.split("|")[-1]
            index = None if (skip and len(sel) == 1) else i + 1

            sv = "" if preserve else raw_suffix
            sv2 = "" if preserve else raw_suffix2

            new_name = build_name(
                base=base,
                index=index,
                prefix=raw_prefix,
                suffix=sv,
                suffix2=sv2,
                name_first=name_first
            )

            if preserve:
                _, found = extract_suffixes(old, 2)
                if not sv and len(found) > 0 and not new_name.endswith(found[0]):
                    new_name = new_name + found[0]
                if not sv2 and len(found) > 1 and not new_name.endswith(found[1]):
                    new_name = new_name + found[1]

            if not is_valid_name(new_name):
                cmds.warning(f"'{new_name}' contains forbidden characters")
                continue

            try:
                cmds.rename(obj, new_name)
            except RuntimeError as err:
                cmds.warning(f"Could not rename '{old}': {err}")

        self.preview_names()

    def get_name(self, *_):
        sel = core.selected_transforms()
        if not sel:
            return
        name = sel[0].split("|")[-1]
        name_first = self._cb_get(self.nameFirstCheckbox)
        no_pref = strip_prefix(name, name_first)
        core_name, _ = extract_suffixes(no_pref, 2)
        self._tf_set(self.renameField, core_name)
        self.preview_names()

    def get_prefix_from_sel(self, *_):
        sel = core.selected_transforms()
        if not sel:
            return
        name = sel[0].split("|")[-1]
        name_first = self._cb_get(self.nameFirstCheckbox)
        core_rest, _ = extract_suffixes(name, 2)

        prefix = ""
        if name_first:
            for p in PREFIXES:
                inv = '_' + p.strip('_')
                if core_rest.endswith(inv):
                    prefix = inv
                    break
        else:
            for p in PREFIXES:
                if name.startswith(p):
                    prefix = p
                    break

        self._tf_set(self.prefixField, prefix)
        self.preview_names()

    def get_suffix_from_sel(self, *_):
        sel = core.selected_transforms()
        if not sel:
            return
        name = sel[0].split("|")[-1]
        name_first = self._cb_get(self.nameFirstCheckbox)
        _, suffixes = extract_suffixes(strip_prefix(name, name_first), 2)
        sfx1 = suffixes[0] if len(suffixes) > 0 else ""
        self._tf_set(self.suffixField, sfx1)
        self.preview_names()

    def get_second_suffix_from_sel(self, *_):
        sel = core.selected_transforms()
        if not sel:
            return
        name = sel[0].split("|")[-1]
        name_first = self._cb_get(self.nameFirstCheckbox)
        _, suffixes = extract_suffixes(strip_prefix(name, name_first), 2)
        sfx2 = suffixes[1] if len(suffixes) > 1 else ""
        self._tf_set(self.secondSuffixField, sfx2)
        self.preview_names()

    def set_prefix(self, prefix, *_):
        core_p = prefix.strip('_')
        new_pref = f"_{core_p}" if self._cb_get(self.nameFirstCheckbox) else f"{core_p}_"
        self._tf_set(self.prefixField, new_pref)
        self.preview_names()

    def preview_names(self, *_):
        base = self._tf_get(self.renameField)
        prefix_val = self._tf_get(self.prefixField) or ""
        suffix_val = self._tf_get(self.suffixField) or ""
        suffix2_val = ""

        name_first = self._cb_get(self.nameFirstCheckbox)
        skip = self._cb_get(self.skipNumberCheckbox)
        preserve = self._cb_get(self.preservePartsCheckbox)

        if suffix_val and not suffix_val.startswith('_'):
            suffix_val = '_' + suffix_val

        if self._cb_get(self.enableSecondSuffixCheckbox):
            suffix2_val = self._tf_get(self.secondSuffixField) or ""
            if suffix2_val and not suffix2_val.startswith('_'):
                suffix2_val = '_' + suffix2_val

        search_txt = self._tf_get(self.searchField)
        replace_txt = self._tf_get(self.replaceField)

        sel = core.selected_transforms()
        if sel:
            old_name = sel[0].split("|")[-1]
            index = None if (skip and len(sel) == 1) else 1
            core_guess = base or old_name

            suffix = "" if preserve else suffix_val
            suffix2 = "" if preserve else suffix2_val

            new_name = build_name(
                base=core_guess,
                index=index,
                prefix=prefix_val,
                suffix=suffix,
                suffix2=suffix2,
                name_first=name_first
            )
            if search_txt:
                new_name = new_name.replace(search_txt, replace_txt)

            if new_name == old_name:
                self._sf_set(self.previewField, f"{old_name} selected")
                self._sf_bgc(self.previewField, (0.1, 0.3, 0.3))
            elif not is_valid_name(new_name):
                self._sf_set(self.previewField, "Contains forbidden characters")
                self._sf_bgc(self.previewField, (0.4, 0.2, 0.2))
            else:
                self._sf_set(self.previewField, f"{old_name} -> {new_name}")
                self._sf_bgc(self.previewField, (0.2, 0.4, 0.2))
        else:
            if not base and not prefix_val and not suffix_val and not suffix2_val:
                self._sf_set(self.previewField, "")
                return
            index = None if skip else 1
            suffix = "" if preserve else suffix_val
            suffix2 = "" if preserve else suffix2_val
            new_name = build_name(
                base=base,
                index=index,
                prefix=prefix_val,
                suffix=suffix,
                suffix2=suffix2,
                name_first=name_first
            )
            self._sf_set(self.previewField, new_name)
            self._sf_bgc(self.previewField, (0.2, 0.4, 0.2))

    def clear_preview(self):
        self._sf_set(self.previewField, "")
        self._sf_bgc(self.previewField, (0.2, 0.2, 0.2))

    def reset_values(self, *_):
        self._tf_set(self.renameField, "")
        self._tf_set(self.prefixField, "")
        self._tf_set(self.suffixField, "")
        self._tf_set(self.secondSuffixField, "")
        self._tf_set(self.searchField, "")
        self._tf_set(self.replaceField, "")

        self._cb_set(self.enableSecondSuffixCheckbox, False)
        self.toggle_second_suffix_ui()

        self._rb_set(self.quickSuffixTarget, 1)

        self._cb_set(self.skipNumberCheckbox, True)
        self._cb_set(self.preservePartsCheckbox, False)
        self._cb_set(self.nameFirstCheckbox, False)

        self.clear_preview()
        self.preview_names()
