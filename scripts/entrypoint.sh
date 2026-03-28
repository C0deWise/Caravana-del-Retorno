#!/bin/sh
set -e

echo "Ejecutando migraciones..."
/usr/local/bin/alembic upgrade head

echo "Ejecutando seed de roles..."
python scripts/seed_roles.py

echo "Iniciando aplicación..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 2