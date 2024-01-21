# -*- mode: python ; coding: utf-8 -*-

from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal, hookspath, runtime_hooks
from kivymd import hooks_path as kivymd_hooks_path

a = Analysis(
    ['main.py'],
    pathex=[],
    datas=[('libs/kv/', 'libs/kv/'), ('assets/', 'assets/')],
    hookspath=[*hookspath(), kivymd_hooks_path],
    hooksconfig={},
    runtime_hooks=runtime_hooks(),
    noarchive=False,
    **get_deps_minimal(video=None, audio=None),
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Passbank',
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
    icon=['data/icon.ico'],
)

app = BUNDLE(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Passbank.app',
    icon='data/icon.png',
    bundle_identifier='dev.ibrahimcetin.passbank',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Passbank',
)
