# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/ocrinvoice/gui/ocr_main_window.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('docs', 'docs'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'pytesseract',
        'pdf2image',
        'opencv-python',
        'PIL',
        'numpy',
        'PyPDF2',
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
    name='OCRInvoiceParser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='installer/icon.ico' if os.path.exists('installer/icon.ico') else None,
)
