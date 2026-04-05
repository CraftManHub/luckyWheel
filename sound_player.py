"""
外部音效库：从 sounds/ 文件夹加载音频文件，随机播放。

搜索路径（按优先级）：
  1. 程序所在目录旁的 sounds/
  2. AppData/LuckyWheel/sounds/

支持格式：mp3, wav, ogg, flac, m4a, aac
"""
import os
import sys
import random
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"}


def _find_sounds_dir():
    """返回 sounds 目录路径（不保证存在），以及找到的音频文件列表"""
    candidates = []

    # 1. exe 所在目录旁的 sounds/（onefile 打包：sys.executable 就是 exe 路径）
    #    开发模式：__file__ 所在目录
    if getattr(sys, "frozen", False):
        # onefile：exe 路径；onedir：同样是 exe 路径
        base = os.path.dirname(os.path.abspath(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(base, "sounds"))

    # 2. AppData/LuckyWheel/sounds
    appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
    candidates.append(os.path.join(appdata, "LuckyWheel", "sounds"))

    for d in candidates:
        if os.path.isdir(d):
            files = [
                os.path.join(d, f)
                for f in os.listdir(d)
                if os.path.splitext(f)[1].lower() in AUDIO_EXTS
            ]
            if files:
                return d, files

    # 没有找到音频文件，返回第一个候选路径供提示用
    return candidates[0], []


class SoundPlayer:
    def __init__(self):
        self._player = QMediaPlayer()
        self._sounds_dir, self._files = _find_sounds_dir()

    @property
    def sounds_dir(self):
        return self._sounds_dir

    @property
    def has_sounds(self):
        return bool(self._files)

    def reload(self):
        """重新扫描音频文件"""
        self._sounds_dir, self._files = _find_sounds_dir()

    def play_random(self):
        if not self._files:
            return
        path = random.choice(self._files)
        url = QUrl.fromLocalFile(path)
        self._player.setMedia(QMediaContent(url))
        self._player.setVolume(80)
        self._player.play()
