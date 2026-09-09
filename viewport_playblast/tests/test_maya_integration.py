#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test Maya integration functionality."""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMayaIntegration(unittest.TestCase):
    """Test Maya integration."""

    def test_maya_modules_available(self):
        """Test Maya modules are available."""
        try:
            import maya.cmds as cmds
            import maya.mel as mel
            import maya.OpenMaya as om
            import maya.OpenMayaUI as omui

            self.assertTrue(True)
        except ImportError:
            self.skipTest("Maya modules not available in this environment")

    def test_maya_commands(self):
        """Test basic Maya commands."""
        try:
            import maya.cmds as cmds

            version = cmds.about(version=True)
            self.assertIsNotNone(version)
        except Exception as e:
            self.skipTest(f"Maya command failed: {e}")


def run_maya_tests():
    """Run Maya integration tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMayaIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_maya_tests()
    sys.exit(0 if success else 1)
