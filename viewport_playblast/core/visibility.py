"""
Viewport visibility management.
"""

import maya.cmds as cmds

from .constants import VIEWPORT_VISIBILITY_LOOKUP


class VisibilityManager:
    """Manage viewport visibility settings."""

    def __init__(self):
        self._visibility_lookup = VIEWPORT_VISIBILITY_LOOKUP

    def get_viewport_visibility(self, model_panel):
        """Get current viewport visibility settings."""
        viewport_visibility = []
        try:
            for item in self._visibility_lookup:
                kwargs = {item[1]: True}
                viewport_visibility.append(
                    cmds.modelEditor(model_panel, q=True, **kwargs)
                )
        except:
            import traceback

            traceback.print_exc()
            raise RuntimeError("Failed to get active viewport visibility.")

        return viewport_visibility

    def set_viewport_visibility(self, model_editor, visibility_flags):
        """Apply visibility flags to the viewport."""
        cmds.modelEditor(model_editor, e=True, **visibility_flags)

    def create_viewport_visibility_flags(self, visibility_data):
        """Create visibility flags dictionary from data."""
        visibility_flags = {}

        data_index = 0
        for item in self._visibility_lookup:
            visibility_flags[item[1]] = visibility_data[data_index]
            data_index += 1

        return visibility_flags
