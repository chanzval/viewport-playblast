"""
Maya utility functions.
"""

import maya.cmds as cmds
import maya.mel as mel


class MayaUtils:
    """Maya helper functions."""

    @staticmethod
    def get_project_dir_path():
        """Get Maya project directory path."""
        return cmds.workspace(q=True, rootDirectory=True)

    @staticmethod
    def get_scene_name():
        """Get current Maya scene name."""
        scene_name = cmds.file(q=True, sceneName=True, shortName=True)
        if scene_name:
            import os

            scene_name = os.path.splitext(scene_name)[0]
        else:
            scene_name = "untitled"

        return scene_name

    @staticmethod
    def get_viewport_panel():
        """Get the active viewport panel."""
        model_panel = cmds.getPanel(withFocus=True)
        try:
            cmds.modelPanel(model_panel, q=True, modelEditor=True)
        except:
            return None

        return model_panel

    @staticmethod
    def get_active_camera():
        """Get the active viewport camera."""
        model_panel = MayaUtils.get_viewport_panel()
        if not model_panel:
            return None

        return cmds.modelPanel(model_panel, q=True, camera=True)

    @staticmethod
    def set_active_camera(camera):
        """Set the active viewport camera."""
        model_panel = MayaUtils.get_viewport_panel()
        if model_panel:
            mel.eval("lookThroughModelPanel {0} {1}".format(camera, model_panel))

    @staticmethod
    def get_frame_rate():
        """Get the current Maya frame rate."""
        rate_str = cmds.currentUnit(q=True, time=True)

        if rate_str == "game":
            return 15.0
        elif rate_str == "film":
            return 24.0
        elif rate_str == "pal":
            return 25.0
        elif rate_str == "ntsc":
            return 30.0
        elif rate_str == "show":
            return 48.0
        elif rate_str == "palf":
            return 50.0
        elif rate_str == "ntscf":
            return 60.0
        elif rate_str.endswith("fps"):
            return float(rate_str[0:-3])
        else:
            raise RuntimeError("Unsupported frame rate: {0}".format(rate_str))
