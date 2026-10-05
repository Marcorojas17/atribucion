"""
Atribución — Guardián NEXUS.

Verifica la conectividad con servicios externos:
1. Ethereum RPC.
2. IPFS gateway.
3. TSA.
4. Mercado Pago.
"""

from __future__ import annotations

from pathlib import Path

import httpx

from guards.base import Finding, GuardAgent


class NexusGuard(GuardAgent):
    """Guardián de conectividad externa."""

    name = "nexus"
    interval_seconds = 300

    async def check(self) -> list[Finding]:
        findings: list[Finding] = []

        checks = [
            ("Ethereum RPC", "https://rpc.sepolia.org"),
            ("IPFS gateway", "https://ipfs.io"),
            ("FreeTSA", "https://freetsa.org"),
            ("Mercado Pago", "https://api.mercadopago.com"),
        ]

        async with httpx.AsyncClient(timeout=8.0) as client:
            for name, url in checks:
                try:
                    r = await client.get(url)
                    if r.status_code >= 500:
                        findings.append(Finding(
                            guard=self.name,
                            severity="warning",
                            message=f"{name} responde {r.status_code}",
                            evidence={"service": name, "url": url, "status": r.status_code},
                        ))
                except httpx.RequestError as e:
                    findings.append(Finding(
                        guard=self.name,
                        severity="critical",
                        message=f"{name} inaccesible: {e}",
                        evidence={"service": name, "url": url},
                    ))

        return findings