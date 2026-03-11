# -*- mode: python ; coding: utf-8 -*-

import importlib.util

from PyInstaller.utils.hooks import collect_submodules


base_hidden = ["pyaudio", "pystray", "pywinauto"]
optional_hidden = []
for name in ("comtypes", "pywintypes", "pythoncom"):
    if importlib.util.find_spec(name) is not None:
        optional_hidden.append(name)

hidden = base_hidden + optional_hidden + collect_submodules("voice_launcher_app")

datas = [
    ("assets/*.ico", "assets"),
    ("config/*.json", "config"),
]

a = Analysis(
    ["voice_launcher.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
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
    a.binaries,
    a.datas,
    [],
    name="VoiceLauncher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    icon="assets/crypto_bot_icon.ico",
    codesign_identity=None,
    entitlements_file=None,
)
