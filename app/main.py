import sys
import json
from pathlib import Path
from core.models.models import init_db
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget  # type: ignore
from menu_tab_widgets import TAB_CLASS_MAP
from PyQt6.QtGui import QIcon  # type: ignore
from core.controller import controller  # Shared state

def load_stylesheet(app, *files):
    qss = ""
    for f in files:
        qss += Path(f).read_text() + "\n"
    app.setStyleSheet(qss)

class MainWindow(QMainWindow):
    def __init__(self, options):
        super().__init__()
        self.setWindowTitle("eSpotify")
        self.setGeometry(100, 100, 400, 200)
        
        # Set the application icon (also sets the window icon)
        app_icon = QIcon("./favicon.ico")
        QApplication.instance().setWindowIcon(app_icon)
        
        self.options = options
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.init_tabs()

    def get_from_options(self, item):
        return list(self.options.get(item, {}).values())  

    def init_tabs(self):
        tab_names = self.get_from_options("tabs")
        colours = self.get_from_options("colours")
        for name, colour in zip(tab_names, colours):
            cls = TAB_CLASS_MAP.get(name)
            if cls:
                self.tabs.addTab(cls(colour), name)

if __name__ == "__main__":
    init_db()
    with open("options.json") as f:
        opts = json.load(f)

    app = QApplication(sys.argv)
    # load your global QSS files here:
    load_stylesheet(app, "styles/theme_base.qss")  # "styles/buttons.qss")
    
    window = MainWindow(opts)
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())
