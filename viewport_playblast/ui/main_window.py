"""
Main UI window for Viewport Playblast.
"""

import os
import sys

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

from ..core.playblast import ViewportPlayblast
from .dialogs.settings import ViewportPlayblastSettingsDialog
from .dialogs.encoder import ViewportPlayblastEncoderSettingsDialog
from .dialogs.visibility import ViewportPlayblastVisibilityDialog


class ViewportPlayblastUi(QtWidgets.QDialog):
    """Main UI dialog for Viewport Playblast."""

    TITLE = "Viewport Playblast"

    CONTAINER_PRESETS = [
        "mov",
        "mp4",
        "Image",
    ]

    RESOLUTION_PRESETS = [
        "Render",
        "HD 1080",
        "HD 720",
        "HD 540",
    ]

    VISIBILITY_PRESETS = [
        "Viewport",
        "Geo",
        "Dynamics",
    ]

    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        """Show the dialog using singleton pattern."""
        if not cls.dlg_instance:
            cls.dlg_instance = ViewportPlayblastUi()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self):
        # Get Maya main window (Python 2/3 compatible)
        if sys.version_info.major < 3:
            maya_main_window = wrapInstance(
                long(omui.MQtUtil.mainWindow()), QtWidgets.QWidget
            )
        else:
            maya_main_window = wrapInstance(
                int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget
            )

        super(ViewportPlayblastUi, self).__init__(maya_main_window)

        self.setWindowTitle(ViewportPlayblastUi.TITLE)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(500)

        self._playblast = ViewportPlayblast()

        self._settings_dialog = None
        self._encoder_settings_dialog = None
        self._visibility_dialog = None

        self.load_settings()

        self.create_actions()
        self.create_menus()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.load_defaults()

        self.append_output("Viewport Playblast v{0}".format(ViewportPlayblast.VERSION))

    def create_actions(self):
        """Create menu actions."""
        self.save_defaults_action = QtWidgets.QAction("Save Defaults", self)
        self.save_defaults_action.triggered.connect(self.save_defaults)

        self.load_defaults_action = QtWidgets.QAction("Load Defaults", self)
        self.load_defaults_action.triggered.connect(self.load_defaults)

        self.show_settings_action = QtWidgets.QAction("Settings...", self)
        self.show_settings_action.triggered.connect(self.show_settings_dialog)

        self.show_about_action = QtWidgets.QAction("About", self)
        self.show_about_action.triggered.connect(self.show_about_dialog)

    def create_menus(self):
        """Create menu bar."""
        self.main_menu = QtWidgets.QMenuBar()

        edit_menu = self.main_menu.addMenu("Edit")
        edit_menu.addAction(self.save_defaults_action)
        edit_menu.addAction(self.load_defaults_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.show_settings_action)

        help_menu = self.main_menu.addMenu("Help")
        help_menu.addAction(self.show_about_action)

    def create_widgets(self):
        """Create UI widgets."""
        self.output_dir_path_le = QtWidgets.QLineEdit()
        self.output_dir_path_le.setPlaceholderText("<Show>/movies")

        self.output_dir_path_select_btn = QtWidgets.QPushButton("...")
        self.output_dir_path_select_btn.setFixedSize(24, 19)
        self.output_dir_path_select_btn.setToolTip("Select Output Directory")

        self.output_dir_path_show_btn = QtWidgets.QPushButton()
        self.output_dir_path_show_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.output_dir_path_show_btn.setFixedSize(24, 19)
        self.output_dir_path_show_btn.setToolTip("Open Output Folder")

        self.output_filename_le = QtWidgets.QLineEdit()
        self.output_filename_le.setPlaceholderText("<Scene>")
        self.output_filename_le.setMaximumWidth(200)
        self.force_overwrite_cb = QtWidgets.QCheckBox("Force overwrite")

        self.resolution_select_cmb = QtWidgets.QComboBox()
        self.resolution_select_cmb.addItems(ViewportPlayblastUi.RESOLUTION_PRESETS)
        self.resolution_select_cmb.addItem("Custom")
        self.resolution_select_cmb.setCurrentText(ViewportPlayblast.DEFAULT_RESOLUTION)

        self.resolution_width_sb = QtWidgets.QSpinBox()
        self.resolution_width_sb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)
        self.resolution_width_sb.setRange(1, 9999)
        self.resolution_width_sb.setMinimumWidth(40)
        self.resolution_width_sb.setAlignment(QtCore.Qt.AlignRight)
        self.resolution_height_sb = QtWidgets.QSpinBox()
        self.resolution_height_sb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)
        self.resolution_height_sb.setRange(1, 9999)
        self.resolution_height_sb.setMinimumWidth(40)
        self.resolution_height_sb.setAlignment(QtCore.Qt.AlignRight)

        self.camera_select_cmb = QtWidgets.QComboBox()
        self.camera_select_hide_defaults_cb = QtWidgets.QCheckBox("Hide defaults")
        self.refresh_cameras()

        self.frame_range_cmb = QtWidgets.QComboBox()
        self.frame_range_cmb.addItems(ViewportPlayblast.FRAME_RANGE_PRESETS)
        self.frame_range_cmb.addItem("Custom")
        self.frame_range_cmb.setCurrentText(ViewportPlayblast.DEFAULT_FRAME_RANGE)

        self.frame_range_start_sb = QtWidgets.QSpinBox()
        self.frame_range_start_sb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)
        self.frame_range_start_sb.setRange(-9999, 9999)
        self.frame_range_start_sb.setMinimumWidth(40)
        self.frame_range_start_sb.setAlignment(QtCore.Qt.AlignRight)

        self.frame_range_end_sb = QtWidgets.QSpinBox()
        self.frame_range_end_sb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)
        self.frame_range_end_sb.setRange(-9999, 9999)
        self.frame_range_end_sb.setMinimumWidth(40)
        self.frame_range_end_sb.setAlignment(QtCore.Qt.AlignRight)

        self.encoding_container_cmb = QtWidgets.QComboBox()
        self.encoding_container_cmb.addItems(ViewportPlayblastUi.CONTAINER_PRESETS)
        self.encoding_container_cmb.setCurrentText(ViewportPlayblast.DEFAULT_CONTAINER)

        self.encoding_video_codec_cmb = QtWidgets.QComboBox()
        self.encoding_video_codec_settings_btn = QtWidgets.QPushButton("Settings...")
        self.encoding_video_codec_settings_btn.setFixedHeight(19)

        self.visibility_cmb = QtWidgets.QComboBox()
        self.visibility_cmb.addItems(ViewportPlayblastUi.VISIBILITY_PRESETS)
        self.visibility_cmb.addItem("Custom")
        self.visibility_cmb.setCurrentText(ViewportPlayblast.DEFAULT_VISIBILITY)

        self.visibility_customize_btn = QtWidgets.QPushButton("Customize...")
        self.visibility_customize_btn.setFixedHeight(19)

        self.overscan_cb = QtWidgets.QCheckBox()
        self.overscan_cb.setChecked(False)

        self.ornaments_cb = QtWidgets.QCheckBox()
        self.ornaments_cb.setChecked(True)

        self.viewer_cb = QtWidgets.QCheckBox()
        self.viewer_cb.setChecked(True)

        self.output_edit = QtWidgets.QPlainTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setWordWrapMode(QtGui.QTextOption.NoWrap)

        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.clear_btn = QtWidgets.QPushButton("Clear")
        self.playblast_btn = QtWidgets.QPushButton("Playblast")
        self.close_btn = QtWidgets.QPushButton("Close")

    def create_layout(self):
        """Create UI layout."""
        output_path_layout = QtWidgets.QHBoxLayout()
        output_path_layout.setSpacing(4)
        output_path_layout.addWidget(self.output_dir_path_le)
        output_path_layout.addWidget(self.output_dir_path_select_btn)
        output_path_layout.addWidget(self.output_dir_path_show_btn)

        output_file_layout = QtWidgets.QHBoxLayout()
        output_file_layout.setSpacing(4)
        output_file_layout.addWidget(self.output_filename_le)
        output_file_layout.addWidget(self.force_overwrite_cb)

        output_layout = QtWidgets.QFormLayout()
        output_layout.setSpacing(4)
        output_layout.addRow("Directory:", output_path_layout)
        output_layout.addRow("Filename:", output_file_layout)

        output_grp = QtWidgets.QGroupBox("Output")
        output_grp.setLayout(output_layout)

        camera_options_layout = QtWidgets.QHBoxLayout()
        camera_options_layout.setSpacing(4)
        camera_options_layout.addWidget(self.camera_select_cmb)
        camera_options_layout.addWidget(self.camera_select_hide_defaults_cb)

        resolution_layout = QtWidgets.QHBoxLayout()
        resolution_layout.setSpacing(4)
        resolution_layout.addWidget(self.resolution_select_cmb)
        resolution_layout.addWidget(self.resolution_width_sb)
        resolution_layout.addWidget(QtWidgets.QLabel("x"))
        resolution_layout.addWidget(self.resolution_height_sb)

        frame_range_layout = QtWidgets.QHBoxLayout()
        frame_range_layout.setSpacing(4)
        frame_range_layout.addWidget(self.frame_range_cmb)
        frame_range_layout.addWidget(self.frame_range_start_sb)
        frame_range_layout.addWidget(self.frame_range_end_sb)

        encoding_layout = QtWidgets.QHBoxLayout()
        encoding_layout.setSpacing(4)
        encoding_layout.addWidget(self.encoding_container_cmb)
        encoding_layout.addWidget(self.encoding_video_codec_cmb)
        encoding_layout.addWidget(self.encoding_video_codec_settings_btn)

        visibility_layout = QtWidgets.QHBoxLayout()
        visibility_layout.setSpacing(4)
        visibility_layout.addWidget(self.visibility_cmb)
        visibility_layout.addWidget(self.visibility_customize_btn)

        options_layout = QtWidgets.QFormLayout()
        options_layout.addRow("Camera:", camera_options_layout)
        options_layout.addRow("Resolution:", resolution_layout)
        options_layout.addRow("Frame Range:", frame_range_layout)
        options_layout.addRow("Encoding:", encoding_layout)
        options_layout.addRow("Visiblity:", visibility_layout)
        options_layout.addRow("Overscan:", self.overscan_cb)
        options_layout.addRow("Ornaments:", self.ornaments_cb)
        options_layout.addRow("Show in Viewer:", self.viewer_cb)

        options_grp = QtWidgets.QGroupBox("Options")
        options_grp.setLayout(options_layout)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.playblast_btn)
        button_layout.addWidget(self.close_btn)

        status_bar_layout = QtWidgets.QHBoxLayout()
        status_bar_layout.addStretch()
        status_bar_layout.addWidget(
            QtWidgets.QLabel("v{0}".format(ViewportPlayblast.VERSION))
        )

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        main_layout.setMenuBar(self.main_menu)
        main_layout.addWidget(output_grp)
        main_layout.addWidget(options_grp)
        main_layout.addWidget(self.output_edit)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(status_bar_layout)

    def create_connections(self):
        """Create signal-slot connections."""
        self.output_dir_path_select_btn.clicked.connect(self.select_output_directory)
        self.output_dir_path_show_btn.clicked.connect(self.open_output_folder)

        self.camera_select_cmb.currentTextChanged.connect(self.on_camera_changed)
        self.camera_select_hide_defaults_cb.toggled.connect(self.refresh_cameras)

        self.frame_range_cmb.currentTextChanged.connect(self.refresh_frame_range)
        self.frame_range_start_sb.editingFinished.connect(self.on_frame_range_changed)
        self.frame_range_end_sb.editingFinished.connect(self.on_frame_range_changed)

        self.encoding_container_cmb.currentTextChanged.connect(
            self.refresh_video_encoders
        )
        self.encoding_video_codec_cmb.currentTextChanged.connect(
            self.on_video_encoder_changed
        )
        self.encoding_video_codec_settings_btn.clicked.connect(
            self.show_encoder_settings_dialog
        )

        self.resolution_select_cmb.currentTextChanged.connect(self.refresh_resolution)
        self.resolution_width_sb.editingFinished.connect(self.on_resolution_changed)
        self.resolution_height_sb.editingFinished.connect(self.on_resolution_changed)

        self.visibility_cmb.currentTextChanged.connect(
            self.on_visibility_preset_changed
        )
        self.visibility_customize_btn.clicked.connect(self.show_visibility_dialog)

        self.refresh_btn.clicked.connect(self.refresh)
        self.clear_btn.clicked.connect(self.output_edit.clear)
        self.playblast_btn.clicked.connect(self.do_playblast)
        self.close_btn.clicked.connect(self.close)

        self._playblast.output_logged.connect(self.append_output)

    def do_playblast(self):
        """Execute the playblast."""
        output_dir_path = self.output_dir_path_le.text()
        if not output_dir_path:
            output_dir_path = self.output_dir_path_le.placeholderText()

        filename = self.output_filename_le.text()
        if not filename:
            filename = self.output_filename_le.placeholderText()

        padding = ViewportPlayblast.DEFAULT_PADDING

        overscan = self.overscan_cb.isChecked()
        show_ornaments = self.ornaments_cb.isChecked()
        show_in_viewer = self.viewer_cb.isChecked()
        overwrite = self.force_overwrite_cb.isChecked()

        self._playblast.execute(
            output_dir_path,
            filename,
            padding,
            overscan,
            show_ornaments,
            show_in_viewer,
            overwrite,
        )

    def select_output_directory(self):
        """Select output directory."""
        current_dir_path = self.output_dir_path_le.text()
        if not current_dir_path:
            current_dir_path = self.output_dir_path_le.placeholderText()

        current_dir_path = self._playblast.resolve_output_directory_path(
            current_dir_path
        )

        file_info = QtCore.QFileInfo(current_dir_path)
        if not file_info.exists():
            current_dir_path = self._playblast.get_project_dir_path()

        new_dir_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", current_dir_path
        )
        if new_dir_path:
            self.output_dir_path_le.setText(new_dir_path)

    def open_output_folder(self):
        """Open the output folder in file browser."""
        output_dir_path = self.output_dir_path_le.text()
        if not output_dir_path:
            output_dir_path = self.output_dir_path_le.placeholderText()

        output_dir_path = self._playblast.resolve_output_directory_path(output_dir_path)

        if os.path.exists(output_dir_path):
            QtCore.QProcess.startDetached("xdg-open", [output_dir_path])
            self.append_output("Opened folder: {0}".format(output_dir_path))
        else:
            self.append_output(
                "[WARNING] Directory does not exist: {0}".format(output_dir_path)
            )

    def refresh(self):
        """Refresh all UI elements."""
        self.refresh_cameras()
        self.refresh_resolution()
        self.refresh_frame_range()
        self.refresh_video_encoders()

    def refresh_cameras(self):
        """Refresh camera list."""
        current_camera = self.camera_select_cmb.currentText()
        self.camera_select_cmb.clear()

        self.camera_select_cmb.addItem("<Active>")

        cameras = cmds.listCameras()
        if self.camera_select_hide_defaults_cb.isChecked():
            for camera in cameras:
                if camera not in ["front", "persp", "side", "top"]:
                    self.camera_select_cmb.addItem(camera)
        else:
            self.camera_select_cmb.addItems(cameras)

        self.camera_select_cmb.setCurrentText(current_camera)

    def on_camera_changed(self):
        """Handle camera selection change."""
        camera = self.camera_select_cmb.currentText()
        if camera == "<Active>":
            camera = None

        self._playblast.set_camera(camera)

    def refresh_resolution(self):
        """Refresh resolution settings."""
        resolution_preset = self.resolution_select_cmb.currentText()
        if resolution_preset != "Custom":
            self._playblast.set_resolution(resolution_preset)

            resolution = self._playblast.get_resolution_width_height()
            self.resolution_width_sb.setValue(resolution[0])
            self.resolution_height_sb.setValue(resolution[1])

    def on_resolution_changed(self):
        """Handle resolution change."""
        resolution = (
            self.resolution_width_sb.value(),
            self.resolution_height_sb.value(),
        )

        for key in ViewportPlayblast.RESOLUTION_LOOKUP.keys():
            if ViewportPlayblast.RESOLUTION_LOOKUP[key] == resolution:
                self.resolution_select_cmb.setCurrentText(key)
                return

        self.resolution_select_cmb.setCurrentText("Custom")

        self._playblast.set_resolution(resolution)

    def refresh_frame_range(self):
        """Refresh frame range settings."""
        frame_range_preset = self.frame_range_cmb.currentText()
        if frame_range_preset != "Custom":
            frame_range = self._playblast.preset_to_frame_range(frame_range_preset)

            self.frame_range_start_sb.setValue(frame_range[0])
            self.frame_range_end_sb.setValue(frame_range[1])

            self._playblast.set_frame_range(frame_range_preset)

    def on_frame_range_changed(self):
        """Handle frame range change."""
        self.frame_range_cmb.setCurrentText("Custom")

        frame_range = (
            self.frame_range_start_sb.value(),
            self.frame_range_end_sb.value(),
        )
        self._playblast.set_frame_range(frame_range)

    def refresh_video_encoders(self):
        """Refresh video encoder list."""
        self.encoding_video_codec_cmb.clear()

        container = self.encoding_container_cmb.currentText()
        self.encoding_video_codec_cmb.addItems(
            ViewportPlayblast.VIDEO_ENCODER_LOOKUP[container]
        )

    def on_video_encoder_changed(self):
        """Handle video encoder change."""
        container = self.encoding_container_cmb.currentText()
        encoder = self.encoding_video_codec_cmb.currentText()

        if container and encoder:
            self._playblast.set_encoding(container, encoder)

    def show_encoder_settings_dialog(self):
        """Show encoder settings dialog."""
        if not self._encoder_settings_dialog:
            self._encoder_settings_dialog = ViewportPlayblastEncoderSettingsDialog(self)
            self._encoder_settings_dialog.accepted.connect(
                self.on_encoder_settings_dialog_modified
            )

        if self.encoding_container_cmb.currentText() == "Image":
            self._encoder_settings_dialog.set_page("Image")

            image_settings = self._playblast.get_image_settings()
            self._encoder_settings_dialog.set_image_settings(image_settings["quality"])

        else:
            encoder = self.encoding_video_codec_cmb.currentText()
            if encoder == "h264":
                self._encoder_settings_dialog.set_page("h264")

                h264_settings = self._playblast.get_h264_settings()
                self._encoder_settings_dialog.set_h264_settings(
                    h264_settings["quality"], h264_settings["preset"]
                )
            else:
                self.append_output(
                    "[ERROR] Settings page not found for encoder: {0}".format(encoder)
                )

        self._encoder_settings_dialog.show()

    def on_encoder_settings_dialog_modified(self):
        """Handle encoder settings dialog changes."""
        if self.encoding_container_cmb.currentText() == "Image":
            image_settings = self._encoder_settings_dialog.get_image_settings()
            self._playblast.set_image_settings(image_settings["quality"])
        else:
            encoder = self.encoding_video_codec_cmb.currentText()
            if encoder == "h264":
                h264_settings = self._encoder_settings_dialog.get_h264_settings()
                self._playblast.set_h264_settings(
                    h264_settings["quality"], h264_settings["preset"]
                )
            else:
                self.append_output(
                    "[ERROR] Failed to set encoder settings. Unknown encoder: {0}".format(
                        encoder
                    )
                )

    def on_visibility_preset_changed(self):
        """Handle visibility preset change."""
        visibility_preset = self.visibility_cmb.currentText()
        if visibility_preset != "Custom":
            self._playblast.set_visibility(visibility_preset)

    def show_visibility_dialog(self):
        """Show visibility customization dialog."""
        if not self._visibility_dialog:
            self._visibility_dialog = ViewportPlayblastVisibilityDialog(self)
            self._visibility_dialog.accepted.connect(self.on_visibility_dialog_modified)

        self._visibility_dialog.set_visibility_data(self._playblast.get_visibility())

        self._visibility_dialog.show()

    def on_visibility_dialog_modified(self):
        """Handle visibility dialog changes."""
        self.visibility_cmb.setCurrentText("Custom")
        self._playblast.set_visibility(self._visibility_dialog.get_visibility_data())

    def save_settings(self):
        """Save settings to Maya optionVar."""
        cmds.optionVar(
            sv=("ViewportPlayblastFFmpegPath", self._playblast.get_ffmpeg_path())
        )

    def load_settings(self):
        """Load settings from Maya optionVar."""
        if cmds.optionVar(exists="ViewportPlayblastFFmpegPath"):
            self._playblast.set_ffmpeg_path(
                cmds.optionVar(q="ViewportPlayblastFFmpegPath")
            )

    def save_defaults(self):
        """Save current UI state as defaults."""
        cmds.optionVar(
            sv=("ViewportPlayblastOutputDir", self.output_dir_path_le.text())
        )
        cmds.optionVar(
            sv=("ViewportPlayblastOutputFilename", self.output_filename_le.text())
        )
        cmds.optionVar(
            iv=("ViewportPlayblastForceOverwrite", self.force_overwrite_cb.isChecked())
        )

        cmds.optionVar(
            sv=("ViewportPlayblastCamera", self.camera_select_cmb.currentText())
        )
        cmds.optionVar(
            iv=(
                "ViewportPlayblastHideDefaultCameras",
                self.camera_select_hide_defaults_cb.isChecked(),
            )
        )

        cmds.optionVar(
            sv=(
                "ViewportPlayblastResolutionPreset",
                self.resolution_select_cmb.currentText(),
            )
        )
        cmds.optionVar(
            iv=("ViewportPlayblastResolutionWidth", self.resolution_width_sb.value())
        )
        cmds.optionVar(
            iv=("ViewportPlayblastResolutionHeight", self.resolution_height_sb.value())
        )

        cmds.optionVar(
            sv=("ViewportPlayblastFrameRangePreset", self.frame_range_cmb.currentText())
        )
        cmds.optionVar(
            iv=("ViewportPlayblastFrameRangeStart", self.frame_range_start_sb.value())
        )
        cmds.optionVar(
            iv=("ViewportPlayblastFrameRangeEnd", self.frame_range_end_sb.value())
        )

        cmds.optionVar(
            sv=(
                "ViewportPlayblastEncodingContainer",
                self.encoding_container_cmb.currentText(),
            )
        )
        cmds.optionVar(
            sv=(
                "ViewportPlayblastEncodingVideoCodec",
                self.encoding_video_codec_cmb.currentText(),
            )
        )

        h264_settings = self._playblast.get_h264_settings()
        cmds.optionVar(sv=("ViewportPlayblastH264Quality", h264_settings["quality"]))
        cmds.optionVar(sv=("ViewportPlayblastH264Preset", h264_settings["preset"]))

        image_settings = self._playblast.get_image_settings()
        cmds.optionVar(iv=("ViewportPlayblastImageQuality", image_settings["quality"]))

        cmds.optionVar(
            sv=("ViewportPlayblastVisibilityPreset", self.visibility_cmb.currentText())
        )

        visibility_data = self._playblast.get_visibility()
        visibility_str = ""
        for item in visibility_data:
            visibility_str = "{0} {1}".format(visibility_str, int(item))
        cmds.optionVar(sv=("ViewportPlayblastVisibilityData", visibility_str))

        cmds.optionVar(iv=("ViewportPlayblastOverscan", self.overscan_cb.isChecked()))
        cmds.optionVar(iv=("ViewportPlayblastOrnaments", self.ornaments_cb.isChecked()))
        cmds.optionVar(iv=("ViewportPlayblastViewer", self.viewer_cb.isChecked()))

        self.save_settings()

    def load_defaults(self):
        """Load saved defaults."""
        if cmds.optionVar(exists="ViewportPlayblastOutputDir"):
            self.output_dir_path_le.setText(
                cmds.optionVar(q="ViewportPlayblastOutputDir")
            )
        if cmds.optionVar(exists="ViewportPlayblastOutputFilename"):
            self.output_filename_le.setText(
                cmds.optionVar(q="ViewportPlayblastOutputFilename")
            )
        if cmds.optionVar(exists="ViewportPlayblastForceOverwrite"):
            self.force_overwrite_cb.setChecked(
                cmds.optionVar(q="ViewportPlayblastForceOverwrite")
            )

        if cmds.optionVar(exists="ViewportPlayblastCamera"):
            self.camera_select_cmb.setCurrentText(
                cmds.optionVar(q="ViewportPlayblastCamera")
            )
        if cmds.optionVar(exists="ViewportPlayblastHideDefaultCameras"):
            self.camera_select_hide_defaults_cb.setChecked(
                cmds.optionVar(q="ViewportPlayblastHideDefaultCameras")
            )

        if cmds.optionVar(exists="ViewportPlayblastResolutionPreset"):
            self.resolution_select_cmb.setCurrentText(
                cmds.optionVar(q="ViewportPlayblastResolutionPreset")
            )
        if self.resolution_select_cmb.currentText() == "Custom":
            if cmds.optionVar(exists="ViewportPlayblastResolutionWidth"):
                self.resolution_width_sb.setValue(
                    cmds.optionVar(q="ViewportPlayblastResolutionWidth")
                )
            if cmds.optionVar(exists="ViewportPlayblastResolutionHeight"):
                self.resolution_height_sb.setValue(
                    cmds.optionVar(q="ViewportPlayblastResolutionHeight")
                )
            self.on_resolution_changed()

        if cmds.optionVar(exists="ViewportPlayblastFrameRangePreset"):
            self.frame_range_cmb.setCurrentText(
                cmds.optionVar(q="ViewportPlayblastFrameRangePreset")
            )
        if self.frame_range_cmb.currentText() == "Custom":
            if cmds.optionVar(exists="ViewportPlayblastFrameRangeStart"):
                self.frame_range_start_sb.setValue(
                    cmds.optionVar(q="ViewportPlayblastFrameRangeStart")
                )
            if cmds.optionVar(exists="ViewportPlayblastFrameRangeEnd"):
                self.frame_range_end_sb.setValue(
                    cmds.optionVar(q="ViewportPlayblastFrameRangeEnd")
                )
            self.on_frame_range_changed()

        if cmds.optionVar(exists="ViewportPlayblastEncodingContainer"):
            self.encoding_container_cmb.setCurrentText(
                cmds.optionVar(q="ViewportPlayblastEncodingContainer")
            )
        if cmds.optionVar(exists="ViewportPlayblastEncodingVideoCodec"):
            self.encoding_video_codec_cmb.setCurrentText(
                cmds.optionVar(q="ViewportPlayblastEncodingVideoCodec")
            )

        if cmds.optionVar(exists="ViewportPlayblastH264Quality") and cmds.optionVar(
            exists="ViewportPlayblastH264Preset"
        ):
            self._playblast.set_h264_settings(
                cmds.optionVar(q="ViewportPlayblastH264Quality"),
                cmds.optionVar(q="ViewportPlayblastH264Preset"),
            )

        if cmds.optionVar(exists="ViewportPlayblastImageQuality"):
            self._playblast.set_image_settings(
                cmds.optionVar(q="ViewportPlayblastImageQuality")
            )

        if cmds.optionVar(exists="ViewportPlayblastVisibilityPreset"):
            self.visibility_cmb.setCurrentText(
                cmds.optionVar(q="ViewportPlayblastVisibilityPreset")
            )
        if self.visibility_cmb.currentText() == "Custom":
            if cmds.optionVar(exists="ViewportPlayblastVisibilityData"):
                visibility_str_list = cmds.optionVar(
                    q="ViewportPlayblastVisibilityData"
                ).split()
                visibility_data = []
                for item in visibility_str_list:
                    if item:
                        visibility_data.append(bool(int(item)))

                self._playblast.set_visibility(visibility_data)

        if cmds.optionVar(exists="ViewportPlayblastOverscan"):
            self.overscan_cb.setChecked(cmds.optionVar(q="ViewportPlayblastOverscan"))
        if cmds.optionVar(exists="ViewportPlayblastOrnaments"):
            self.ornaments_cb.setChecked(cmds.optionVar(q="ViewportPlayblastOrnaments"))
        if cmds.optionVar(exists="ViewportPlayblastViewer"):
            self.viewer_cb.setChecked(cmds.optionVar(q="ViewportPlayblastViewer"))

    def show_settings_dialog(self):
        """Show settings dialog."""
        if not self._settings_dialog:
            self._settings_dialog = ViewportPlayblastSettingsDialog(self)
            self._settings_dialog.accepted.connect(self.on_settings_dialog_modified)

        self._settings_dialog.set_ffmpeg_path(self._playblast.get_ffmpeg_path())

        self._settings_dialog.show()

    def on_settings_dialog_modified(self):
        """Handle settings dialog changes."""
        ffmpeg_path = self._settings_dialog.get_ffmpeg_path()
        self._playblast.set_ffmpeg_path(ffmpeg_path)

        self.save_settings()

    def show_about_dialog(self):
        """Show about dialog."""
        text = "<h2>{0}</h2>".format(ViewportPlayblastUi.TITLE)
        text += "<p>Version: {0}</p>".format(ViewportPlayblast.VERSION)
        text += "<p>Professional viewport playblast tool for Maya.</p><br>"

        QtWidgets.QMessageBox().about(self, "About", "{0}".format(text))

    def append_output(self, text):
        """Append text to output log."""
        self.output_edit.appendPlainText(text)

    def keyPressEvent(self, event):
        """Handle key press events."""
        super(ViewportPlayblastUi, self).keyPressEvent(event)
        event.accept()

    def showEvent(self, event):
        """Handle show event."""
        self.refresh()
