"""
程序内置音效库：用 Python 生成几种不同风格的短音效 WAV，
无需外部音频文件，通过 QMediaPlayer 播放。
"""
import math
import struct
import random
import tempfile
import os
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl


SAMPLE_RATE = 44100


def _pack_wav(samples) -> bytes:
    """将 -1~1 浮点样本列表打包成 16bit mono WAV bytes"""
    n = len(samples)
    data = struct.pack(f"<{n}h", *(max(-32768, min(32767, int(s * 32767))) for s in samples))
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + len(data), b"WAVE",
        b"fmt ", 16, 1, 1,
        SAMPLE_RATE, SAMPLE_RATE * 2, 2, 16,
        b"data", len(data),
    )
    return header + data


def _adsr(t, attack=0.01, decay=0.05, sustain=0.6, release=0.2, total=1.0):
    if t < attack:
        return t / attack
    elif t < attack + decay:
        return 1.0 - (1.0 - sustain) * (t - attack) / decay
    elif t < total - release:
        return sustain
    else:
        remaining = total - t
        return sustain * remaining / release if remaining > 0 else 0


# ── 各种音效生成函数 ──────────────────────────────────────

def _sound_fanfare(dur=1.2):
    """欢快号角：上行音阶"""
    sr = SAMPLE_RATE
    n = int(sr * dur)
    notes = [523.25, 659.25, 783.99, 1046.50]  # C5 E5 G5 C6
    seg = n // len(notes)
    samples = []
    for fi, freq in enumerate(notes):
        for i in range(seg):
            t = i / sr
            env = _adsr(t, 0.01, 0.05, 0.7, 0.15, seg / sr)
            s = math.sin(2 * math.pi * freq * t) * 0.6
            s += math.sin(2 * math.pi * freq * 2 * t) * 0.2
            s += math.sin(2 * math.pi * freq * 3 * t) * 0.1
            samples.append(s * env)
    return _pack_wav(samples)


def _sound_magic(dur=1.0):
    """魔法音效：频率快速上扫 + 颤音"""
    sr = SAMPLE_RATE
    n = int(sr * dur)
    samples = []
    for i in range(n):
        t = i / sr
        freq = 400 + 1200 * (t / dur) ** 2
        vibrato = math.sin(2 * math.pi * 8 * t) * 15
        env = math.exp(-t * 1.5) * (1 - math.exp(-t * 30))
        s = math.sin(2 * math.pi * (freq + vibrato) * t) * 0.7
        samples.append(s * env)
    return _pack_wav(samples)


def _sound_sparkle(dur=0.8):
    """星星闪烁：随机高频短脉冲叠加"""
    sr = SAMPLE_RATE
    n = int(sr * dur)
    samples = [0.0] * n
    for _ in range(12):
        freq = random.uniform(800, 2400)
        start = random.randint(0, n // 2)
        length = random.randint(sr // 20, sr // 8)
        for j in range(min(length, n - start)):
            t = j / sr
            env = math.exp(-t * 20)
            samples[start + j] += math.sin(2 * math.pi * freq * t) * 0.25 * env
    # 归一化
    mx = max(abs(s) for s in samples) or 1
    samples = [s / mx * 0.8 for s in samples]
    return _pack_wav(samples)


def _sound_drum_roll(dur=1.0):
    """鼓点连打 + 收尾重击"""
    sr = SAMPLE_RATE
    n = int(sr * dur)
    samples = [0.0] * n
    # 连打（噪音衰减模拟）
    rolls = 16
    for k in range(rolls):
        start = int(n * 0.0 + k * (n * 0.65 / rolls))
        amp = 0.3 + 0.5 * (k / rolls)
        length = int(sr * 0.04)
        for j in range(min(length, n - start)):
            t = j / sr
            noise = random.uniform(-1, 1)
            env = math.exp(-t * 40)
            samples[start + j] += noise * env * amp
    # 重击结尾
    hit_start = int(n * 0.7)
    for j in range(min(int(sr * 0.3), n - hit_start)):
        t = j / sr
        noise = random.uniform(-1, 1)
        env = math.exp(-t * 10)
        freq = 80
        tone = math.sin(2 * math.pi * freq * t)
        samples[hit_start + j] += (noise * 0.4 + tone * 0.6) * env
    mx = max(abs(s) for s in samples) or 1
    samples = [s / mx * 0.85 for s in samples]
    return _pack_wav(samples)


def _sound_chime(dur=1.5):
    """风铃：多频叠加衰减"""
    sr = SAMPLE_RATE
    n = int(sr * dur)
    freqs = [523.25, 659.25, 880.0, 1108.73, 1318.51]
    samples = [0.0] * n
    for fi, freq in enumerate(freqs):
        delay = int(fi * sr * 0.07)
        for j in range(n - delay):
            t = j / sr
            env = math.exp(-t * 2.5)
            samples[delay + j] += math.sin(2 * math.pi * freq * t) * env * 0.3
    mx = max(abs(s) for s in samples) or 1
    samples = [s / mx * 0.8 for s in samples]
    return _pack_wav(samples)


def _sound_lucky(dur=1.3):
    """幸运音：三和弦 + 上行琶音"""
    sr = SAMPLE_RATE
    chord = [261.63, 329.63, 392.00, 523.25]  # C4 E4 G4 C5
    n = int(sr * dur)
    samples = [0.0] * n
    for fi, freq in enumerate(chord):
        delay = int(fi * sr * 0.06)
        for j in range(n - delay):
            t = j / sr
            total_t = dur - delay / sr
            env = _adsr(t, 0.005, 0.1, 0.5, 0.4, total_t)
            samples[delay + j] += math.sin(2 * math.pi * freq * t) * env * 0.35
    mx = max(abs(s) for s in samples) or 1
    samples = [s / mx * 0.8 for s in samples]
    return _pack_wav(samples)


# ── 音效管理器 ────────────────────────────────────────────

_SOUND_GENERATORS = [
    _sound_fanfare,
    _sound_magic,
    _sound_sparkle,
    _sound_drum_roll,
    _sound_chime,
    _sound_lucky,
]

# 临时文件缓存
_tmp_files = []  # list of str


def _ensure_sound_files():
    global _tmp_files
    if _tmp_files:
        return _tmp_files
    for gen in _SOUND_GENERATORS:
        wav_data = gen()
        fd, path = tempfile.mkstemp(suffix=".wav")
        with os.fdopen(fd, "wb") as f:
            f.write(wav_data)
        _tmp_files.append(path)
    return _tmp_files


class SoundPlayer:
    """随机播放一个内置音效"""

    def __init__(self):
        self._player = QMediaPlayer()
        self._files = _ensure_sound_files()

    def play_random(self):
        path = random.choice(self._files)
        url = QUrl.fromLocalFile(path)
        self._player.setMedia(QMediaContent(url))
        self._player.setVolume(80)
        self._player.play()

    def cleanup(self):
        for p in self._files:
            try:
                os.remove(p)
            except Exception:
                pass
