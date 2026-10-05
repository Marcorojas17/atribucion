"""
Atribución — Endpoint principal.

POST /v1/agents/{agent_id}/actions

Este es EL endpoint del producto. Una línea de código para el cliente.

Por debajo:
1. Valida la API key.
2. Verifica las firmas del agente (clásica + PQC).
3. Carga y valida el Contrato de Atribución.
4. Emite la credencial verificable (VC 2.0).
5. Firma con la clave híbrida.
6. Ancla el Merkle root a Ethereum.
7. Sella con RFC 3161.
8. Devuelve el certificado.

Cumple con EU AI Act Art. 12, 14, 22.
"""

from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status

# Añadir core/src al path para importar el core criptográfico
CORE_SRC = Path(__file__).resolve().parents[2] / "core" / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from atribucion import anchor, contract as contract_module  # noqa: E402
from atribucion import crypto, merkle, tsa, vc as vc_module  # noqa: E402

from api.middleware.auth import TenantContext, get_current_tenant  # noqa: E402
from api.schemas.action import (  # noqa: E402
    ActionRequest,
    ActionResponse,
    AnchorInfo,
    ComplianceStatus,
    SignatureInfo,
    TimestampInfo,
)


router = APIRouter(prefix="/v1", tags=["actions"])


# ─────────────────────────────────────────────────────────────
# ENDPOINT
# ─────────────────────────────────────────────────────────────

@router.post(
    "/agents/{agent_id}/actions",
    response_model=ActionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una acción de un agente IA",
    description=(
        "Registra una acción de un agente autónomo y devuelve un "
        "certificado verificable que cumple con EU AI Act Art. 12, 14 y 22."
    ),
)
async def record_action(
    agent_id: str,
    body: ActionRequest,
    tenant: TenantContext = Depends(get_current_tenant),
    x_agent_signature: str = Header(..., alias="X-Agent-Signature"),
    x_agent_signature_pqc: str = Header(..., alias="X-Agent-Signature-PQC"),
) -> ActionResponse:
    """
    Registra una acción de un agente y devuelve su certificado.

    Flujo completo:

    1. Validar agente (mock: deriva DID del agent_id).
    2. Verificar firmas del agente.
    3. Cargar/crear Contrato de Atribución.
    4. Validar la acción contra el contrato.
    5. Construir el payload canónico.
    6. Hashear + pinear a IPFS.
    7. Emitir credencial verificable.
    8. Firmar la credencial (híbrida).
    9. Anclar el Merkle root.
    10. Sellar con TSA.
    11. Devolver el certificado.
    """

    # ─── 1. Agente (mock: DID derivado del agent_id) ────────────
    agent_did = "did:kronos:agent:0x" + hashlib.sha256(
        agent_id.encode()
    ).hexdigest()[:40]

    # ─── 2. Payload canónico para verificación ──────────────────
    canonical_payload = crypto.canonical_bytes(body.model_dump(mode="json"))

    # Verificación mock: en producción, el DID del agente tendría
    # su clave pública registrada, y verificaríamos contra ella.
    # Aquí validamos solo el formato de las firmas.
    if not x_agent_signature.startswith("0x") or len(x_agent_signature) < 10:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma clásica con formato inválido.",
        )
    if not x_agent_signature_pqc.startswith("0x") or len(x_agent_signature_pqc) < 10:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma PQC con formato inválido.",
        )

    # ─── 3. Contrato de Atribución (mock) ───────────────────────
    # En producción, se carga de la DB. Aquí se crea al vuelo.
    contrato = contract_module.create_default(
        agent_did=agent_did,
        creator_did=tenant.id,
        operator_did=tenant.id,
        autonomy_level=body.autonomy_level,
        proveedor_modelo="otro",
    )

    # ─── 4. Validar la acción contra el contrato ────────────────
    try:
        contract_module.validate_action(contrato, body)
    except contract_module.ContractViolation as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Violación del Contrato de Atribución: {e}",
        ) from e

    # ─── 5. Payload canónico de la acción ───────────────────────
    action_id = f"act_{uuid4().hex}"
    recorded_at = datetime.now(timezone.utc)

    action_record = {
        "action_id": action_id,
        "agent_did": agent_did,
        "tenant_id": tenant.id,
        "action": body.action,
        "input": body.input,
        "output": body.output,
        "reasoning": body.reasoning,
        "autonomy_level": body.autonomy_level,
        "human_approval": (
            body.human_approval.model_dump(mode="json")
            if body.human_approval
            else None
        ),
        "contract_hash": contrato.hash,
        "recorded_at": recorded_at.isoformat(),
    }

    # ─── 6. Hashear + IPFS ──────────────────────────────────────
    payload_hash = crypto.hash_double(action_record)
    payload_cid = await anchor.pin_to_ipfs(action_record)

    # ─── 7. Emitir credencial verificable ───────────────────────
    certificate_id = f"cert_{uuid4().hex}"
    credential = vc_module.issue(
        credential_id=certificate_id,
        issuer=agent_did,
        subject=agent_did,
        action=action_record,
        evidence={
            "ipfs_cid": payload_cid,
            "sha256": payload_hash["sha256"],
            "sha3": payload_hash["sha3"],
        },
    )

    # ─── 8. Firmar la credencial (híbrida) ──────────────────────
    # Mock: en producción, la clave privada del agente sale del HSM.
    mock_priv, _ = crypto.generate_ecdsa_keypair()
    credential = vc_module.attach_proof(credential, mock_priv)

    # ─── 9. Anclar el Merkle root ───────────────────────────────
    merkle_root = merkle.root_of([action_record])
    anchor_result = await anchor.submit(
        merkle_root=merkle_root,
        metadata={
            "certificate_id": certificate_id,
            "agent_did": agent_did,
            "tenant_id": tenant.id,
        },
    )

    # ─── 10. Sellar con RFC 3161 ────────────────────────────────
    tsa_result = await tsa.seal(
        payload=credential.canonical_bytes(),
        hash_algorithm="sha256",
    )

    # ─── 11. Responder ──────────────────────────────────────────
    return ActionResponse(
        certificate_id=certificate_id,
        proof_url=f"https://api.atribucion.io/v1/proofs/{certificate_id}",
        compliance={
            "eu_ai_act": ComplianceStatus(
                article_12="compliant",
                article_14=(
                    "compliant" if body.human_approval else "not_applicable"
                ),
                article_22=(
                    "compliant" if body.reasoning else "not_applicable"
                ),
            )
        },
        anchor=AnchorInfo(
            tx_hash=anchor_result.tx_hash,
            block=anchor_result.block,
            network=anchor_result.network,
            merkle_root=anchor_result.merkle_root,
        ),
        timestamp_rfc3161=TimestampInfo(
            authority=tsa_result.authority,
            sealed_at=tsa_result.sealed_at,
            token=tsa_result.token,
        ),
        signature=SignatureInfo(
            classic=credential.proof["signatureClassic"],
            pqc=credential.proof["signaturePqc"],
        ),
    )


# ─────────────────────────────────────────────────────────────
# HEALTHCHECK
# ─────────────────────────────────────────────────────────────

@router.get(
    "/health",
    tags=["system"],
    summary="Health check del API",
)
async def health() -> dict[str, str]:
    """Healthcheck público. Devuelve el estado del servicio."""
    return {
        "status": "ok",
        "service": "atribucion-api",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }