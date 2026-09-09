#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test UI functionality of Viewport Playblast."""

import sys
import os
import unittest

# Mock Maya modules (same as test_core.py)
# ... [include mock modules here]

from PySide2 import QtCore, QtWidgets
from viewport_playblast import ViewportPlayblastUi


class TestViewportPlayblastUi(unittest.TestCase):
    """Test UI functionality."""

    def setUp(self):
        """Set up test environment."""
        self.app = QtWidgets.QApplication.instance()
        if not self.app:
            self.app = QtWidgets.QApplication([])
        self.ui = ViewportPlayblastUi()

    def tearDown(self):
        """Clean up test environment."""
        self.ui.close()
        self.ui.deleteLater()

    def test_ui_initialization(self):
        """Test UI initialization."""
        self.assertIsNotNone(self.ui)
        self.assertEqual(self.ui.windowTitle(), "Viewport Playblast")

    def test_ui_widgets_created(self):
        """Test UI widgets are created."""
        self.assertIsNotNone(self.ui.output_dir_path_le)
        self.assertIsNotNone(self.ui.output_filename_le)
        self.assertIsNotNone(self.ui.resolution_select_cmb)
        self.assertIsNotNone(self.ui.camera_select_cmb)
        self.assertIsNotNone(self.ui.frame_range_cmb)
        self.assertIsNotNone(self.ui.encoding_container_cmb)
        self.assertIsNotNone(self.ui.playblast_btn)
        self.assertIsNotNone(self.ui.output_edit)

    def test_ui_connections(self):
        """Test signal connections."""
        self.assertIsNotNone(self.ui.playblast_btn.clicked)
        self.assertIsNotNone(self.ui.close_btn.clicked)
        self.assertIsNotNone(self.ui.refresh_btn.clicked)
        self.assertIsNotNone(self.ui.clear_btn.clicked)

    def test_do_playblast(self):
        """Test playblast execution from UI."""
        self.ui.output_dir_path_le.setText("/tmp")
        self.ui.output_filename_le.setText("test")
        self.ui.force_overwrite_cb.setChecked(True)

        try:
            self.ui.do_playblast()
        except Exception as e:
            self.fail(f"do_playblast raised exception: {e}")


def run_ui_tests():
    """Run UI tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestViewportPlayblastUi)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_ui_tests()
    sys.exit(0 if success else 1)
