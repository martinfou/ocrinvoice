# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_ocr_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config/default_config.yaml', 'config'),
        ('config/business_mappings.json', 'config'),
        ('config/logging_config.yaml', 'config'),
    ],
    hiddenimports=[
        'ocrinvoice.gui.ocr_main_window',
        'ocrinvoice.gui.widgets.pdf_preview',
        'ocrinvoice.gui.widgets.data_panel',
        'ocrinvoice.gui.widgets.file_naming',
        'ocrinvoice.parsers.invoice_parser',
        'ocrinvoice.core.ocr_engine',
        'ocrinvoice.core.text_extractor',
        'ocrinvoice.core.image_processor',
        'ocrinvoice.utils.fuzzy_matcher',
        'ocrinvoice.utils.amount_normalizer',
        'ocrinvoice.utils.ocr_corrections',
        'ocrinvoice.utils.file_manager',
        'ocrinvoice.utils.filename_utils',
        'ocrinvoice.business.business_mapping_manager',
        'ocrinvoice.business.database',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'pytesseract',
        'pdf2image',
        'pdfplumber',
        'PyPDF2',
        'fuzzywuzzy',
        'cv2',
        'PIL',
        'numpy',
        'pandas',
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
    [],
    exclude_binaries=True,
    name='OCRInvoiceParser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OCRInvoiceParser',
) 