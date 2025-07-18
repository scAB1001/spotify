from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget  # type: ignore
from core.controller import controller

class PlaylistsTab(QWidget):
    def __init__(self, colour):
        super().__init__()
        self.setStyleSheet(f"background-color: {colour};")
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.song_list = QListWidget()
        layout.addWidget(QLabel("Playlist: Chill Vibes"))
        layout.addWidget(self.song_list)

        refresh_button = QPushButton("Refresh Playlist")
        refresh_button.clicked.connect(self.load_playlist)
        layout.addWidget(refresh_button)

        self.load_playlist()

    def load_playlist(self):
        self.song_list.clear()
        self.song_list.addItems(controller.get_playlist("Chill Vibes"))
