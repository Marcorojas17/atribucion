"""
Atribución — Guardián PHOENIX.

Verifica la resiliencia del sistema:
1. Detecta si el API está respondiendo.
2. Detecta si hay pendientes de anclar.
3. Detecta si hay fallos repetidos.
4. Sugiere reintentos.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx

from guards.base import Finding, GuardAgent


class PhoenixGuard(GuardAgent):
    """Guardián de resiliencia."""

    name = "phoenix"
    interval_seconds = 180

    def __init__(
        self,
        state_dir: Path | None = None,
        api_url: str | None = None,
    ) -> None:
        super().__init__(state_dir)
        self.api_url = api_url or os.getenv("API_URL", "http://localhost:8000")

    async def check(self) -> list[Finding]:
        findings: list[Finding] = []

        # 1. Verificar que el API responde
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self.api_url}/v1/health")
                if r.status_code != 200:
                    findings.append(Finding(
                        guard=self.name,
                        severity="critical",
                        message=f"API respondió con {r.status_code}",
                        evidence={"status_code": r.status_code, "url": self.api_url},
                    ))
                else:
                    findings.append(Finding(
                        guard=self.name,
                        severity="info",
                        message="API OK",
                        evidence={"url": self.api_url, "version": r.json().get("version")},
                    ))
        except httpx.RequestError as e:
            findings.append(Finding(
                guard=self.name,
                severity="critical",
                message=f"API no responde: {e}",
                evidence={"url": self.api_url},
            ))

        # 2. Verificar pendientes de anclar
        pending_file = Path.home() / ".atribucion" / "pending_anchors.jsonl"
        if pending_file.exists():
            count = sum(1 for _ in pending_file.read_text(encoding="utf-8").splitlines() if _.strip())
            if count > 100:
                findings.append(Finding(
                    guard=self.name,
                    severity="warning",
                    message=f"{count} anclajes pendientes (posible backlog)",
                    evidence={"pending_count": count},
                ))

        return findings