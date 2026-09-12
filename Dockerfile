FROM node:22-bookworm-slim AS frontend
WORKDIR /ui
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build
FROM python:3.11-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.lock /app/backend/requirements.lock
RUN pip install --no-cache-dir -r backend/requirements.lock
COPY backend/ /app/backend/
COPY sample-data/ /app/sample-data/
COPY capabilities.json /app/capabilities.json
COPY --from=frontend /ui/out /app/frontend/out/
ENV APP_ENV=production CHECKPOINT_BACKEND=memory DATA_DIR=/app/data PYTHONUNBUFFERED=1
WORKDIR /app/backend
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
