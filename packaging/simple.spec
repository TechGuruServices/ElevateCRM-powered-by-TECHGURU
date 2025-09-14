
import os
from pathlib import Path

backend_dir = Path("../backend")
datas = []

# Add database if exists
db_files = list(backend_dir.glob("*.db"))
for db_file in db_files:
    datas.append((str(db_file), "."))

# Add static files directory
static_dir = backend_dir / "app" / "static"
if static_dir.exists():
    datas.append((str(static_dir), "app/static"))
    print(f"Including static files from: {static_dir}")

# Add migration files
migrations_dir = backend_dir / "migrations"
if migrations_dir.exists():
    datas.append((str(migrations_dir), "migrations"))

hiddenimports = [
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
    'fastapi',
    'fastapi.responses',
    'fastapi.staticfiles',
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.dialects.postgresql',
    'pydantic',
    'jwt',
    'passlib',
    'passlib.handlers.bcrypt',
    'bcrypt',
    'alembic',
    'alembic.config',
    'app.main',
    'app.core.config',
    'app.core.database',
    'app.api.v1.api',
    'app.api.v1.health',
]

a = Analysis(
    ['simple_launcher.py'],
    pathex=[str(backend_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ElevateCRM',
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
