import os
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect


class SoundController:
    def __init__(self, assets_path: str = "assets"):
        self.assets_path = assets_path
        self._start_sound = None
        self._stop_sound = None
        self._sounds_loaded = False
        
    def _ensure_sounds_loaded(self):
        if self._sounds_loaded:
            return
            
        start_path = os.path.join(self.assets_path, "start.wav")
        stop_path = os.path.join(self.assets_path, "stop.wav")
        
        if os.path.exists(start_path):
            self._start_sound = QSoundEffect()
            self._start_sound.setSource(QUrl.fromLocalFile(os.path.abspath(start_path)))
            self._start_sound.setVolume(0.5)
            
        if os.path.exists(stop_path):
            self._stop_sound = QSoundEffect()
            self._stop_sound.setSource(QUrl.fromLocalFile(os.path.abspath(stop_path)))
            self._stop_sound.setVolume(0.5)
            
        self._sounds_loaded = True
    
    def play_start_sound(self):
        self._ensure_sounds_loaded()
        if self._start_sound is not None:
            self._start_sound.play()
    
    def play_stop_sound(self):
        self._ensure_sounds_loaded()
        if self._stop_sound is not None:
            self._stop_sound.play()
