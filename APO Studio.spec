# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("faster_whisper")

import os
venv = os.path.join(os.path.dirname(os.path.abspath(SPEC)), '.venv')
nvidia_base = os.path.join(venv, 'Lib', 'site-packages', 'nvidia')

cuda_binaries = []
for sub in ['cublas', 'cudnn', 'cuda_runtime', 'cuda_nvrtc']:
    bin_dir = os.path.join(nvidia_base, sub, 'bin')
    if os.path.isdir(bin_dir):
        for dll in os.listdir(bin_dir):
            if dll.lower().endswith('.dll'):
                src = os.path.join(bin_dir, dll)
                cuda_binaries.append((src, os.path.join('nvidia', sub, 'bin')))

a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=cuda_binaries,
    datas=[
    ("assets", "assets"),
    ("docs", "docs"),
    ("ffmpeg", "ffmpeg"),
    ("src/config", "config"),
    ("src/knowledge", "knowledge"),
    ("src/prompts", "prompts"),
    ("src/schemas", "schemas"),
    ],
    hiddenimports=hiddenimports,
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
    name='APO Studio',
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
    icon="assets/branding/logo_transparence_AS.ico",
    version="version_info.txt",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='APO Studio',
)
