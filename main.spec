# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_qt_plugins, collect_data_files

block_cipher = None

# Collect common Qt plugins used by PyQt6 GUI apps
qt_plugins = collect_qt_plugins('PyQt6', ['platforms', 'styles', 'imageformats', 'iconengines'])
# Collect any data files from the PyQt6 package that might be needed
qt_datas = collect_data_files('PyQt6')

datas = qt_datas + qt_plugins

a = Analysis(
    ['main.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='iptvstalker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='iptvstalker',
)
