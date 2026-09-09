#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test core functionality of ViewportPlayblast."""

import sys
import os
import re
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from viewport_playblast import ViewportPlayblast


class TestViewportPlayblast(unittest.TestCase):
    """Test core ViewportPlayblast functionality."""

    def setUp(self):
        """Set up test environment."""
        self.playblast = ViewportPlayblast(ffmpeg_path="/usr/bin/ffmpeg")
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test class initialization."""
        self.assertIsNotNone(self.playblast)
        self.assertEqual(self.playblast.VERSION, "1.0.0")
        self.assertEqual(self.playblast.get_ffmpeg_path(), "/usr/bin/ffmpeg")

    def test_set_camera(self):
        """Test camera setting."""
        self.playblast.set_camera("persp")
        self.assertEqual(self.playblast._camera, "persp")

        self.playblast.set_camera("invalid_cam")
        self.assertIsNone(self.playblast._camera)

    def test_set_resolution_preset(self):
        """Test resolution presets."""
        self.playblast.set_resolution("HD 1080")
        width, height = self.playblast.get_resolution_width_height()
        self.assertEqual((width, height), (1920, 1080))

        self.playblast.set_resolution("HD 720")
        width, height = self.playblast.get_resolution_width_height()
        self.assertEqual((width, height), (1280, 720))

    def test_set_resolution_custom(self):
        """Test custom resolution."""
        custom_res = (800, 600)
        self.playblast.set_resolution(custom_res)
        width, height = self.playblast.get_resolution_width_height()
        self.assertEqual((width, height), custom_res)

    def test_set_frame_range_preset(self):
        """Test frame range presets."""
        import maya.cmds as cmds

        original_playbackOptions = cmds.playbackOptions
        original_getAttr = cmds.getAttr

        try:

            def mock_playbackOptions(
                q=None,
                minTime=None,
                maxTime=None,
                animationStartTime=None,
                animationEndTime=None,
            ):
                if minTime:
                    return 1
                if maxTime:
                    return 100
                if animationStartTime:
                    return 1
                if animationEndTime:
                    return 50
                return None

            def mock_getAttr(attr):
                if attr == "defaultRenderGlobals.startFrame":
                    return 1
                if attr == "defaultRenderGlobals.endFrame":
                    return 100
                return None

            cmds.playbackOptions = mock_playbackOptions
            cmds.getAttr = mock_getAttr

            self.playblast = ViewportPlayblast(ffmpeg_path="/usr/bin/ffmpeg")

            self.playblast.set_frame_range("Playback")
            start, end = self.playblast.get_start_end_frame()
            self.assertEqual(start, 1)
            self.assertEqual(end, 100)

            self.playblast.set_frame_range("Animation")
            start, end = self.playblast.get_start_end_frame()
            self.assertEqual(start, 1)
            self.assertEqual(end, 50)

            self.playblast.set_frame_range("Render")
            start, end = self.playblast.get_start_end_frame()
            self.assertEqual(start, 1)
            self.assertEqual(end, 100)

        finally:
            cmds.playbackOptions = original_playbackOptions
            cmds.getAttr = original_getAttr

    def test_set_frame_range_custom(self):
        """Test custom frame range."""
        custom_range = (50, 75)
        self.playblast.set_frame_range(custom_range)
        start, end = self.playblast.get_start_end_frame()
        self.assertEqual((start, end), custom_range)

    def test_set_encoding(self):
        """Test encoding settings."""
        self.playblast.set_encoding("mp4", "h264")
        self.assertEqual(self.playblast._container_format, "mp4")
        self.assertEqual(self.playblast._encoder_name, "h264")

        self.playblast.set_encoding("invalid", "h264")
        self.assertEqual(self.playblast._container_format, "mp4")

    def test_set_h264_settings(self):
        """Test h264 settings."""
        self.playblast.set_h264_settings("High", "fast")
        settings = self.playblast.get_h264_settings()
        self.assertEqual(settings["quality"], "High")
        self.assertEqual(settings["preset"], "fast")

    def test_set_image_settings(self):
        """Test image settings."""
        self.playblast.set_image_settings(85)
        settings = self.playblast.get_image_settings()
        self.assertEqual(settings["quality"], 85)

        self.playblast.set_image_settings(150)
        settings = self.playblast.get_image_settings()
        self.assertEqual(settings["quality"], 85)

    def test_requires_ffmpeg(self):
        """Test FFmpeg requirement check."""
        self.playblast.set_encoding("mp4", "h264")
        self.assertTrue(self.playblast._container_format != "Image")

        self.playblast.set_encoding("Image", "png")
        self.assertTrue(self.playblast._container_format == "Image")

    def test_resolve_output_directory_path(self):
        """Test output directory resolution."""
        import maya.cmds as cmds

        original_workspace = cmds.workspace

        try:

            def mock_workspace(q=None, rootDirectory=None):
                return "/tmp"

            cmds.workspace = mock_workspace
            self.playblast = ViewportPlayblast(ffmpeg_path="/usr/bin/ffmpeg")

            dir_path = "<Show>/movies"
            resolved = self.playblast.resolve_output_directory_path(dir_path)
            self.assertEqual(resolved, "/tmp/movies")

        finally:
            cmds.workspace = original_workspace

        dir_path = "/custom/path"
        resolved = self.playblast.resolve_output_directory_path(dir_path)
        self.assertEqual(resolved, "/custom/path")

    def test_resolve_output_filename(self):
        """Test filename resolution."""
        import maya.cmds as cmds

        original_file = cmds.file

        try:

            def mock_unsaved(q=None, sceneName=None, shortName=None):
                if q and sceneName and shortName:
                    return None
                return None

            cmds.file = mock_unsaved
            self.playblast = ViewportPlayblast(ffmpeg_path="/usr/bin/ffmpeg")

            filename = "<Scene>_playblast"
            resolved = self.playblast.resolve_output_filename(filename)
            self.assertEqual(resolved, "untitled_playblast")

        finally:
            cmds.file = original_file

        filename = "fixed_name"
        resolved = self.playblast.resolve_output_filename(filename)
        self.assertEqual(resolved, "fixed_name")

    def test_get_project_dir_path(self):
        """Test project directory path."""
        project_path = self.playblast.get_project_dir_path()

        self.assertIsInstance(project_path, str)
        self.assertTrue(len(project_path) > 0)
        self.assertTrue(os.path.exists(project_path))
        self.assertTrue(os.path.isdir(project_path))
        self.assertTrue(os.path.isabs(project_path))

    def test_get_scene_name(self):
        """Test scene name."""
        scene_name = self.playblast.get_scene_name()

        self.assertIsInstance(scene_name, str)
        self.assertTrue(len(scene_name) > 0)
        self.assertNotIn(".", scene_name)
        self.assertTrue(re.match(r"^[\w\-_]+$", scene_name))

    def test_validate_ffmpeg(self):
        """Test FFmpeg validation."""
        self.playblast.set_ffmpeg_path("/usr/bin/ffmpeg")
        result = self.playblast.validate_ffmpeg()

        if os.path.exists("/usr/bin/ffmpeg"):
            self.assertTrue(result)

        self.playblast.set_ffmpeg_path("/path/to/nonexistent/ffmpeg")
        result = self.playblast.validate_ffmpeg()
        self.assertFalse(result)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestViewportPlayblast))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=" * 60)
    print("Viewport Playblast - Core Tests")
    print("=" * 60)
    success = run_tests()
    sys.exit(0 if success else 1)
