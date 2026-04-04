"""
build.py - LuckyWheel packaging script

Usage:
    python build.py                  # output to ./dist/
    python build.py D:/output/path   # output to specified directory
"""
import sys
import os
import shutil
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(SCRIPT_DIR, "main.py")
APP_NAME = "LuckyWheel"
ICON_NAME = "lucky.ico"

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SCRIPT_DIR, "dist")

EXCLUDES = [
    "PyQt5.QtWebEngine",
    "PyQt5.QtWebEngineWidgets",
    "PyQt5.QtWebEngineCore",
    "PyQt5.QtNetwork",
    "PyQt5.QtBluetooth",
    "PyQt5.QtNfc",
    "PyQt5.QtPositioning",
    "PyQt5.QtLocation",
    "PyQt5.QtSensors",
    "PyQt5.QtSerialPort",
    "PyQt5.QtSql",
    "PyQt5.QtTest",
    "PyQt5.QtXml",
    "PyQt5.QtXmlPatterns",
    "PyQt5.QtMultimedia",
    "PyQt5.QtMultimediaWidgets",
    "PyQt5.QtDesigner",
    "PyQt5.QtHelp",
    "matplotlib",
    "numpy",
    "pandas",
    "scipy",
    "cv2",
    "tkinter",
]

def clean():
    for p in [
        os.path.join(SCRIPT_DIR, "build"),
        os.path.join(SCRIPT_DIR, "__pycache__"),
        os.path.join(SCRIPT_DIR, APP_NAME + ".spec"),
    ]:
        if os.path.isdir(p):
            shutil.rmtree(p)
            print(f"  removed dir:  {p}")
        elif os.path.isfile(p):
            os.remove(p)
            print(f"  removed file: {p}")

def build():
    os.makedirs(OUT_DIR, exist_ok=True)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "-i", ICON_NAME,
        "--onefile",
        "--windowed",
        "--name", APP_NAME,
        "--distpath", OUT_DIR,
        "--workpath", os.path.join(SCRIPT_DIR, "build"),
        "--specpath", SCRIPT_DIR,
    ]
    for mod in EXCLUDES:
        cmd += ["--exclude-module", mod]
    cmd.append(MAIN)

    print("Command:", " ".join(cmd))
    print()
    result = subprocess.run(cmd)
    return result.returncode

def main():
    print("=" * 60)
    print(f"  LuckyWheel Build Script")
    print(f"  Output: {OUT_DIR}")
    print("=" * 60)

    print("\n[1/3] Checking PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--version"],
                       check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("ERROR: PyInstaller not found. Run: pip install pyinstaller")
        sys.exit(1)

    print("\n[2/3] Cleaning old build artifacts...")
    clean()

    print("\n[3/3] Building executable...")
    code = build()

    if code != 0:
        print("\nERROR: Build failed. See output above.")
        sys.exit(1)

    print("\n[3/3] Cleaning temp files...")
    clean()

    exe = os.path.join(OUT_DIR, APP_NAME + ".exe")
    size_mb = os.path.getsize(exe) / 1024 / 1024
    print()
    print("=" * 60)
    print("  Build successful!")
    print(f"  Output: {exe}")
    print(f"  Size:   {size_mb:.1f} MB")
    print("=" * 60)

if __name__ == "__main__":
    main()
