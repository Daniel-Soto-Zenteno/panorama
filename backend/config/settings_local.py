"""Desarrollo local con SQLite, sin modificar la configuración PostgreSQL."""
import os
import secrets
from pathlib import Path

secret_path = Path(__file__).resolve().parent.parent / '.local-secret-key'
if 'SECRET_KEY' not in os.environ:
    try:
        with secret_path.open('x', encoding='utf-8') as secret_file:
            secret_file.write(secrets.token_urlsafe(48))
    except FileExistsError:
        pass
    os.environ['SECRET_KEY'] = secret_path.read_text(encoding='utf-8').strip()
for key in ('DB_NAME', 'DB_USER', 'DB_PASSWORD'):
    os.environ.setdefault(key, 'unused')

from .settings import *  # noqa: F403

DEBUG = True
DESIGN_PREVIEW = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'design.sqlite3'}}
