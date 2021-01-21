# -*- mode: python ; coding: utf-8 -*-

from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path

import os


path = os.path.abspath(".")
block_cipher = None


a = Analysis(['main.py'],
             pathex=[path],
             binaries=[],
             datas=[("libs\\kv\\", "libs\\kv\\"), ("libs\\kivy_garden\\", "libs\\kivy_garden\\"), ("assets\\fonts\\", "assets\\fonts\\")],
             hiddenimports=[
                "libs.baseclass.addaccountscreen.py",
                "libs.baseclass.loginscreen.py",
                "libs.baseclass.mainscreen.py",
                "libs.baseclass.manager.py",
                "libs.baseclass.optionsscreen.py",
                "libs.baseclass.registerscreen.py"
             ],
             hookspath=[kivymd_hooks_path],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure,
         a.zipped_data,
         cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Passbank',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          icon="data\\icon.ico",
          console=False,
          manifest=None)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               upx=True,
               upx_exclude=[],
               name='Passbank')
