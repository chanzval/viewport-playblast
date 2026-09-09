"""
FFmpeg encoding functionality.
"""

import os
import sys

from PySide2 import QtCore


class FFmpegEncoder(QtCore.QObject):
    """Handle FFmpeg encoding operations."""

    output_logged = QtCore.Signal(str)

    def __init__(self, ffmpeg_path=None):
        super(FFmpegEncoder, self).__init__()
        self._ffmpeg_path = ffmpeg_path or "/usr/bin/ffmpeg"
        self._process = None
        self._initialize_process()

    def set_ffmpeg_path(self, ffmpeg_path):
        """Set the FFmpeg executable path."""
        if ffmpeg_path:
            self._ffmpeg_path = ffmpeg_path
        else:
            self._ffmpeg_path = "/usr/bin/ffmpeg"

    def get_ffmpeg_path(self):
        """Get the FFmpeg executable path."""
        return self._ffmpeg_path

    def _initialize_process(self):
        """Initialize the FFmpeg QProcess."""
        self._process = QtCore.QProcess()
        self._process.readyReadStandardError.connect(self._process_output)

    def _process_output(self):
        """Process FFmpeg output."""
        byte_array_output = self._process.readAllStandardError()

        if sys.version_info.major < 3:
            output = str(byte_array_output)
        else:
            output = str(byte_array_output, "utf-8")

        self.output_logged.emit(output)

    def execute_ffmpeg_command(self, command):
        """Execute an FFmpeg command."""
        # Split command for Linux argument handling
        parts = command.split()
        program = parts[0]
        arguments = parts[1:]

        self._process.start(program, arguments)
        if self._process.waitForStarted():
            while self._process.state() != QtCore.QProcess.NotRunning:
                QtCore.QCoreApplication.processEvents()
                QtCore.QThread.usleep(10)

    def validate_ffmpeg(self):
        """Validate the FFmpeg installation."""
        if not self._ffmpeg_path:
            self.output_logged.emit("[ERROR] ffmpeg executable path not set")
            return False
        elif not os.path.exists(self._ffmpeg_path):
            self.output_logged.emit(
                "[ERROR] ffmpeg executable path does not exist: {0}".format(
                    self._ffmpeg_path
                )
            )
            return False
        elif os.path.isdir(self._ffmpeg_path):
            self.output_logged.emit(
                "[ERROR] Invalid ffmpeg path: {0}".format(self._ffmpeg_path)
            )
            return False

        # Linux-specific: Check if file is executable
        if not os.access(self._ffmpeg_path, os.X_OK):
            self.output_logged.emit(
                "[ERROR] ffmpeg is not executable: {0}".format(self._ffmpeg_path)
            )
            return False

        return True

    def encode_h264(
        self,
        source_path,
        output_path,
        framerate,
        crf,
        preset,
        audio_file_path=None,
        audio_offset=0,
    ):
        """Encode image sequence to H.264 video."""
        # Build command as a list for proper argument handling on Linux
        cmd_parts = [
            self._ffmpeg_path,
            "-y",
            "-framerate",
            str(framerate),
            "-i",
            source_path,
        ]

        if audio_file_path:
            cmd_parts.extend(["-ss", str(audio_offset), "-i", audio_file_path])

        cmd_parts.extend(
            [
                "-c:v",
                "libx264",
                "-crf:v",
                str(crf),
                "-preset:v",
                preset,
                "-profile:v",
                "high",
                "-level:v",
                "4.0",
                "-pix_fmt",
                "yuv420p",
            ]
        )

        if audio_file_path:
            cmd_parts.extend(["-filter_complex", "[1:0] apad", "-shortest"])

        cmd_parts.append(output_path)

        cmd_string = " ".join(cmd_parts)
        self.output_logged.emit(cmd_string)

        self.execute_ffmpeg_command(cmd_string)
