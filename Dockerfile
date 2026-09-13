# ============================================================
# Infera — single-container production build
# 1. Builds the React frontend (Vite static bundle)
# 2. Installs the FastAPI backend
# 3. Serves the SPA with nginx and reverse-proxies /api to uvicorn
# ============================================================

# ---- Stage 1: build frontend ----
FROM node:20-alpine AS web-build
ARG VITE_GOOGLE_ONLY=false
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
# NOTE: the Google OAuth client id is NOT baked in here — the app fetches it
# at runtime from /api/v1/auth/google-config, so no build arg is required.
RUN VITE_API_URL=/api/v1 VITE_GOOGLE_ONLY=$VITE_GOOGLE_ONLY npm run build

# ---- Stage 2: runtime (nginx + uvicorn) ----
FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends nginx && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY --from=web-build /app/frontend/dist /usr/share/nginx/html
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY deploy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
CMD ["/entrypoint.sh"]