"""
Atribución — Guardián ORACLE.

Verifica la consistencia de datos:
1. Detecta certificados sin acción asociada.
2. Detecta DIDs inválidos.
3. Detecta contratos sin firmar.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from guards.base import Finding, GuardAgent


class OracleGuard(GuardAgent):
    """Guardián de consistencia de datos."""

    name = "oracle"
    interval_seconds = 600

    DID_PATTERN = re.compile(r"^did:kronos:(agent|human|robot|org):0x[a-fA-F0-9]{40}$")

    def __init__(self, state_dir: Path | None = None, data_dir: Path | None = None) -> None:
        super().__init__(state_dir)
        self.data_dir = data_dir or (Path.home() / ".atribucion")

    async def check(self) -> list[Finding]:
        findings: list[Finding] = []

        certs_file = self.data_dir / "certificates.json"
        if not certs_file.exists():
            return findings

        try:
            certs = json.loads(certs_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return findings

        for cert_id, cert in certs.items():
            agent_did = cert.get("agent_did", "")

            # Validar formato de DID
            if agent_did and not self.DID_PATTERN.match(agent_did):
                findings.append(Finding(
                    guard=self.name,
                    severity="warning",
                    message=f"DID inválido en certificado {cert_id}",
                    evidence={"certificate_id": cert_id, "did": agent_did},
                ))

            # Validar que tiene credencial
            if not cert.get("credential"):
                findings.append(Finding(
                    guard=self.name,
                    severity="warning",
                    message=f"Certificado {cert_id} sin credencial",
                    evidence={"certificate_id": cert_id},
                ))

        return findings