# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
import sys
import ctypes

# Custom Library

# Custom Packages

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
def fix_icon_for_taskbar(app_model_id:str):
    # Define application ICON,
    #   makes sure the APPLICATION icon is shown in the taskbar
    if (sys_platform := sys.platform) == "win32":
        # WINDOWS NEEDS THIS to make this possible
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_model_id)
    else:
        # TODO fix this! (aka, find out how to do this)
        raise NotImplementedError(f"the 'fix_icon_for_taskbar' function doe not work for the os: {sys_platform}")