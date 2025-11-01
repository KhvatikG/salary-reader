# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

# Добавляем директорию src в пути Python
sys.path.insert(0, os.path.abspath('src'))

block_cipher = None

a = Analysis(
    ['src/salary_reader/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/salary_reader/resources/*', 'resources'),
        ('src/salary_reader/resources/fonts/*', 'resources/fonts'),
        ('src/salary_reader/resources/images/*', 'resources/images'),
        ('pyproject.toml', '.')
    ],
    hiddenimports=[
        'iiko_api',
        'iiko_api.core',
        'iiko_api.endpoints',
        'iiko_api.models',
        'iiko_api.services',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtOpenGL',
        'PySide6.QtOpenGLWidgets',
        'PySide6.QtPrintSupport',
        'PySide6.QtSvg',
        'PySide6.QtSvgWidgets',
        'PySide6.QtTest',
        'PySide6.QtUiTools',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebSockets',
        'PySide6.QtXml',
        'loguru',
        'sqlalchemy',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.dialects.sqlite.pysqlite',
        'sqlite3',
        'salary_reader.restart_helper',
        'openpyxl',
        'reportlab',
        'xmltodict',
        'requests',
        'packaging',
        'pysidesix_frameless_window',
        'PIL',
        'PIL.Image',
        'PIL._imaging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',
        'numpy.core._multiarray_tests',
        'numpy.libs',
        'numpy.libs._multiarray_umath',
        'numpy.libs._multiarray_tests',
    ],
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
    name='SalaryReader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/salary_reader/resources/images/export-icon.ico'
)
