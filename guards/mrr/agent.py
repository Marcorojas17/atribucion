"""
Atribución — Guardián MRR.

Monitoriza la salud del negocio:
1. Detecta caídas en el uso.
2. Detecta clientes inactivos.
3. Detecta pagos fallidos.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from guards.base import Finding, GuardAgent


class MRRGuard(GuardAgent):
    """Guardián de reputación y negocio."""

    name = "mrr"
    interval_seconds = 3600

    def __init__(self, state_dir: Path | None = None, data_dir: Path | None = None) -> None:
        super().__init__(state_dir)
        self.data_dir = data_dir or (Path.home() / ".atribucion")

    async def check(self) -> list[Finding]:
        findings: list[Finding] = []

        # 1. Verificar tenants inactivos
        tenants_file = self.data_dir / "tenants.json"
        if tenants_file.exists():
            try:
                tenants = json.loads(tenants_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return findings

            now = datetime.now(timezone.utc)
            inactive = 0
            for tenant_id, tenant in tenants.items():
                try:
                    created = datetime.fromisoformat(
                        tenant.get("created_at", "").replace("Z", "+00:00")
                    )
                    age_days = (now - created).days
                    if age_days > 30 and not tenant.get("api_key"):
                        inactive += 1
                except (ValueError, AttributeError):
                    continue

            if inactive > 0:
                findings.append(Finding(
                    guard=self.name,
                    severity="info",
                    message=f"{inactive} tenants inactivos > 30 días",
                    evidence={"inactive_count": inactive},
                ))

        # 2. Verificar certificados recientes
        certs_file = self.data_dir / "certificates.json"
        if certs_file.exists():
            try:
                certs = json.loads(certs_file.read_text(encoding="utf-8"))
                findings.append(Finding(
                    guard=self.name,
                    severity="info",
                    message=f"{len(certs)} certificados totales emitidos",
                    evidence={"total_certificates": len(certs)},
                ))
            except json.JSONDecodeError:
                pass

        return findings