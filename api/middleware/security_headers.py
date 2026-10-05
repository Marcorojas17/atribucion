"""
Atribución — Security headers middleware.

Añade headers de seguridad a cada respuesta.
Cumple con OWASP Secure Headers Project.
"""

from __future__ import annotations

from fastapi import Request


SECURITY_HEADERS = {
    # OWASP
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    # HSTS
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    # CSP básico (ajustar según apps)
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self' https://api.atribucion.io"
    ),
    # Cross-Origin
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
}


async def security_headers_middleware(request: Request, call_next):
    """Añade headers de seguridad a cada respuesta."""
    response = await call_next(request)

    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value

    # Identifica la versión de Atribución
    response.headers["X-Atribucion-Version"] = "0.1.0"

    return response