"""Drag-and-drop installer for Rename Tool in Autodesk Maya."""

import os
import shutil

import maya.cmds as cmds
import maya.mel as mel


TOOL_NAME = "Rename Tool"
TOOL_VERSION = "V3.8"
TOOL_AUTHOR = "JaimeBM"
PACKAGE_NAME = "rename_tool"
LAUNCHER_NAME = "RenameTool_Launcher.py"


def install():
    """Copy the tool package and launcher into Maya's user scripts folder."""
    user_scripts = cmds.internalVar(userScriptDir=True)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    source_tool_dir = os.path.join(current_dir, PACKAGE_NAME)
    destination_tool_dir = os.path.join(user_scripts, PACKAGE_NAME)
    source_launcher = os.path.join(current_dir, LAUNCHER_NAME)
    destination_launcher = os.path.join(user_scripts, LAUNCHER_NAME)

    if not os.path.exists(source_tool_dir):
        raise RuntimeError("The 'rename_tool' folder was not found.")

    if not os.path.exists(source_launcher):
        raise RuntimeError("'RenameTool_Launcher.py' was not found.")

    if os.path.exists(destination_tool_dir):
        shutil.rmtree(destination_tool_dir)
    shutil.copytree(source_tool_dir, destination_tool_dir)
    shutil.copy2(source_launcher, destination_launcher)


def create_shelf_button():
    """Create a launcher button on Maya's currently selected shelf."""
    top_shelf = mel.eval("$tmpVar=$gShelfTopLevel")
    current_shelf = cmds.tabLayout(top_shelf, query=True, selectTab=True)
    icon_path = os.path.join(
        cmds.internalVar(userScriptDir=True), PACKAGE_NAME, "icons", "RenameIcon.png"
    ).replace("\\", "/")

    cmds.shelfButton(
        parent=current_shelf,
        command="import RenameTool_Launcher; RenameTool_Launcher.launch()",
        annotation="Launch Rename Tool",
        label="Rename",
        sourceType="Python",
        backgroundColor=(1.0, 1.0, 1.0),
        enableBackground=True,
        image=icon_path
    )


def onMayaDroppedPythonFile(*args):
    """Maya callback executed when this installer is dropped into the viewport."""
    install()
    create_shelf_button()
    cmds.confirmDialog(
        title=f"{TOOL_NAME} Installed",
        message=(
            f"{TOOL_NAME} {TOOL_VERSION} has been installed successfully.\n\n"
            "A shelf button has been created for quick access.\n\n"
            f"Author: {TOOL_AUTHOR}"
        ),
        button=["OK"]
    )
