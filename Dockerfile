# ─────────────────────────────────────────────────────────────
# ATRIBUCIÓN — Imagen de producción
# ─────────────────────────────────────────────────────────────

FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ─────────────────────────────────────────────────────────────
# DEPENDENCIAS PYTHON
# ─────────────────────────────────────────────────────────────

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────────────────────
# CÓDIGO
# ─────────────────────────────────────────────────────────────

COPY core/ ./core/
COPY api/ ./api/
COPY tests/ ./tests/
COPY pyproject.toml ./

# ─────────────────────────────────────────────────────────────
# USUARIO NO-ROOT (seguridad)
# ─────────────────────────────────────────────────────────────

RUN useradd -m -u 1000 atribucion && \
    chown -R atribucion:atribucion /app

USER atribucion

# ─────────────────────────────────────────────────────────────
# PUERTO Y COMANDO
# ─────────────────────────────────────────────────────────────

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/v1/health || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]