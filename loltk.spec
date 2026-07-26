# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'pytest', '_pytest'],
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
    name='loltk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # 不使用 UPX 壓縮。這個執行檔的用途是給陌生人下載，而 UPX 壓縮是
    # 防毒軟體誤判的常見來源；另外 PyInstaller 在找不到 UPX 時會靜默
    # 跳過，導致不同機器建出來的執行檔不一致，難以重現。
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
