"""
Encoder settings dialog for Viewport Playblast.
"""

from PySide2 import QtCore
from PySide2 import QtWidgets

from ...core.constants import H264_PRESETS


class ViewportPlayblastEncoderSettingsDialog(QtWidgets.QDialog):
    """Encoder settings dialog."""

    ENCODER_PAGES = {
        "h264": 0,
        "Image": 1,
    }

    H264_QUALITIES = [
        "Very High",
        "High",
        "Medium",
        "Low",
    ]

    def __init__(self, parent):
        super(ViewportPlayblastEncoderSettingsDialog, self).__init__(parent)

        self.setWindowTitle("Encoder Settings")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setModal(True)
        self.setMinimumWidth(220)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        """Create dialog widgets."""
        # h264
        self.h264_quality_combo = QtWidgets.QComboBox()
        self.h264_quality_combo.addItems(
            ViewportPlayblastEncoderSettingsDialog.H264_QUALITIES
        )

        self.h264_preset_combo = QtWidgets.QComboBox()
        self.h264_preset_combo.addItems(H264_PRESETS)

        h264_layout = QtWidgets.QFormLayout()
        h264_layout.addRow("Quality:", self.h264_quality_combo)
        h264_layout.addRow("Preset:", self.h264_preset_combo)

        h264_settings_wdg = QtWidgets.QGroupBox("h264 Options")
        h264_settings_wdg.setLayout(h264_layout)

        # image
        self.image_quality_sb = QtWidgets.QSpinBox()
        self.image_quality_sb.setMinimumWidth(40)
        self.image_quality_sb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)
        self.image_quality_sb.setMinimum(1)
        self.image_quality_sb.setMaximum(100)

        image_layout = QtWidgets.QFormLayout()
        image_layout.addRow("Quality:", self.image_quality_sb)

        image_settings_wdg = QtWidgets.QGroupBox("Image Options")
        image_settings_wdg.setLayout(image_layout)

        self.settings_stacked_wdg = QtWidgets.QStackedWidget()
        self.settings_stacked_wdg.addWidget(h264_settings_wdg)
        self.settings_stacked_wdg.addWidget(image_settings_wdg)

        self.accept_btn = QtWidgets.QPushButton("Accept")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")

    def create_layout(self):
        """Create dialog layout."""
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.accept_btn)
        button_layout.addWidget(self.cancel_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(4)
        main_layout.addWidget(self.settings_stacked_wdg)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        """Create signal-slot connections."""
        self.accept_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.close)

    def set_page(self, page):
        """Set the active settings page."""
        if not page in ViewportPlayblastEncoderSettingsDialog.ENCODER_PAGES:
            return False

        self.settings_stacked_wdg.setCurrentIndex(
            ViewportPlayblastEncoderSettingsDialog.ENCODER_PAGES[page]
        )
        return True

    def set_h264_settings(self, quality, preset):
        """Set H.264 settings in the dialog."""
        self.h264_quality_combo.setCurrentText(quality)
        self.h264_preset_combo.setCurrentText(preset)

    def get_h264_settings(self):
        """Get H.264 settings from the dialog."""
        return {
            "quality": self.h264_quality_combo.currentText(),
            "preset": self.h264_preset_combo.currentText(),
        }

    def set_image_settings(self, quality):
        """Set image settings in the dialog."""
        self.image_quality_sb.setValue(quality)

    def get_image_settings(self):
        """Get image settings from the dialog."""
        return {
            "quality": self.image_quality_sb.value(),
        }
