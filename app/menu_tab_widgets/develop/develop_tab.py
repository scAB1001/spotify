from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel  # type: ignore

class DevelopTab(QWidget):
    def __init__(self, colour):
        super().__init__()
        self.setStyleSheet(f"background-color: {colour};")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Developer Tools Coming Soon..."))
        self.setLayout(layout)
