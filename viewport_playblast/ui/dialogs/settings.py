"""
Settings dialog for Viewport Playblast.
"""

from PySide2 import QtCore
from PySide2 import QtWidgets


class ViewportPlayblastSettingsDialog(QtWidgets.QDialog):
    """Settings dialog for FFmpeg path."""

    def __init__(self, parent):
        super(ViewportPlayblastSettingsDialog, self).__init__(parent)

        self.setWindowTitle("Settings")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(360)
        self.setModal(True)

        self.ffmpeg_path_le = QtWidgets.QLineEdit()
        self.ffmpeg_path_select_btn = QtWidgets.QPushButton("...")
        self.ffmpeg_path_select_btn.setFixedSize(24, 19)
        self.ffmpeg_path_select_btn.clicked.connect(self.select_ffmpeg_executable)

        ffmpeg_layout = QtWidgets.QHBoxLayout()
        ffmpeg_layout.setSpacing(4)
        ffmpeg_layout.addWidget(self.ffmpeg_path_le)
        ffmpeg_layout.addWidget(self.ffmpeg_path_select_btn)

        ffmpeg_grp = QtWidgets.QGroupBox("FFmpeg Path")
        ffmpeg_grp.setLayout(ffmpeg_layout)

        self.accept_btn = QtWidgets.QPushButton("Accept")
        self.accept_btn.clicked.connect(self.accept)

        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.accept_btn)
        button_layout.addWidget(self.cancel_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        main_layout.addWidget(ffmpeg_grp)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

    def set_ffmpeg_path(self, path):
        """Set FFmpeg path in the line edit."""
        self.ffmpeg_path_le.setText(path)

    def get_ffmpeg_path(self):
        """Get FFmpeg path from the line edit."""
        return self.ffmpeg_path_le.text()

    def select_ffmpeg_executable(self):
        """Open file dialog to select FFmpeg executable."""
        current_path = self.ffmpeg_path_le.text()

        new_path = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select FFmpeg Executable", current_path
        )[0]
        if new_path:
            self.ffmpeg_path_le.setText(new_path)
