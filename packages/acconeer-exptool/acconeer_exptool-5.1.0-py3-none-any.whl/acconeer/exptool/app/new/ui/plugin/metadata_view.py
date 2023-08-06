from __future__ import annotations

from typing import Optional

from PySide6 import QtCore
from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QLineEdit, QWidget

from acconeer.exptool import a121


_WIDGET_WIDTH = 125


class MetadataView(QGroupBox):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.setTitle("Metadata")
        self.setLayout(QGridLayout(self))

        row = 0

        self.frame_data_length = MetadataValueWidget(self)
        self.layout().addWidget(self.frame_data_length, row, 1)
        self.layout().addWidget(QLabel("Frame data length", self), row, 0)

        row += 1

        self.calibration_temperature = MetadataValueWidget(self)
        self.layout().addWidget(self.calibration_temperature, row, 1)
        self.layout().addWidget(QLabel("Calibration temperature", self), row, 0)

        row += 1

        self.max_sweep_rate = MetadataValueWidget(self)
        self.layout().addWidget(self.max_sweep_rate, row, 1)
        self.layout().addWidget(QLabel("Max sweep rate", self), row, 0)

        self.update(None)

    def update(self, metadata: Optional[a121.Metadata]) -> None:
        self.frame_data_length.setText(f"{metadata.frame_data_length}" if metadata else "-")
        self.calibration_temperature.setText(
            f"{metadata.calibration_temperature}" if metadata else "-"
        )

        if metadata:
            if metadata.max_sweep_rate:
                max_sweep_rate_text = f"{metadata.max_sweep_rate:.0f} Hz"
            else:
                max_sweep_rate_text = "N/A"
        else:
            max_sweep_rate_text = "-"

        self.max_sweep_rate.setText(max_sweep_rate_text)


class MetadataValueWidget(QLineEdit):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAlignment(QtCore.Qt.AlignRight)
        self.setFixedWidth(_WIDGET_WIDTH)
        self.setReadOnly(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
