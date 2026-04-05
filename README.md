


# 🎡 LuckyWheel - 可自定义的幸运大转盘应用

一个基于 PyQt5 构建的现代、功能丰富的转盘应用，适用于随机抽奖、赠品活动、决策或娱乐。通过直观的界面和炫目的视觉效果，自定义转盘的每一个细节。

## ✨ 核心功能

-   **🎨 深度视觉定制**：为转盘和主窗口分别设置背景，支持静态图片与动态 GIF，内置精美渐变与色彩主题。
-   **⚙️ 灵活转盘配置**：动态添加、编辑和删除转盘选项，实时预览，多套预设配色方案。
-   **💾 配置持久化**：自动保存用户的抽奖选项配置与背景图设置，下次启动无需重新设置。
-   **🎯 流畅用户体验**：无边框现代化设计，支持任意位置拖拽窗口，侧滑式设置面板，高DPI适配。
-   **📦 一键打包分发**：提供便捷脚本，可快速构建为跨平台（Windows/macOS/Linux）的独立可执行文件。
-   **增加：花瓣特效，抽奖音效可配置，抽奖权重和份数都可配置**

## 🚀 快速使用指南

1.  **启动**应用。
2.  在右侧面板**添加/编辑**抽奖选项。
3.  点击齿轮按钮(⚙)，在滑出的设置面板中**自定义背景**（支持图片/GIF）。
4.  点击“**SPIN**”按钮开始旋转。
5.  所有配置（选项、背景）将自动保存，下次启动时自动加载。
6.  配置音效可以在程序所在目录增加sounds文件夹，往里面放随机抽取的音效文件。

## ⚙️ 技术规格

-   **依赖**：Python 3.7+， PyQt5
-   **开源**：项目代码开放，可根据需要修改或扩展。



**立即打造您专属的幸运大转盘吧！** 🎯

---

# 🎡 LuckyWheel - Customizable Spin Wheel Application

A modern, feature-rich spin wheel application built with PyQt5, perfect for random draws, giveaways, decision-making, or just for fun. Customize every aspect of the wheel with an intuitive interface and stunning visual effects.

## ✨ Features

### 🎨 **Visual Customization**
- **Dual Background Support**: Set separate backgrounds for the wheel and main window
- **GIF/Image Support**: Use both static images and animated GIFs
- **Gradient & Color Customization**: Beautiful default gradient backgrounds
- **Smooth Animations**: Professional fade and slide animations

### ⚙️ **Configurable Wheel**
- **Dynamic Options**: Add, edit, and remove wheel segments
- **Real-time Preview**: Changes update instantly
- **Persistent Configuration**: Settings saved automatically
- **Multiple Themes**: Pre-configured color schemes

### 🎯 **User Experience**
- **Frameless Design**: Clean, modern interface
- **Drag & Drop**: Move window by dragging anywhere
- **Right-side Drawer**: Slide-out settings panel
- **High DPI Support**: Crisp display on high-resolution screens
- **Responsive Layout**: Adapts to window resizing

### 📦 **Packaging Ready**
- **One-click Build**: Convert to standalone executable
- **Size Optimized**: Excludes unnecessary modules
- **Cross-platform**: Windows, macOS, Linux (with dependencies)

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- PyQt5

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
# Default output (./dist/)
python build.py

# Custom output directory
python build.py "D:/output/path"
```

### Build Features
- Single executable file (`LuckyWheel.exe`)
- No console window
- Optimized module exclusion
- Custom icon support
- Clean build process

## 📁 Project Structure
```
LuckyWheel/
├── main.py              # Application entry point
├── main_window.py      # Main window implementation
├── wheel_widget.py     # Spin wheel widget
├── config_panel.py     # Configuration panel
├── bg_drawer.py        # Background settings drawer
├── build.py           # Packaging script
├── config.json        # User configuration
├── lucky.ico         # Application icon
└── README.md         # This file
```

## 🎮 Usage Guide

### Basic Operations
1. **Launch** the application
2. **Add/Edit options** in the configuration panel
3. **Customize backgrounds** using the settings drawer (⚙ button)
4. **Click "SPIN"** to spin the wheel
5. **View results** in the display area

### Background Customization
- **Wheel Background**: Image/GIF behind wheel segments
- **Window Background**: Global application background
- **Clear Backgrounds**: Restore to default gradients
- **File Formats**: JPG, PNG, GIF, BMP

### Configuration
- **Options List**: Edit text, colors, and order
- **Auto-save**: Changes saved to `config.json`
- **Default Restore**: Built-in fallback options
- **Import/Export**: Manual JSON editing supported

## ⚙️ Technical Details

### Dependencies
```txt
PyQt5>=5.15.0
```

### Key Components
- **RootWidget**: Background-aware base widget with GIF support
- **WheelWidget**: Custom-drawn spinning wheel with physics simulation
- **ConfigPanel**: Real-time option editor with validation
- **BgDrawer**: Animated slide-out settings panel
- **MainWindow**: Frameless window with drag functionality

### Performance Optimizations
- Efficient QPainter rendering
- Memory-managed GIF playback
- Lazy loading of resources
- Minimal module footprint in builds

## 🎨 Customization Tips

### Creating Custom Backgrounds
- **Recommended Size**: 1920x1080 for best results
- **GIF Optimization**: Keep under 5MB for smooth playback
- **Color Contrast**: Ensure text remains readable
- **Transparency**: PNG with alpha channel supported

### Editing Configuration Manually
```json
[
  {
    "text": "Option 1",
    "color": "#FF5733"
  },
  {
    "text": "Option 2", 
    "color": "#33FF57"
  }
]
```

## 📝 License

This project is open source and available under the LICENSE.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Troubleshooting

### Common Issues

**Q: Application won't start**
```
A: Ensure PyQt5 is installed: `pip install PyQt5`
```

**Q: GIF backgrounds not animating**
```
A: Check GIF file integrity. Some GIFs may have compatibility issues.
```

**Q: Build fails with PyInstaller error**
```
A: Update PyInstaller: `pip install --upgrade pyinstaller`
```

**Q: High CPU usage with GIF backgrounds**
```
A: Reduce GIF size or frame rate. Consider using static images.
```

### Debug Mode
Run with verbose output:
```bash
python -v main.py
```

## 📊 Version History

- **v1.0.0** (Initial Release)
  - Core spin wheel functionality
  - Background customization
  - Configuration management
  - Executable packaging

## 🙏 Acknowledgments

- Built with https://www.riverbankcomputing.com/software/pyqt/
- Inspired by various wheel-of-fortune applications
- Icons from https://www.flaticon.com/

## 📞 Support

For support, please:
1. Check the #-troubleshooting section
2. Search existing ../../issues
3. Create a new issue with detailed description

---

**Enjoy spinning!** 🎯