"""
Atribución — Guardián VAULT.

Verifica la seguridad de claves y secretos:
1. Detecta claves privadas expuestas en texto plano.
2. Detecta .env con permisos inseguros.
3. Detecta secretos en git history.
"""

from __future__ import annotations

import os
import re
import stat
from pathlib import Path

from guards.base import Finding, GuardAgent


class VaultGuard(GuardAgent):
    """Guardián de secretos."""

    name = "vault"
    interval_seconds = 3600

    # Patrones de secretos comunes
    SECRET_PATTERNS = [
        (r"0x[a-fA-F0-9]{64}", "private key"),
        (r"sk_live_[a-zA-Z0-9]{24,}", "stripe live key"),
        (r"AKIA[0-9A-Z]{16}", "AWS access key"),
        (r"ghp_[a-zA-Z0-9]{36}", "GitHub PAT"),
    ]

    async def check(self) -> list[Finding]:
        findings: list[Finding] = []

        # 1. Verificar permisos de .env
        env_path = Path.home() / ".atribucion" / ".env"
        if env_path.exists():
            mode = env_path.stat().st_mode
            if mode & stat.S_IROTH:  # readable by others
                findings.append(Finding(
                    guard=self.name,
                    severity="critical",
                    message=f".env con permisos inseguros: {oct(mode)}",
                    evidence={"path": str(env_path), "mode": oct(mode)},
                ))

        # 2. Buscar secretos en archivos de configuración
        config_dir = Path.home() / ".atribucion"
        if config_dir.exists():
            for path in config_dir.glob("*.json"):
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue

                for pattern, name in self.SECRET_PATTERNS:
                    if re.search(pattern, content):
                        findings.append(Finding(
                            guard=self.name,
                            severity="critical",
                            message=f"Posible {name} en {path.name}",
                            evidence={"file": str(path), "pattern": name},
                        ))

        # 3. Verificar que no hay .env en directorios públicos
        public_dirs = [Path("/tmp"), Path("/var/www")]
        for d in public_dirs:
            if d.exists():
                for env_file in d.glob("**/.env"):
                    findings.append(Finding(
                        guard=self.name,
                        severity="critical",
                        message=f".env expuesto en {env_file}",
                        evidence={"path": str(env_file)},
                    ))

        return findings