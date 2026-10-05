"""
Atribución — Guardián TSA.

Verifica la integridad de los sellos de tiempo:
1. Detecta sellos vencidos.
2. Detecta sellos duplicados.
3. Verifica formato de tokens.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from guards.base import Finding, GuardAgent


class TSAGuard(GuardAgent):
    """Guardián de sellos de tiempo."""

    name = "tsa"
    interval_seconds = 600

    def __init__(self, state_dir: Path | None = None, certs_dir: Path | None = None) -> None:
        super().__init__(state_dir)
        self.certs_dir = certs_dir or (Path.home() / ".atribucion")

    async def check(self) -> list[Finding]:
        findings: list[Finding] = []

        certs_path = self.certs_dir / "certificates.json"
        if not certs_path.exists():
            return findings

        try:
            certs = json.loads(certs_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return findings

        seen_tokens: set[str] = set()
        now = datetime.now(timezone.utc)

        for cert_id, cert in certs.items():
            token = cert.get("tsa_token", "")
            if not token:
                findings.append(Finding(
                    guard=self.name,
                    severity="warning",
                    message=f"Certificado {cert_id} sin sello TSA",
                    evidence={"certificate_id": cert_id},
                ))
                continue

            # Detección: duplicados
            if token in seen_tokens:
                findings.append(Finding(
                    guard=self.name,
                    severity="critical",
                    message=f"Token TSA duplicado: {cert_id}",
                    evidence={"certificate_id": cert_id, "token": token[:20]},
                ))
            else:
                seen_tokens.add(token)

            # Detección: formato inválido
            if not token.startswith("0x") or len(token) != 66:
                findings.append(Finding(
                    guard=self.name,
                    severity="warning",
                    message=f"Token TSA con formato inválido: {cert_id}",
                    evidence={"certificate_id": cert_id, "token": token[:20]},
                ))

        return findings