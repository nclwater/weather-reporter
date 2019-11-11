# -*- mode: python -*-

import os
import tinycss2

version = '0.1.0'

block_cipher = None


a = Analysis(['weather_reporter/ui.py', 'build.spec'],
             binaries=[],
             pathex=['C:/Users/AA/ZZ'],
             datas=[(os.path.join(os.path.dirname(tinycss2.__file__), 'VERSION'), 'tinycss2')],
             hiddenimports=['tinycss2'],
             win_no_prefer_redirects=False,
             win_private_assemblies=True,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

name = 'SHEAR-Weather-Reporter-{}'.format(version)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=name,
          upx=False,
          strip=False,
          console=True,
          debug=True)
