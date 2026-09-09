"""
Path utility functions.
"""

import os


class PathUtils:
    """Path helper functions."""

    @staticmethod
    def normalize_path(path):
        """Normalize path for Linux compatibility."""
        if path:
            path = path.replace("\\", "/")
        return path

    @staticmethod
    def resolve_placeholders(path, replacements):
        """Resolve placeholders in a path."""
        for placeholder, value in replacements.items():
            if placeholder in path:
                path = path.replace(placeholder, value)
        return path

    @staticmethod
    def ensure_directory_exists(path):
        """Ensure a directory exists, creating if necessary."""
        if not os.path.exists(path):
            os.makedirs(path)
        return path
