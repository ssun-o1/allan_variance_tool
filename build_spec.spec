# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

a = Analysis(
    ['allan_variance_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'numpy',
        'pandas',
        'openpyxl',
        'matplotlib',
        'matplotlib.backends.backend_agg',
        'PIL',
        'PIL._imagingtk',
        'PIL._tkinter_finder',
        'tkinter',
    ],
    hookspath=[],
    hooksconfig={},
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='艾伦方差分析工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windows 下不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加 .ico 或 .icns 文件路径
)

# macOS 打包为 .app
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='艾伦方差分析工具.app',
        icon=None,  # 可以添加 .icns 文件路径
        bundle_identifier='com.allanvariance.tool',
    )
