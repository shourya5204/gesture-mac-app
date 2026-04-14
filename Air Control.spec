# -*- mode: python ; coding: utf-8 -*-

import os


APP_VERSION = os.environ.get('AIR_CONTROL_VERSION', '1.0.0')
BUILD_NUMBER = os.environ.get('AIR_CONTROL_BUILD', APP_VERSION)


a = Analysis(
    ['menu_bar.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Air Control',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='AirControl.icns',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Air Control',
)
app = BUNDLE(
    coll,
    name='Air Control.app',
    icon='AirControl.icns',
    bundle_identifier='com.aircontrol.app',
    info_plist={
        'CFBundleDisplayName': 'Air Control',
        'CFBundleShortVersionString': APP_VERSION,
        'CFBundleVersion': BUILD_NUMBER,
        'LSUIElement': True,
        'NSCameraUsageDescription': 'Air Control uses the camera to detect hand gestures.',
        'NSAppleEventsUsageDescription': 'Air Control sends desktop navigation commands through System Events.',
    },
)
