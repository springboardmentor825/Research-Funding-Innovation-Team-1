#!/bin/sh
set -e

cd /app/backend

# Start the FastAPI backend on the loopback (nginx proxies /api to it)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 &

# Start nginx in the foreground
exec nginx -g 'daemon off;'