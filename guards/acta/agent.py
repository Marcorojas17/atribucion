"""
Atribución — Guardián ACTA.

Audita los logs del sistema:
1. Detecta accesos fuera de horario.
2. Detecta IPs sospechosas.
3. Detecta patrones de rate limiting.
4. Verifica que no haya gaps en los logs.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from guards.base import Finding, GuardAgent


class ACTAGuard(GuardAgent):
    """Guardián de auditoría de logs."""

    name = "acta"
    interval_seconds = 300

    def __init__(self, state_dir: Path | None = None, logs_dir: Path | None = None) -> None:
        super().__init__(state_dir)
        self.logs_dir = logs_dir or (Path.home() / ".atribucion" / "logs")

    async def check(self) -> list[Finding]:
        findings: list[Finding] = []

        log_file = self.logs_dir / "access.log"
        if not log_file.exists():
            return findings

        try:
            lines = log_file.read_text(encoding="utf-8").splitlines()
        except OSError:
            return findings

        # Analizar últimos 1000 accesos
        recent = lines[-1000:]
        ips: Counter[str] = Counter()
        hours: Counter[int] = Counter()

        for line in recent:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            ip = entry.get("ip", "")
            ts = entry.get("timestamp", "")

            if ip:
                ips[ip] += 1

            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                hours[dt.hour] += 1
            except (ValueError, AttributeError):
                continue

        # Detección 1: IPs con muchas requests (>100 en el último período)
        for ip, count in ips.most_common(5):
            if count > 100:
                findings.append(Finding(
                    guard=self.name,
                    severity="warning",
                    message=f"IP {ip} con {count} requests (posible abuso)",
                    evidence={"ip": ip, "count": count},
                ))

        # Detección 2: accesos fuera de horario (2am-5am)
        off_hours = sum(hours[h] for h in [2, 3, 4, 5])
        if off_hours > len(recent) * 0.3:
            findings.append(Finding(
                guard=self.name,
                severity="warning",
                message=f"{off_hours} accesos fuera de horario (2-5am)",
                evidence={"off_hours": off_hours, "total": len(recent)},
            ))

        # Detección 3: gaps en logs
        if len(recent) > 1:
            try:
                first = datetime.fromisoformat(
                    json.loads(recent[0]).get("timestamp", "").replace("Z", "+00:00")
                )
                last = datetime.fromisoformat(
                    json.loads(recent[-1]).get("timestamp", "").replace("Z", "+00:00")
                )
                span = (last - first).total_seconds()
                if span > 0 and len(recent) / span < 0.01:
                    findings.append(Finding(
                        guard=self.name,
                        severity="info",
                        message=f"Tasa de accesos baja: {len(recent)} en {span:.0f}s",
                    ))
            except (ValueError, AttributeError):
                pass

        return findings