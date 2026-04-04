# 🎡 LuckyWheel - Customizable Spin Wheel Application

A modern, feature-rich spin wheel application built with PyQt5, perfect for random draws, giveaways, decision-making, or just for fun. Customize every aspect of the wheel with an intuitive interface and stunning visual effects.

!https://via.placeholder.com/800x450/4A148C/FFFFFF?text=LuckyWheel+Demo

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