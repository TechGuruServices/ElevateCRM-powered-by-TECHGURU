
import os
from pathlib import Path

backend_dir = Path("../backend")
datas = []

# Add all necessary data files
files_to_include = [
    # Database files
    (backend_dir.glob("*.db"), "."),
    # Static files
    (backend_dir / "app" / "static", "app/static"),
    # Migration files (if needed)
    (backend_dir / "migrations", "migrations"),
    # Config files
    (backend_dir.glob("*.ini"), "."),
]

for source, dest in files_to_include:
    if isinstance(source, Path):
        if source.exists():
            datas.append((str(source), dest))
            print(f"Including: {source} -> {dest}")
    else:
        for file in source:
            if file.exists():
                datas.append((str(file), dest))
                print(f"Including: {file} -> {dest}")

# Comprehensive hidden imports
hiddenimports = [
    # Uvicorn and FastAPI core
    'uvicorn',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.server',
    'uvicorn.config',
    
    # FastAPI
    'fastapi',
    'fastapi.responses',
    'fastapi.staticfiles',
    'fastapi.middleware',
    'fastapi.middleware.cors',
    'fastapi.security',
    
    # SQLAlchemy
    'sqlalchemy',
    'sqlalchemy.dialects',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.dialects.postgresql',
    'sqlalchemy.engine',
    'sqlalchemy.pool',
    
    # Pydantic
    'pydantic',
    'pydantic.v1',
    
    # Authentication
    'jwt',
    'passlib',
    'passlib.handlers',
    'passlib.handlers.bcrypt',
    'bcrypt',
    
    # Other essentials
    'email_validator',
    'python_multipart',
    'starlette',
    'starlette.middleware',
    'starlette.responses',
]

# Analysis configuration
a = Analysis(
    ['robust_launcher.py'],
    pathex=[str(backend_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate binaries
seen = set()
a.binaries = [x for x in a.binaries if x[0] not in seen and not seen.add(x[0])]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ElevateCRM_Fixed',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
