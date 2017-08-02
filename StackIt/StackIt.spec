# -*- mode: python -*-

block_cipher = None


a = Analysis(['StackIt.py'],
             pathex=['C:\\Users\\Clock\\Documents\\Projects\\StackIt'],
             binaries=[],
             datas=[('resources', 'resources')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='StackIt',
          debug=False,
          strip=False,
          upx=True,
          console=True )
