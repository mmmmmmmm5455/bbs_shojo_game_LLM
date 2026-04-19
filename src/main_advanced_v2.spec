# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec: 图形主程序 onedir，输出 dist/BBSShojoGame/。"""
import os

block_cipher = None
spec_dir = os.path.dirname(os.path.abspath(SPEC))

bbs_data_src = os.path.join(spec_dir, "story_mode", "bbs_data")
datas = []
if os.path.isdir(bbs_data_src):
    datas.append((bbs_data_src, os.path.join("story_mode", "bbs_data")))

assets_src = os.path.join(os.path.dirname(spec_dir), "assets")
if os.path.isdir(assets_src):
    datas.append((assets_src, "assets"))

a = Analysis(
    ["main_advanced_v2.py"],
    pathex=[spec_dir],
    binaries=[],
    datas=datas,
    hiddenimports=["story_mode.bbs_engine", "story_mode.girl_state"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="BBSShojoGame",
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
    version=os.path.join(spec_dir, "file_version_info.txt"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="BBSShojoGame",
)
