# Air Control

Air Control is a macOS menu-bar app that lets you control desktop navigation
with hand gestures using your camera.

## Features

- Menu-bar app for macOS
- Camera-based gesture tracking
- Swipe left and right to switch desktops
- Hold near the top or bottom of the frame to scroll

## Requirements

- macOS
- Camera permission
- Accessibility permission for desktop switching and scrolling

## Run Locally

Create and activate a virtual environment, then install dependencies and run:

```bash
python3 -m venv venv
source venv/bin/activate
pip install pyinstaller rumps opencv-contrib-python pyobjc-framework-Vision pyobjc-framework-Quartz
python menu_bar.py
```

## Build

Build the app bundle with:

```bash
./venv/bin/pyinstaller -y "Air Control.spec"
```

The built app will be created at:

```bash
dist/Air Control.app
```

To package a DMG:

```bash
hdiutil create -volname "Air Control" -srcfolder "dist/Air Control.app" -ov -format UDZO "Air Control.dmg"
```

## Sharing With Friends

You can share the generated DMG, but this app is currently unsigned and not
notarized. On another Mac, users may need to:

- right-click the app and choose `Open`
- go to `System Settings > Privacy & Security` and allow the app
- grant Camera and Accessibility permissions

## Signing And Notarization

Release signing support is included in:

- [README_RELEASE.md](README_RELEASE.md)
- [release_macos.sh](release_macos.sh)

An Apple Developer account is required for notarized distribution.
