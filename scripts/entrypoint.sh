#!/bin/sh
set -e

echo "Creando tablas..."
python /app/scripts/init_db.py

echo "Ejecutando seed de roles..."
python /app/scripts/seed_roles.py

echo "Iniciando aplicación..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 2