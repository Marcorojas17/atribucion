"""
Atribución — Guardián SENTINEL.

Verifica el perímetro de seguridad:
1. Detecta requests maliciosos.
2. Detecta payloads anómalos.
3. Detecta firmas inválidas repetidas.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from guards.base import Finding, GuardAgent


class SentinelGuard(GuardAgent):
    """Guardián de perímetro."""

    name = "sentinel"
    interval_seconds = 120

    def __init__(self, state_dir: Path | None = None, logs_dir: Path | None = None) -> None:
        super().__init__(state_dir)
        self.logs_dir = logs_dir or (Path.home() / ".atribucion" / "logs")

    async def check(self) -> list[Finding]:
        findings: list[Finding] = []

        log_file = self.logs_dir / "errors.log"
        if not log_file.exists():
            return findings

        errors_401: Counter[str] = Counter()
        errors_422: Counter[str] = Counter()

        for line in log_file.read_text(encoding="utf-8").splitlines()[-500:]:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            status = entry.get("status")
            ip = entry.get("ip", "unknown")

            if status == 401:
                errors_401[ip] += 1
            elif status == 422:
                errors_422[ip] += 1

        # Detección: muchos 401 desde la misma IP (posible ataque)
        for ip, count in errors_401.most_common(5):
            if count > 20:
                findings.append(Finding(
                    guard=self.name,
                    severity="critical",
                    message=f"IP {ip} con {count} errores 401 (posible ataque)",
                    evidence={"ip": ip, "401_count": count},
                ))

        # Detección: muchos 422 (posible fuzzing)
        for ip, count in errors_422.most_common(5):
            if count > 50:
                findings.append(Finding(
                    guard=self.name,
                    severity="warning",
                    message=f"IP {ip} con {count} errores 422 (posible fuzzing)",
                    evidence={"ip": ip, "422_count": count},
                ))

        return findings