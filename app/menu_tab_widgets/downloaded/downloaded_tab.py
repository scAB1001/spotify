from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QFileDialog, QHBoxLayout, QInputDialog) # type: ignore
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput  # type: ignore
from PyQt6.QtCore import QUrl  # type: ignore
from PyQt6.QtGui import QIcon  # type: ignore
from core.controller import controller
from core.models.Song import Song
from mutagen.mp3 import MP3  # type: ignore
import os

class DownloadedTab(QWidget):
    def __init__(self, color):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # num_songs = 2
        layout.addWidget(QLabel(f"{len(controller.downloaded_songs)} Downloaded Songs"))

        self.song_list = QListWidget()
        layout.addWidget(self.song_list)
        
        self.rename_btn = QPushButton("Rename")
        self.rename_btn.setObjectName("renameBtn")
        self.rename_btn.clicked.connect(self.rename_song)
        layout.addWidget(self.rename_btn)
        
        self.import_btn = QPushButton("Import Songs")
        self.import_btn.setObjectName("importBtn")
        self.import_btn.clicked.connect(self.import_songs)
        layout.addWidget(self.import_btn)
        
        self.test_btn = QPushButton("test")
        self.test_btn.setObjectName("testBtn")
        self.test_btn.clicked.connect(self.test_method)
        layout.addWidget(self.test_btn)

        self.current_song_index = -1
        self.init_audio_player(layout)
        self.refresh_songs()
        
     
    def test_method(self):
        print(controller.get_num_downloaded_songs())

    def rename_song(self):
        selected_index = self.song_list.currentRow()
        if selected_index == -1:
            print("No song selected.")
            return

        song = controller.downloaded_songs[selected_index]

        new_title, ok = QInputDialog.getText(self, "Rename Song", "Enter new title:", text=song.title)
        if ok and new_title.strip():
            # Strip extension if included
            new_title = os.path.splitext(new_title.strip())[0]

            from core.db import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE songs SET title = ?, updated_at = ? WHERE file_path = ?",
                        (new_title, song.updated_at, song.file_path))
            conn.commit()
            conn.close()

            # Refresh controller and UI
            controller._downloaded_songs = None
            self.refresh_songs()
            print(f"Renamed to: {new_title}")

    def init_audio_player(self, parent_layout):
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        # Bottom nav bar
        nav_bar = QHBoxLayout()

        rewind_icn = QIcon('./icons/rewindIcn.png')
        self.rewind_btn = QPushButton(rewind_icn, "Rewind")
        self.rewind_btn.setToolTip("Rewind the current song")
        self.rewind_btn.clicked.connect(self.rewind)

        play_pause_icn = QIcon('./icons/playPauseIcn.png')
        self.play_pause_btn = QPushButton(play_pause_icn, "Play")
        self.play_pause_btn.setToolTip("Toggle Play/Pause")
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)

        forward_icn = QIcon('./icons/forwardIcn.png')
        self.forward_btn = QPushButton(forward_icn, "Forward")
        self.forward_btn.setToolTip("Play the next song")
        self.forward_btn.clicked.connect(self.play_next_song)

        nav_bar.addWidget(self.rewind_btn)
        nav_bar.addWidget(self.play_pause_btn)
        nav_bar.addWidget(self.forward_btn)

        parent_layout.addLayout(nav_bar)

        # Connect auto-play on song end
        self.media_player.mediaStatusChanged.connect(self.auto_next_on_finished)

    def refresh_songs(self):
        self.song_list.clear()
        for song in controller.downloaded_songs:
            self.song_list.addItem(song.title)

    def import_songs(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select MP3 Files",
            "",
            "MP3 Files (*.mp3)"
        )
        
        for path in file_paths:
            try:
                audio = MP3(path)
                duration = int(audio.info.length)
                file_name = os.path.basename(path)

                clean_title = os.path.splitext(file_name)[0]
                song = Song(
                    title=clean_title,
                    artist="",
                    album="",
                    year=0,
                    genre="",
                    file_path=path,
                    file_name=file_name,
                    duration=duration,
                    file_format="mp3"
                )
                song.save()
            except ValueError as ve:
                print(f"Failed to import {path}: {ve}")

        controller._downloaded_songs = None
        self.refresh_songs()

    def get_selected_song_index(self):
        return self.song_list.currentRow()

    def toggle_play_pause(self):
        if self.media_player.source().isEmpty():
            # Nothing loaded — treat as "play selected"
            self.play_selected_song()
        elif self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_pause_btn.setText("Play")
        else:
            self.media_player.play()
            self.play_pause_btn.setText("Pause")

    def play_selected_song(self):
        index = self.get_selected_song_index()
        if index == -1:
            print("No song selected.")
            return

        self.play_song_by_index(index)

    def rewind(self):
        index = self.get_selected_song_index()
        if index == -1:
            print("No song selected.")
            return

        self.play_song_by_index(index, from_start=True)

    def play_song_by_index(self, index, from_start=False):
        if index < 0 or index >= len(controller.downloaded_songs):
            return

        self.current_song_index = index
        song = controller.downloaded_songs[index]

        file_url = QUrl.fromLocalFile(song.file_path)
        self.media_player.setSource(file_url)
        self.media_player.play()
        self.play_pause_btn.setText("Pause")

        if from_start:
            self.media_player.setPosition(0)

        self.song_list.setCurrentRow(index)

    def play_next_song(self):
        if len(controller.downloaded_songs) == 0:
            return

        next_index = (self.current_song_index + 1) % len(controller.downloaded_songs)
        self.play_song_by_index(next_index)

    def auto_next_on_finished(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.play_next_song()
