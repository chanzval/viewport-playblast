"""
Main playblast functionality.
"""

import os
import copy
import shutil
import subprocess
import traceback
from datetime import datetime

from PySide2 import QtCore

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om

from .constants import (
    VERSION,
    DEFAULT_FFMPEG_PATH,
    RESOLUTION_LOOKUP,
    FRAME_RANGE_PRESETS,
    VIDEO_ENCODER_LOOKUP,
    H264_QUALITIES,
    H264_PRESETS,
    VIEWPORT_VISIBILITY_LOOKUP,
    VIEWPORT_VISIBILITY_PRESETS,
    DEFAULT_CAMERA,
    DEFAULT_RESOLUTION,
    DEFAULT_FRAME_RANGE,
    DEFAULT_CONTAINER,
    DEFAULT_ENCODER,
    DEFAULT_H264_QUALITY,
    DEFAULT_H264_PRESET,
    DEFAULT_IMAGE_QUALITY,
    DEFAULT_VISIBILITY,
    DEFAULT_PADDING,
)
from .encoder import FFmpegEncoder
from .visibility import VisibilityManager


class ViewportPlayblast(QtCore.QObject):
    """Main playblast controller class."""

    VERSION = VERSION

    DEFAULT_FFMPEG_PATH = DEFAULT_FFMPEG_PATH
    RESOLUTION_LOOKUP = RESOLUTION_LOOKUP
    FRAME_RANGE_PRESETS = FRAME_RANGE_PRESETS
    VIDEO_ENCODER_LOOKUP = VIDEO_ENCODER_LOOKUP
    H264_QUALITIES = H264_QUALITIES
    H264_PRESETS = H264_PRESETS
    VIEWPORT_VISIBILITY_LOOKUP = VIEWPORT_VISIBILITY_LOOKUP
    VIEWPORT_VISIBILITY_PRESETS = VIEWPORT_VISIBILITY_PRESETS

    DEFAULT_CAMERA = DEFAULT_CAMERA
    DEFAULT_RESOLUTION = DEFAULT_RESOLUTION
    DEFAULT_FRAME_RANGE = DEFAULT_FRAME_RANGE

    DEFAULT_CONTAINER = DEFAULT_CONTAINER
    DEFAULT_ENCODER = DEFAULT_ENCODER
    DEFAULT_H264_QUALITY = DEFAULT_H264_QUALITY
    DEFAULT_H264_PRESET = DEFAULT_H264_PRESET
    DEFAULT_IMAGE_QUALITY = DEFAULT_IMAGE_QUALITY

    DEFAULT_VISIBILITY = DEFAULT_VISIBILITY
    DEFAULT_PADDING = DEFAULT_PADDING

    output_logged = QtCore.Signal(str)

    def __init__(self, ffmpeg_path=None, log_to_maya=True):
        super(ViewportPlayblast, self).__init__()

        self._encoder = FFmpegEncoder(ffmpeg_path)
        self._encoder.output_logged.connect(self.log_output)

        self._visibility_manager = VisibilityManager()

        self.set_maya_logging_enabled(log_to_maya)

        self.set_camera(ViewportPlayblast.DEFAULT_CAMERA)
        self.set_resolution(ViewportPlayblast.DEFAULT_RESOLUTION)
        self.set_frame_range(ViewportPlayblast.DEFAULT_FRAME_RANGE)

        self.set_encoding(
            ViewportPlayblast.DEFAULT_CONTAINER, ViewportPlayblast.DEFAULT_ENCODER
        )
        self.set_h264_settings(
            ViewportPlayblast.DEFAULT_H264_QUALITY,
            ViewportPlayblast.DEFAULT_H264_PRESET,
        )
        self.set_image_settings(ViewportPlayblast.DEFAULT_IMAGE_QUALITY)

        self.set_visibility(ViewportPlayblast.DEFAULT_VISIBILITY)

    def set_ffmpeg_path(self, ffmpeg_path):
        """Set the FFmpeg executable path."""
        self._encoder.set_ffmpeg_path(ffmpeg_path)

    def get_ffmpeg_path(self):
        """Get the FFmpeg executable path."""
        return self._encoder.get_ffmpeg_path()

    def set_maya_logging_enabled(self, enabled):
        """Enable or disable Maya console logging."""
        self._log_to_maya = enabled

    def set_camera(self, camera):
        """Set the camera to use for playblast."""
        if camera and camera not in cmds.listCameras():
            self.log_error("Camera does not exist: {0}".format(camera))
            camera = None

        self._camera = camera

    def set_resolution(self, resolution):
        """Set the resolution for playblast."""
        self._resolution_preset = None

        try:
            widthHeight = self.preset_to_resolution(resolution)
            self._resolution_preset = resolution
        except:
            widthHeight = resolution

        valid_resolution = True
        try:
            if not (
                isinstance(widthHeight[0], int) and isinstance(widthHeight[1], int)
            ):
                valid_resolution = False
        except:
            valid_resolution = False

        if valid_resolution:
            if widthHeight[0] <= 0 or widthHeight[1] <= 0:
                self.log_error(
                    "Invalid resolution: {0}. Values must be greater than zero.".format(
                        widthHeight
                    )
                )
                return
        else:
            presets = []
            for preset in ViewportPlayblast.RESOLUTION_LOOKUP.keys():
                presets.append("'{0}'".format(preset))

            self.log_error(
                "Invalid resoluton: {0}. Expected one of [int, int], {1}".format(
                    widthHeight, ", ".join(presets)
                )
            )
            return

        self._widthHeight = (widthHeight[0], widthHeight[1])

    def get_resolution_width_height(self):
        """Get the current resolution as (width, height)."""
        if self._resolution_preset:
            return self.preset_to_resolution(self._resolution_preset)

        return self._widthHeight

    def preset_to_resolution(self, resolution_preset):
        """Convert a resolution preset to (width, height)."""
        if resolution_preset == "Render":
            width = cmds.getAttr("defaultResolution.width")
            height = cmds.getAttr("defaultResolution.height")
            return (width, height)
        elif resolution_preset in ViewportPlayblast.RESOLUTION_LOOKUP.keys():
            return ViewportPlayblast.RESOLUTION_LOOKUP[resolution_preset]
        else:
            raise RuntimeError(
                "Invalid resolution preset: {0}".format(resolution_preset)
            )

    def set_frame_range(self, frame_range):
        """Set the frame range for playblast."""
        resolved_frame_range = self.resolve_frame_range(frame_range)
        if not resolved_frame_range:
            return

        self._frame_range_preset = None
        if frame_range in ViewportPlayblast.FRAME_RANGE_PRESETS:
            self._frame_range_preset = frame_range

        self._start_frame = resolved_frame_range[0]
        self._end_frame = resolved_frame_range[1]

    def get_start_end_frame(self):
        """Get the current frame range as (start, end)."""
        if self._frame_range_preset:
            return self.preset_to_frame_range(self._frame_range_preset)

        return (self._start_frame, self._end_frame)

    def resolve_frame_range(self, frame_range):
        """Resolve a frame range input to (start, end)."""
        try:
            if type(frame_range) in [list, tuple]:
                start_frame = frame_range[0]
                end_frame = frame_range[1]
            else:
                start_frame, end_frame = self.preset_to_frame_range(frame_range)

            return (start_frame, end_frame)

        except:
            presets = []
            for preset in ViewportPlayblast.FRAME_RANGE_PRESETS:
                presets.append("'{0}'".format(preset))
            self.log_error(
                "Invalid frame range. Expected one of (start_frame, end_frame), {0}".format(
                    ", ".join(presets)
                )
            )

        return None

    def preset_to_frame_range(self, frame_range_preset):
        """Convert a frame range preset to (start, end)."""
        if frame_range_preset == "Render":
            start_frame = int(cmds.getAttr("defaultRenderGlobals.startFrame"))
            end_frame = int(cmds.getAttr("defaultRenderGlobals.endFrame"))
        elif frame_range_preset == "Playback":
            start_frame = int(cmds.playbackOptions(q=True, minTime=True))
            end_frame = int(cmds.playbackOptions(q=True, maxTime=True))
        elif frame_range_preset == "Animation":
            start_frame = int(cmds.playbackOptions(q=True, animationStartTime=True))
            end_frame = int(cmds.playbackOptions(q=True, animationEndTime=True))
        else:
            raise RuntimeError(
                "Invalid frame range preset: {0}".format(frame_range_preset)
            )

        return (start_frame, end_frame)

    def set_visibility(self, visibility_data):
        """Set the visibility settings."""
        if not visibility_data:
            visibility_data = []

        if not type(visibility_data) in [list, tuple]:
            visibility_data = self.preset_to_visibility(visibility_data)

            if visibility_data is None:
                return

        self._visibility = copy.copy(visibility_data)

    def get_visibility(self):
        """Get the current visibility settings."""
        if not self._visibility:
            return self.get_viewport_visibility()

        return self._visibility

    def preset_to_visibility(self, visibility_preset):
        """Convert a visibility preset to visibility data."""
        if (
            not visibility_preset
            in ViewportPlayblast.VIEWPORT_VISIBILITY_PRESETS.keys()
        ):
            self.log_error("Invaild visibility preset: {0}".format(visibility_preset))
            return None

        visibility_data = []

        preset_names = ViewportPlayblast.VIEWPORT_VISIBILITY_PRESETS[visibility_preset]
        if preset_names:
            for lookup_item in ViewportPlayblast.VIEWPORT_VISIBILITY_LOOKUP:
                visibility_data.append(lookup_item[0] in preset_names)

        return visibility_data

    def get_viewport_visibility(self):
        """Get the current viewport visibility settings."""
        model_panel = self.get_viewport_panel()
        if not model_panel:
            self.log_error(
                "Failed to get viewport visibility. A viewport is not active."
            )
            return None

        return self._visibility_manager.get_viewport_visibility(model_panel)

    def set_viewport_visibility(self, model_editor, visibility_flags):
        """Apply visibility flags to the viewport."""
        self._visibility_manager.set_viewport_visibility(model_editor, visibility_flags)

    def create_viewport_visibility_flags(self, visibility_data):
        """Create visibility flags dictionary from data."""
        return self._visibility_manager.create_viewport_visibility_flags(
            visibility_data
        )

    def set_encoding(self, container_format, encoder):
        """Set the encoding format and codec."""
        if container_format not in ViewportPlayblast.VIDEO_ENCODER_LOOKUP.keys():
            self.log_error(
                "Invalid container: {0}. Expected one of {1}".format(
                    container_format, ViewportPlayblast.VIDEO_ENCODER_LOOKUP.keys()
                )
            )
            return

        if encoder not in ViewportPlayblast.VIDEO_ENCODER_LOOKUP[container_format]:
            self.log_error(
                "Invalid encoder: {0}. Expected one of {1}".format(
                    encoder, ViewportPlayblast.VIDEO_ENCODER_LOOKUP[container_format]
                )
            )
            return

        self._container_format = container_format
        self._encoder_name = encoder

    def set_h264_settings(self, quality, preset):
        """Set H.264 encoding settings."""
        if not quality in ViewportPlayblast.H264_QUALITIES.keys():
            self.log_error(
                "Invalid h264 quality: {0}. Expected one of {1}".format(
                    quality, ViewportPlayblast.H264_QUALITIES.keys()
                )
            )
            return

        if not preset in ViewportPlayblast.H264_PRESETS:
            self.log_error(
                "Invalid h264 preset: {0}. Expected one of {1}".format(
                    preset, ViewportPlayblast.H264_PRESETS
                )
            )
            return

        self._h264_quality = quality
        self._h264_preset = preset

    def get_h264_settings(self):
        """Get H.264 encoding settings."""
        return {
            "quality": self._h264_quality,
            "preset": self._h264_preset,
        }

    def set_image_settings(self, quality):
        """Set image quality settings."""
        if quality > 0 and quality <= 100:
            self._image_quality = quality
        else:
            self.log_error("Invalid image quality: {0}. Expected value between 1-100")

    def get_image_settings(self):
        """Get image quality settings."""
        return {
            "quality": self._image_quality,
        }

    def execute(
        self,
        output_dir,
        filename,
        padding=4,
        overscan=False,
        show_ornaments=True,
        show_in_viewer=True,
        overwrite=False,
    ):
        """Execute the playblast."""
        if self.requires_ffmpeg and not self.validate_ffmpeg():
            self.log_error(
                "ffmpeg executable is not configured. See script editor for details."
            )
            return

        if not output_dir:
            self.log_error("Output directory path not set")
            return
        if not filename:
            self.log_error("Output file name not set")
            return

        output_dir = self.resolve_output_directory_path(output_dir)
        filename = self.resolve_output_filename(filename)

        if padding <= 0:
            padding = ViewportPlayblast.DEFAULT_PADDING

        if self.requires_ffmpeg:
            output_path = os.path.normpath(
                os.path.join(
                    output_dir, "{0}.{1}".format(filename, self._container_format)
                )
            )
            if not overwrite and os.path.exists(output_path):
                self.log_error(
                    "Output file already exists. Enable overwrite to ignore."
                )
                return

            playblast_output_dir = "{0}/playblast_temp".format(output_dir)
            playblast_output = os.path.normpath(
                os.path.join(playblast_output_dir, filename)
            )
            force_overwrite = True
            compression = "png"
            image_quality = 100
            index_from_zero = True
            viewer = False
        else:
            playblast_output = os.path.normpath(os.path.join(output_dir, filename))
            force_overwrite = overwrite
            compression = self._encoder_name
            image_quality = self._image_quality
            index_from_zero = False
            viewer = show_in_viewer

        widthHeight = self.get_resolution_width_height()
        start_frame, end_frame = self.get_start_end_frame()

        options = {
            "filename": playblast_output,
            "widthHeight": widthHeight,
            "percent": 100,
            "startTime": start_frame,
            "endTime": end_frame,
            "clearCache": True,
            "forceOverwrite": force_overwrite,
            "format": "image",
            "compression": compression,
            "quality": image_quality,
            "indexFromZero": index_from_zero,
            "framePadding": padding,
            "showOrnaments": show_ornaments,
            "viewer": viewer,
        }

        self.log_output("Playblast options: {0}".format(options))

        viewport_model_panel = self.get_viewport_panel()
        if not viewport_model_panel:
            return

        model_editor = cmds.modelPanel(viewport_model_panel, q=True, modelEditor=True)
        if not model_editor:
            self.log_error("Failed to get model editor from viewport.")
            return

        orig_camera = self.get_active_camera()
        if not orig_camera:
            self.log_error(
                "Could not get camera from viewport. Please click in a viewport."
            )
            return

        camera = self._camera
        if not camera:
            camera = orig_camera

        if camera not in cmds.listCameras():
            self.log_error("Camera does not exist: {0}".format(camera))
            return

        if camera != orig_camera:
            self.set_active_camera(camera)

        orig_visibility_flags = self.create_viewport_visibility_flags(
            self.get_viewport_visibility()
        )
        playblast_visibility_flags = self.create_viewport_visibility_flags(
            self.get_visibility()
        )
        self.set_viewport_visibility(model_editor, playblast_visibility_flags)

        if not overscan:
            overscan_attr = "{0}.overscan".format(camera)
            orig_overscan = cmds.getAttr(overscan_attr)
            cmds.setAttr(overscan_attr, 1.0)

        playblast_failed = False
        try:
            cmds.playblast(**options)
            self.log_output(
                "Playblast created in the selected output directory: {0}.".format(
                    output_dir
                )
            )
        except:
            traceback.print_exc()
            self.log_error("Failed to create playblast. See script editor for details.")
            playblast_failed = True
        finally:
            if not overscan:
                cmds.setAttr(overscan_attr, orig_overscan)
            self.set_viewport_visibility(model_editor, orig_visibility_flags)
            if camera != orig_camera:
                self.set_active_camera(orig_camera)

        if playblast_failed:
            return

        if self._container_format in ["mov", "mp4"]:
            source_path = "{0}/{1}.%0{2}d.png".format(
                playblast_output_dir, filename, padding
            )

            if self._encoder_name == "h264":
                self.encode_h264(source_path, output_path, start_frame)
            else:
                self.log_error(
                    "Encoding failed. Unsupported encoder ({0}) for container ({1}).".format(
                        self._encoder_name, self._container_format
                    )
                )
                self.remove_temp_dir(playblast_output_dir)
                return

            self.remove_temp_dir(playblast_output_dir)

            if show_in_viewer:
                self.open_in_viewer(output_path)

            self.send_completion_notification(output_path)
            self.open_output_folder(output_path)

        else:
            self.open_output_folder(playblast_output)

    def remove_temp_dir(self, temp_dir_path):
        """Remove temporary directory and its contents."""
        temp_dir_path = os.path.normpath(temp_dir_path)
        playblast_dir = QtCore.QDir(temp_dir_path)
        playblast_dir.setNameFilters(["*.png"])
        playblast_dir.setFilter(QtCore.QDir.Files)
        for f in playblast_dir.entryList():
            playblast_dir.remove(f)

        if not playblast_dir.rmdir(temp_dir_path):
            try:
                if os.path.exists(temp_dir_path):
                    shutil.rmtree(temp_dir_path, ignore_errors=True)
                    self.log_output(
                        "Removed temporary directory (fallback): {0}".format(
                            temp_dir_path
                        )
                    )
            except Exception as e:
                self.log_warning(
                    "Failed to remove temporary directory: {0}".format(str(e))
                )

    def open_in_viewer(self, path):
        """Open the output file in the default viewer."""
        if not os.path.exists(path):
            self.log_error(
                "Failed to open in viewer. File does not exist: {0}".format(path)
            )
            return

        if self._container_format in ("mov", "mp4") and cmds.optionVar(
            exists="PlayblastCmdQuicktime"
        ):
            executable_path = cmds.optionVar(q="PlayblastCmdQuicktime")
            if executable_path:
                QtCore.QProcess.startDetached(executable_path, [path])
                return

        QtCore.QProcess.startDetached("xdg-open", [path])

    def validate_ffmpeg(self):
        """Validate the FFmpeg installation."""
        return self._encoder.validate_ffmpeg()

    def requires_ffmpeg(self):
        """Check if FFmpeg is required."""
        return self._container_format != "Image"

    def encode_h264(self, source_path, output_path, start_frame):
        """Encode image sequence to H.264 video."""
        framerate = self.get_frame_rate()

        audio_file_path, audio_frame_offset = self.get_audio_attributes()
        audio_offset = 0
        if audio_file_path:
            audio_offset = self.get_audio_offset_in_sec(
                start_frame, audio_frame_offset, framerate
            )

        crf = ViewportPlayblast.H264_QUALITIES[self._h264_quality]
        preset = self._h264_preset

        self._encoder.encode_h264(
            source_path,
            output_path,
            framerate,
            crf,
            preset,
            audio_file_path,
            audio_offset,
        )

    def get_frame_rate(self):
        """Get the current Maya frame rate."""
        rate_str = cmds.currentUnit(q=True, time=True)

        if rate_str == "game":
            frame_rate = 15.0
        elif rate_str == "film":
            frame_rate = 24.0
        elif rate_str == "pal":
            frame_rate = 25.0
        elif rate_str == "ntsc":
            frame_rate = 30.0
        elif rate_str == "show":
            frame_rate = 48.0
        elif rate_str == "palf":
            frame_rate = 50.0
        elif rate_str == "ntscf":
            frame_rate = 60.0
        elif rate_str.endswith("fps"):
            frame_rate = float(rate_str[0:-3])
        else:
            raise RuntimeError("Unsupported frame rate: {0}".format(rate_str))

        return frame_rate

    def get_audio_attributes(self):
        """Get audio attributes from Maya timeline."""
        sound_node = mel.eval("timeControl -q -sound $gPlayBackSlider;")
        if sound_node:
            file_path = cmds.getAttr("{0}.filename".format(sound_node))
            file_info = QtCore.QFileInfo(file_path)
            if file_info.exists():
                offset = cmds.getAttr("{0}.offset".format(sound_node))
                return (file_path, offset)

        return (None, None)

    def get_audio_offset_in_sec(self, start_frame, audio_frame_offset, frame_rate):
        """Convert audio offset from frames to seconds."""
        return (start_frame - audio_frame_offset) / frame_rate

    def resolve_output_directory_path(self, dir_path):
        """Resolve output directory path with placeholders."""
        # Normalize path separators for Linux
        dir_path = dir_path.replace("\\", "/")

        if "<Show>" in dir_path:
            dir_path = dir_path.replace("<Show>", self.get_project_dir_path())

        return dir_path

    def resolve_output_filename(self, filename):
        """Resolve output filename with placeholders."""
        if "<Scene>" in filename:
            filename = filename.replace("<Scene>", self.get_scene_name())

        return filename

    def get_project_dir_path(self):
        """Get Maya project directory path."""
        return cmds.workspace(q=True, rootDirectory=True)

    def get_scene_name(self):
        """Get current Maya scene name."""
        scene_name = cmds.file(q=True, sceneName=True, shortName=True)
        if scene_name:
            scene_name = os.path.splitext(scene_name)[0]
        else:
            scene_name = "untitled"

        return scene_name

    def _is_model_panel(self, panel):
        """Check if a panel is a valid 3D viewport."""
        try:
            return cmds.modelPanel(panel, q=True, exists=True)
        except:
            return False

    def _get_all_viewports(self):
        """Get all 3D viewport panels."""
        return cmds.getPanel(type="modelPanel") or []

    def get_viewport_panel(self):
        """Get the appropriate viewport panel."""
        # If camera is selected, then return any viewport
        if self._camera:
            viewports = self._get_all_viewports()
            if viewports:
                # Return first valid viewport
                for panel in viewports:
                    if self._is_model_panel(panel):
                        return panel
                return viewports[0]  # Fallback
            else:
                self.log_error("No viewport found for camera: {0}".format(self._camera))
                return None

        # If no camera, then return focused viewport
        focused = cmds.getPanel(withFocus=True)
        if focused and self._is_model_panel(focused):
            return focused

        # If no camera and no focused panel, then error
        viewports = self._get_all_viewports()
        if viewports:
            self.log_error("No camera selected and no viewport has focus.")
            self.log_warning("Please either:")
            self.log_warning("> Select a camera from the dropdown")
            self.log_warning("> Click in a 3D viewport")
        else:
            self.log_error("No viewport found in the scene.")

        return None

    def get_active_camera(self):
        """Get the camera from the active viewport."""
        model_panel = self.get_viewport_panel()
        if not model_panel:
            return None

        try:
            camera = cmds.modelPanel(model_panel, q=True, camera=True)
            if camera and camera in cmds.listCameras():
                return camera
        except:
            pass

        # Fallback: get first available camera
        cameras = cmds.listCameras()
        if cameras:
            self.log_warning(
                "Could not get camera from viewport. Using: {0}".format(cameras[0])
            )
            return cameras[0]

        self.log_error("No cameras found in the scene.")
        return None

    def set_active_camera(self, camera):
        """Set the active viewport camera."""
        model_panel = self.get_viewport_panel()
        if model_panel:
            mel.eval("lookThroughModelPanel {0} {1}".format(camera, model_panel))
        else:
            self.log_error("Failed to set active camera. A viewport is not active.")

    def log_error(self, text):
        """Log an error message."""
        if self._log_to_maya:
            om.MGlobal.displayError("[ViewportPlayblast] {0}".format(text))

        self.output_logged.emit("[ERROR] {0}".format(text))

    def log_warning(self, text):
        """Log a warning message."""
        if self._log_to_maya:
            om.MGlobal.displayWarning("[ViewportPlayblast] {0}".format(text))

        self.output_logged.emit("[WARNING] {0}".format(text))

    def log_output(self, text):
        """Log an info message."""
        if self._log_to_maya:
            om.MGlobal.displayInfo(text)

        self.output_logged.emit(text)

    def open_output_folder(self, path):
        """Open the output folder in file browser."""

        folder_path = os.path.dirname(path)

        if not os.path.exists(folder_path):
            self.log_error("Output folder does not exist: {0}".format(folder_path))
            return

        try:
            subprocess.Popen(["xdg-open", folder_path])
            self.log_output("Opened folder: {0}".format(folder_path))
        except Exception as e:
            self.log_error("Failed to open folder: {0}".format(str(e)))

    def send_completion_notification(self, output_path):
        """Send notification when playblast is complete."""
        try:
            subprocess.Popen(
                [
                    "notify-send",
                    "Viewport Playblast Complete",
                    "Output saved to: {0}".format(output_path),
                    "-i",
                    "video-x-generic",
                    "-t",
                    "10000",
                ]
            )
            self.log_output("Desktop notification sent")
        except Exception as e:
            self.log_warning("Failed to send desktop notification: {0}".format(str(e)))
