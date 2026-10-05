"""
KAF — Emisión de certificados.

Convierte un KAFAssessment en un certificado firmado y anclable.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

# Añadir core/src al path
CORE_SRC = Path(__file__).resolve().parents[2] / "core" / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from atribucion import crypto  # noqa: E402

from kaf.certification.auditor import KAFAssessment  # noqa: E402


@dataclass
class KAFCertificate:
    """Certificado KAF emitido."""

    certificate_id: str
    agent_id: str
    agent_did: str
    level: str
    controls_passed: int
    controls_total: int
    issued_at: str
    expires_at: str
    assessment_hash: str
    signature_classic: str = ""
    signature_pqc: str = ""
    anchor_tx: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "certificate_id": self.certificate_id,
            "agent_id": self.agent_id,
            "agent_did": self.agent_did,
            "level": self.level,
            "controls_passed": self.controls_passed,
            "controls_total": self.controls_total,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "assessment_hash": self.assessment_hash,
            "signature_classic": self.signature_classic,
            "signature_pqc": self.signature_pqc,
            "anchor_tx": self.anchor_tx,
            "metadata": self.metadata,
        }


def issue_certificate(
    assessment: KAFAssessment,
    agent_did: str,
    private_key_pem: bytes,
    validity_days: int = 365,
) -> KAFCertificate:
    """
    Emite un certificado KAF firmado.

    Solo se emite si la evaluación alcanzó al menos KAF-1.
    """
    if assessment.level_achieved == "none":
        raise ValueError(
            "No se puede emitir certificado: el agente no alcanza KAF-1."
        )

    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=validity_days)

    # Hash de la evaluación completa
    assessment_dict = assessment.to_dict()
    assessment_hash = hashlib.sha256(
        crypto.canonical_bytes(assessment_dict)
    ).hexdigest()

    certificate = KAFCertificate(
        certificate_id=f"kaf_{uuid4().hex}",
        agent_id=assessment.agent_id,
        agent_did=agent_did,
        level=assessment.level_achieved,
        controls_passed=assessment.controls_passed,
        controls_total=assessment.controls_total,
        issued_at=now.isoformat(),
        expires_at=expires.isoformat(),
        assessment_hash=assessment_hash,
    )

    # Firmar el certificado
    payload = crypto.canonical_bytes({
        "certificate_id": certificate.certificate_id,
        "agent_did": certificate.agent_did,
        "level": certificate.level,
        "issued_at": certificate.issued_at,
        "assessment_hash": certificate.assessment_hash,
    }).decode("utf-8")

    sig_classic, sig_pqc = crypto.sign_hybrid(private_key_pem, payload)
    certificate.signature_classic = sig_classic
    certificate.signature_pqc = sig_pqc

    return certificate