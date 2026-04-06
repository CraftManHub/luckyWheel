
# 🎡 LuckyWheel - 可自定义的幸运大转盘应用

一个基于 PyQt5 构建的现代、功能丰富的转盘应用，适用于随机抽奖、赠品活动、决策或娱乐。具有神秘魔法主题视觉风格，支持权重、份数、音效、背景图等深度自定义。

## ✨ 核心功能

- **🎨 深度视觉定制**：为转盘和主窗口分别设置背景，支持静态图片（JPG/PNG/BMP）与动态 GIF，内置神秘魔法主题渐变配色。
- **⚙️ 灵活转盘配置**：动态添加、编辑、删除抽奖选项；支持每个选项单独设置**文字颜色**；可展开「配比」列设置**抽奖权重**，可展开「份数」列设置**各奖项数量上限**。
- **💾 配置持久化**：抽奖选项自动保存至项目目录下的 `config.json`；背景图路径保存至系统 `%APPDATA%\LuckyWheel\bg_config.json`，重启无需重新设置。
- **🎵 可配置音效**：转盘结束时随机播放 `sounds/` 文件夹中的音频文件；设置面板内可一键静音。
- **🌸 花瓣粒子特效**：点击画面触发椭圆花瓣、心形、五角星三种粒子爆发动画。
- **🎯 流畅用户体验**：无边框现代化设计，支持任意位置拖拽窗口，侧滑式设置面板，高DPI适配，转盘带外发光、符文动画、水晶指针等魔法视觉效果。
- **📦 一键打包分发**：提供便捷脚本，可快速构建为 Windows 独立可执行文件（`.exe`）。

## 🚀 快速使用指南

1. **启动**应用。
2. 在右侧面板**添加/编辑**抽奖选项（至少保留 2 个）。
3. 点击列头上方的「**配比**」按钮展开权重列，填写各选项的相对权重（数字越大中奖概率越高）。
4. 点击「**份数**」按钮展开份数列，填写各奖项的库存数量（`∞` 表示无限次；设为 `0` 后该选项自动从转盘移除）；勾选「**不管份数**」可临时忽略份数限制。
5. 点击齿轮按钮（⚙）滑出设置面板，可设置**转盘背景**和**全局背景**（支持图片/GIF），以及切换**静音**状态。
6. 点击「**SPIN**」按钮（面板底部）开始旋转。
7. 所有配置（选项、背景路径）自动保存，下次启动时自动加载。

### 音效配置

在程序所在目录（或打包后 `.exe` 同级目录）新建 `sounds/` 文件夹，将音频文件放入其中，每次转盘结束后将随机播放一个。

支持格式：`mp3`、`wav`、`ogg`、`flac`、`m4a`、`aac`

## ⚙️ 技术规格

- **依赖**：Python 3.7+，PyQt5（含 QtMultimedia 模块，用于音效播放）
- **开源**：项目代码开放，可根据需要修改或扩展。

---

**立即打造您专属的幸运大转盘吧！** 🎯

---

# 🎡 LuckyWheel - Customizable Spin Wheel Application

A modern, feature-rich spin wheel application built with PyQt5, featuring a mystical magic theme. Perfect for random draws, giveaways, decision-making, or entertainment. Supports weighted probability, quota limits, sound effects, and custom backgrounds.

## ✨ Features

### 🎨 **Visual Customization**
- **Dual Background Support**: Set separate backgrounds for the wheel area and the main window
- **GIF/Image Support**: Supports static images (JPG, PNG, BMP) and animated GIFs
- **Magic Theme**: Built-in dark mystical color palette with glow effects, rune animations, and a crystal pointer
- **Smooth Animations**: Ease-out spin physics; decorative rune ring and center sigil always slowly rotate

### ⚙️ **Configurable Wheel**
- **Dynamic Options**: Add, edit, and remove wheel segments (minimum 2 required)
- **Text Color**: Click the color swatch in the color column to pick a per-option text color
- **Weight (配比)**: Click the "配比" toggle button to show the weight column. Higher weight = higher probability. Wheel segment sizes are proportional to weights.
- **Quota (份数)**: Click the "份数" toggle button to show the quota column. Set a finite stock per prize (∞ = unlimited). When a prize's quota reaches 0 it is automatically removed from the wheel. Enable "不管份数" (Ignore Quota) to temporarily bypass limits.
- **Persistent Configuration**: Options saved automatically to `config.json` in the project directory

### 🎵 **Sound Effects**
- Place audio files in a `sounds/` folder next to the executable (or next to `main.py` in dev mode)
- Supported formats: `mp3`, `wav`, `ogg`, `flac`, `m4a`, `aac`
- A random file is played each time the wheel finishes spinning
- Mute toggle available in the settings drawer (⚙ button)

### 🌸 **Petal Particle Effects**
- Click anywhere on the window to trigger a burst of particle effects
- Three particle shapes: elliptical petals, hearts, and five-pointed stars

### 🎯 **User Experience**
- **Frameless Design**: Clean, borderless window; drag anywhere to move it
- **Right-side Drawer**: Click the ⚙ button to slide open the settings panel
- **High DPI Support**: Crisp display on high-resolution screens
- **Responsive Layout**: Adapts to window resizing

