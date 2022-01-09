# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


bot = Analysis(['bot_main.py'],
             pathex=[],
             binaries=[],
             datas=[('config.ini', '.'), ('win','win')],
             hiddenimports=['_cffi_backend'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

yt = Analysis(['yt_utils.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

MERGE( (bot, 'bot_main', 'Kasul Bot'), (yt, 'yt_utils', 'yt_utils'))

bot_pyz = PYZ(bot.pure, bot.zipped_data,
             cipher=block_cipher)
bot_exe = EXE(bot_pyz,
          bot.scripts, 
          [],
          exclude_binaries=True,
          name='Kasul Bot',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )


yt_pyz = PYZ(yt.pure, yt.zipped_data,
             cipher=block_cipher)

yt_exe = EXE(yt_pyz,
    yt.scripts, 
    [],
    exclude_binaries=True,
    name='yt_utils',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None )

bot_coll = COLLECT(bot_exe,
               bot.binaries,
               bot.zipfiles,
               bot.datas,
               yt_exe,
               yt.binaries,
               yt.zipfiles,
               yt.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Kasul Bot')