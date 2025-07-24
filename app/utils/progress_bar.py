from PyQt6.QtWidgets import QSlider  # type: ignore
from PyQt6.QtCore import Qt, QTimer  # type: ignore

class ProgressBar(QSlider):
    """A slider that advances every second up to `duration`."""
    def __init__(self, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self._elapsed = 0
        self._duration = 0
        self.setRange(0, 0)

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        self.sliderMoved.connect(self._seek)

    def _tick(self):
        self._elapsed += 1
        if self._elapsed > self._duration:
            self._timer.stop()
            return
        self.setValue(self._elapsed)

    def _seek(self, pos):
        self._elapsed = pos

    def restart(self, duration: int):
        self._duration = duration
        self.setRange(0, duration)
        self._elapsed = 0
        self.setValue(0)
        self._timer.start()

    def play_pause(self):
        if self._timer.isActive():
            self._timer.stop()
        else:
            self._timer.start()

    def stop(self):
        self._timer.stop()
        self._elapsed = 0
        self.setValue(0)