### 📦 **Packaging Ready**
- **One-click Build**: Convert to a standalone `.exe` with `python build.py`
- **Size Optimized**: Unnecessary Qt modules excluded automatically
- **Windows**: Primary target; macOS/Linux require additional dependency setup

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- PyQt5 (including QtMultimedia)

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd LuckyWheel

# Install dependencies
pip install PyQt5

# Run the application
python main.py
```

## 🛠 Building from Source

### 1. Install Build Tools
```bash
pip install pyinstaller
```

### 2. Build Executable
```bash
# Output to ./dist/LuckyWheel.exe
python build.py

# Output to a custom directory
python build.py "D:/output/path"
```

The build script automatically cleans temp files after a successful build.

## 📁 Project Structure
```
LuckyWheel/
├── main.py              # Application entry point
├── main_window.py       # Main window (frameless, drag, layout)
├── wheel_widget.py      # Spin wheel rendering and physics
├── config_panel.py      # Right-side option editor panel
├── bg_drawer.py         # Slide-out background/sound settings drawer
├── petal_overlay.py     # Click-triggered petal particle effects
├── sound_player.py      # Random sound effect player
├── build.py             # PyInstaller packaging script
├── config.json          # Saved wheel options (auto-generated)
├── lucky.ico            # Application icon
└── README.md            # This file
```

> **Note**: Background image paths are saved to `%APPDATA%\LuckyWheel\bg_config.json`, not in the project directory.

## 🎮 Usage Guide

### Basic Operations
1. **Launch** the application
2. **Add/Edit options** in the right-side configuration panel
3. **Customize backgrounds** using the settings drawer (⚙ button, right edge)
4. **Click the SPIN button** (bottom of the config panel) to spin the wheel
5. **View results** in the result display area below the spin button

### Weight Configuration
Click the "配比" button in the panel header to reveal the weight column.

| Option | Weight | Effective Probability |
|--------|--------|-----------------------|
| Prize A | 10 | 10 / (10+30+60) = 10% |
| Prize B | 30 | 30% |
| Prize C | 60 | 60% |

Wheel segment sizes are rendered proportionally to weights.

### Quota Configuration
Click the "份数" button to reveal the quota column:
- `∞` — unlimited draws (default)
- Any positive integer — stock count; decremented automatically after each win
- `0` — exhausted; option is excluded from the wheel on the next spin
- Toggle "不管份数" to ignore all quotas temporarily (e.g., for a rehearsal)

### Background Customization
Open the ⚙ drawer on the right edge:
- **Wheel Background (转盘卷轴)**: Image/GIF shown inside the wheel circle
- **Window Background (世界卷轴)**: Global application background
- **Clear**: Restores the default gradient
- **Supported formats**: JPG, PNG, GIF, BMP
- **Recommended size**: 1920×1080 for window background; keep GIFs under 5 MB for smooth playback

### Sound Effects Setup
```
LuckyWheel.exe          ← or main.py in dev mode
sounds/
  ├── win.mp3
  ├── fanfare.wav
  └── tada.ogg
```
Any audio file in the `sounds/` folder will be picked at random when the wheel stops. If no `sounds/` folder exists, the app runs silently.

### Editing Configuration Manually
```json
[
  {
    "text": "First Prize",
    "weight": 10,
    "text_color": "#FFFFFF",
    "quota": 1
  },
  {
    "text": "Participation",
    "weight": 80,
    "text_color": "#FFD700",
    "quota": -1
  }
]
```
> `quota: -1` means unlimited. The `color` field (wheel segment background) is assigned automatically from the built-in theme palette and does not need to be set manually.

## ⚙️ Technical Details

### Dependencies
```
PyQt5>=5.15.0   (includes QtMultimedia for audio)
```

### Key Components
- **WheelWidget**: Custom-drawn spinning wheel with weighted random selection, ease-out-quart physics, and decorative magic animations
- **ConfigPanel**: Option editor with weight/quota column toggles and real-time wheel sync
- **BgDrawer**: Animated slide-out settings panel for backgrounds and mute
- **PetalOverlay**: Transparent overlay widget rendering click-triggered particle bursts
- **SoundPlayer**: QtMultimedia-based random audio player with auto-discovery of `sounds/` directory
- **MainWindow**: Frameless window with mouse-drag repositioning and High DPI setup

## 🐛 Troubleshooting

**Q: Application won't start**
```
pip install PyQt5
```

**Q: No sound plays**
```
1. Create a sounds/ folder next to main.py (or the .exe)
2. Add at least one mp3/wav/ogg/flac/m4a/aac file
3. Check that the mute button in the ⚙ drawer is not active
```

**Q: GIF backgrounds not animating**
```
Check GIF file integrity. Very large or high-frame-rate GIFs
may cause high CPU usage — consider reducing size or frame rate.
```

**Q: Build fails with PyInstaller error**
```
pip install --upgrade pyinstaller
```

**Q: Saved backgrounds don't load after moving the exe**
```
Background paths are stored as absolute paths in:
%APPDATA%\LuckyWheel\bg_config.json
Re-select your backgrounds after moving the executable.
```

## 📊 Version History

- **v1.0.0** — Core spin wheel, background customization, configuration management, executable packaging
- **v1.1.0** — Added petal particle effects, configurable sound effects, per-option weight (配比) and quota (份数) support

## 📝 License

This project is open source and available under the LICENSE file.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**Enjoy spinning!** 🎯
