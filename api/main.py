"""
Atribución — Servidor FastAPI.

Punto de entrada del API. Monta los routers, aplica middleware
y expone los endpoints del producto:

    POST /v1/agents                      → registrar agente
    POST /v1/agents/{agent_id}/actions   → registrar acción
    GET  /v1/proofs/{certificate_id}     → verificar certificado
    GET  /v1/health                      → healthcheck

Arrancar en local:
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

Documentación interactiva:
    http://localhost:8000/docs
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api import __version__
from api.routes.actions import router as actions_router
from api.routes.agents import router as agents_router
from api.routes.proofs import router as proofs_router


# ─────────────────────────────────────────────────────────────
# LIFESPAN
# ─────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Ciclo de vida del servidor.

    Startup:
        - Verificar conexión a Ethereum (si hay wallet)
        - Inicializar cache

    Shutdown:
        - Cerrar conexiones limpiamente
    """
    print(f"🚀 Atribución API v{__version__} arrancando...")
    yield
    print("👋 Atribución API cerrando...")


# ─────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Atribución",
    description=(
        "Compliance EU AI Act para agentes IA en un solo endpoint.\n\n"
        "Registra cada acción de tu agente y recibe un certificado "
        "verificable, anclado a Ethereum, sellado por TSA."
    ),
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Marco Antonio Rojas Valdovinos",
        "email": "hola@atribucion.io",
        "url": "https://atribucion.io",
    },
    license_info={
        "name": "MIT OR Apache-2.0",
        "url": "https://github.com/Marcorojas17/atribucion",
    },
)


# ─────────────────────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Añade headers de seguridad a cada respuesta."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-Atribucion-Version"] = __version__
    return response


# ─────────────────────────────────────────────────────────────
# EXCEPTION HANDLERS
# ─────────────────────────────────────────────────────────────

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Convierte ValueError en 400 Bad Request."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "bad_request",
            "detail": str(exc),
            "path": request.url.path,
        },
    )


# ─────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────

app.include_router(actions_router)
app.include_router(agents_router)
app.include_router(proofs_router)


# ─────────────────────────────────────────────────────────────
# ROOT
# ─────────────────────────────────────────────────────────────

@app.get("/", tags=["system"], summary="Información del API")
async def root() -> dict:
    """Raíz del API. Devuelve información y lista de endpoints."""
    return {
        "service": "atribucion",
        "version": __version__,
        "description": "Compliance EU AI Act para agentes IA",
        "endpoints": {
            "register_agent": "POST /v1/agents",
            "record_action": "POST /v1/agents/{agent_id}/actions",
            "verify_certificate": "GET /v1/proofs/{certificate_id}",
            "health": "GET /v1/health",
            "docs": "GET /docs",
        },
        "repository": "https://github.com/Marcorojas17/atribucion",
    }


# ─────────────────────────────────────────────────────────────
# ENTRYPOINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )