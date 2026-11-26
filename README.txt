Rename Tool V3.8
Maya Utility

FEATURES
--------
- Rename selected transforms with optional sequential numbering.
- Add, read, or remove prefixes and suffixes, including a second suffix.
- Use quick prefix and suffix buttons, plus additional suffixes.
- Preserve existing suffixes when renaming.
- Choose prefix-first or name-first naming order.
- Search and replace names in the selection, hierarchy, or entire scene.
- Preview the resulting name before applying changes.

INSTALLATION
------------
1. Extract the Tool_Rename folder from the ZIP file.
2. Open Autodesk Maya.
3. Drag install_rename.py into the Maya viewport.
4. The tool will be copied to Maya's user scripts folder and a button
   will be created on the currently selected Shelf.
5. Click the Rename shelf button to open the tool.

RUNNING FROM THE SCRIPT EDITOR
------------------------------
import RenameTool_Launcher
RenameTool_Launcher.launch()

MODULE STRUCTURE
----------------
rename_tool/
    __init__.py
    constants.py
    core.py
    launcher.py
    ui.py
    utils.py

RenameTool_Launcher.py
    Standalone launcher

install_rename.py
    Drag-and-drop installer for Maya

COMPATIBILITY
-------------
Designed for Autodesk Maya 2026 and 2027

AUTHOR
------
JaimeBM
https://github.com/JBMOL

LICENSE
-------
MIT License. See the LICENSE file for the full license text.
