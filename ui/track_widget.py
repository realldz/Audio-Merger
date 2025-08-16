from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy
from PyQt5.QtCore import pyqtSignal

class TrackWidget(QWidget):
    pin_toggled = pyqtSignal(bool)

    def __init__(self, text, is_pinned=False, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Pin Button
        self.pin_button = QPushButton('📌')
        self.pin_button.setCheckable(True)
        self.pin_button.setChecked(is_pinned)
        self.pin_button.setFixedSize(25, 25)
        self.pin_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:checked {
                background-color: #D3D3D3; /* Light Gray */
                border: 1px solid #A9A9A9; /* Dark Gray */
                border-radius: 4px;
            }
        """)
        self.pin_button.toggled.connect(self.pin_toggled.emit)

        # Track Name Label
        self.label = QLabel(text)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout.addWidget(self.pin_button)
        layout.addWidget(self.label)
        
        self.setLayout(layout)

    def set_pinned(self, is_pinned):
        self.pin_button.setChecked(is_pinned)

    def get_text(self):
        return self.label.text()
