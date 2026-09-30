#!/usr/bin/env bash
set -e
echo "Инициализация базы данных и схемы..."
python3 backend/init_db.py
echo "Запуск сервера веб-приложения..."
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload