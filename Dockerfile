FROM node:22-alpine AS frontend-builder

WORKDIR /build/frontend
RUN corepack enable
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm run build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MKA_ROOT_DIR=/app

WORKDIR /app
COPY backend/pyproject.toml ./backend/
COPY backend/manufacturing_agent ./backend/manufacturing_agent
RUN python -m pip install --no-cache-dir ./backend

COPY data ./data
COPY evals ./evals
COPY --from=frontend-builder /build/frontend/dist ./frontend/dist

EXPOSE 8000
CMD ["uvicorn", "manufacturing_agent.api:app", "--host", "0.0.0.0", "--port", "8000"]
