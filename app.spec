# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['app.py', 'geekhub\\__init__.py', 'geekhub\\api\\robot.py', 'geekhub\\api\\__init__.py', 'geekhub\\common\\fake_user_agent.py', 'geekhub\\common\\msg_type.py', 'geekhub\\common\\__init__.py', 'geekhub\\workers\\check.py', 'geekhub\\workers\\msg.py', 'geekhub\\workers\\user.py', 'geekhub\\workers\\worker.py', 'geekhub\\workers\\__init__.py'],
             pathex=['D:\\workspace\\python\\GeekHub-App'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='geekhub',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='geekhub.ico')
