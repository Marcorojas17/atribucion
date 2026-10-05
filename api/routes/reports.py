"""
Atribución — Endpoints de reportes.

GET /v1/reports/{yyyy-mm}       → informe mensual en JSON
GET /v1/reports/{yyyy-mm}.pdf   → informe mensual en PDF
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from api.middleware.auth import TenantContext, get_current_tenant

router = APIRouter(prefix="/v1/reports", tags=["reports"])

PERIOD_PATTERN = re.compile(r"^\d{4}-\d{2}$")


# ─────────────────────────────────────────────────────────────
# JSON
# ─────────────────────────────────────────────────────────────

@router.get(
    "/{period}",
    summary="Informe mensual (JSON)",
)
async def get_monthly_report(
    period: str,
    tenant: TenantContext = Depends(get_current_tenant),
) -> dict[str, Any]:
    """
    Devuelve el informe mensual del tenant en JSON.

    El período debe estar en formato YYYY-MM.
    """
    if not PERIOD_PATTERN.match(period):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de período inválido. Usa YYYY-MM.",
        )

    year, month = period.split("-")

    # Mock: en producción, agregar datos reales de la DB
    return {
        "period": period,
        "tenant_id": tenant.id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_actions": 0,
            "total_agents": 0,
            "total_certificates": 0,
            "period_start": f"{year}-{month}-01T00:00:00Z",
            "period_end": f"{year}-{month}-28T23:59:59Z",
        },
        "compliance": {
            "eu_ai_act": {
                "article_12": "compliant",
                "article_14": "compliant",
                "article_22": "compliant",
            }
        },
        "proofs": {
            "merkle_root": "0x" + "0" * 64,
            "anchor_tx": "0x" + "0" * 64,
            "anchor_network": "mock",
            "tsa_authority": "mock-tsa",
        },
    }


# ─────────────────────────────────────────────────────────────
# PDF
# ─────────────────────────────────────────────────────────────

@router.get(
    "/{period}.pdf",
    summary="Informe mensual (PDF)",
    responses={
        200: {"content": {"application/pdf": {}}},
    },
)
async def get_monthly_report_pdf(
    period: str,
    tenant: TenantContext = Depends(get_current_tenant),
) -> Response:
    """
    Devuelve el informe mensual en PDF.

    Genera un PDF mínimo con los datos del período.
    En producción, usa ReportLab para un PDF completo.
    """
    if not PERIOD_PATTERN.match(period):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de período inválido. Usa YYYY-MM.",
        )

    # PDF mínimo válido (placeholder)
    pdf_content = _build_minimal_pdf(
        title=f"Informe Atribución — {period}",
        tenant_id=tenant.id,
    )

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="atribucion-{period}.pdf"',
        },
    )


def _build_minimal_pdf(title: str, tenant_id: str) -> bytes:
    """
    Construye un PDF mínimo válido (1 página, texto).

    Cuando se instale ReportLab, se reemplaza por un PDF
    con tabla de acciones, gráficos y firma digital.
    """
    content = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length 90>>stream
BT /F1 16 Tf 72 720 Td ({title}) Tj ET
BT /F1 12 Tf 72 690 Td (Tenant: {tenant_id}) Tj ET
endstream
endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000239 00000 n 
0000000378 00000 n 
trailer<</Size 6/Root 1 0 R>>
startxref
449
%%EOF"""
    return content.encode("latin-1")