import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel  # type: ignore
from PyQt6.QtCore import Qt  # type: ignore
from utils.player_controls import PlayerControls

class DemoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#f0f0f0")
        v = QVBoxLayout(self)
        v.setContentsMargins(10,10,10,10)
        v.setSpacing(10)

        # placeholder content
        content = QLabel("SONG AREA")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.setStyleSheet("background:grey")
        content.setFixedHeight(200)
        v.addWidget(content, stretch=1)

        # player footer
        self.controls = PlayerControls()
        v.addWidget(self.controls, stretch=0)

from menu_tab_widgets import DevelopTab
class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Player Footer Demo")
        self.resize(600,300)

        tabs = QTabWidget()
        tabs.addTab(DemoTab(), "Tab 1")
        tabs.addTab(DevelopTab("blue"), "Tab 2")
        self.setCentralWidget(tabs)


if __name__=="__main__":
    app = QApplication(sys.argv)
    w = DemoWindow()
    w.show()
    sys.exit(app.exec())
