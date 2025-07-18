from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel  # type: ignore

class StatisticsTab(QWidget):
    def __init__(self, colour):
        super().__init__()
        self.setStyleSheet(f"background-color: {colour};")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Statistics Coming Soon..."))
        self.setLayout(layout)
