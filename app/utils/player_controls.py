from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton  # type: ignore
from PyQt6.QtCore import Qt # type: ignore
from utils.progress_bar import ProgressBar

class PlayerControls(QWidget):
    """Footer with: [1] restart [2] current time [3] slider [4] duration [5] play/pause"""
    def __init__(self, parent=None):
        super().__init__(parent)
        h = QHBoxLayout(self)
        h.setContentsMargins(5,5,5,5)
        h.setSpacing(10)

        # [1] restart
        self.restart_btn = QPushButton("⟲")
        self.restart_btn.setFixedSize(30,30)
        self.restart_btn.setStyleSheet("background:darkgreen")
        h.addWidget(self.restart_btn)

        # [2] current time
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setFixedWidth(50)
        self.current_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_time_label.setStyleSheet("background:darkcoral")
        h.addWidget(self.current_time_label)

        # [3] slider
        self.progress = ProgressBar()
        self.progress.setStyleSheet("background:darkblue")
        h.addWidget(self.progress, stretch=1)

        # [4] duration
        self.duration_label = QLabel("00:50")
        self.duration_label.setFixedWidth(50)
        self.duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.duration_label.setStyleSheet("background:darkpink")
        h.addWidget(self.duration_label)

        # [5] play/pause
        self.play_pause_btn = QPushButton("▶️")
        self.play_pause_btn.setFixedSize(30,30)
        self.play_pause_btn.setStyleSheet("background:khaki")
        h.addWidget(self.play_pause_btn)

        # wire up
        self.restart_btn.clicked.connect(lambda: self._on_restart())
        self.play_pause_btn.clicked.connect(lambda: self.progress.play_pause())

        # Each time slider moves (timer tick or user drag), update the label:
        self.progress.valueChanged.connect(self._on_progress_changed)

    def _on_restart(self):
        # parse duration_label text "MM:SS" → seconds
        m, s = map(int, self.duration_label.text().split(":"))
        total = m*60 + s
        self.progress.restart(total)

    def _on_progress_changed(self, val: int):
        # update current_time_label to MM:SS
        m, s = divmod(val, 60)
        self.current_time_label.setText(f"{m:02d}:{s:02d}")

