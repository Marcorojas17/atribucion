"""
KAF — Auditor automático.

Evalúa un agente contra los 47 controles KAF y devuelve
qué nivel de certificación alcanza.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


# ─────────────────────────────────────────────────────────────
# MODELOS
# ─────────────────────────────────────────────────────────────

@dataclass
class ControlResult:
    """Resultado de evaluar un control."""

    control_id: str
    name: str
    passed: bool
    severity: str
    auto_auditable: bool
    evidence: str = ""


@dataclass
class KAFAssessment:
    """Resultado completo de una evaluación KAF."""

    agent_id: str
    level_achieved: str  # KAF-1 / KAF-2 / KAF-3 / KAF-4 / none
    controls_passed: int
    controls_total: int
    results: list[ControlResult] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "level_achieved": self.level_achieved,
            "controls_passed": self.controls_passed,
            "controls_total": self.controls_total,
            "results": [
                {
                    "control_id": r.control_id,
                    "name": r.name,
                    "passed": r.passed,
                    "severity": r.severity,
                    "auto_auditable": r.auto_auditable,
                    "evidence": r.evidence,
                }
                for r in self.results
            ],
            "timestamp": self.timestamp,
        }


# ─────────────────────────────────────────────────────────────
# AUDITOR
# ─────────────────────────────────────────────────────────────

KAF_CONTROLS_PATH = Path(__file__).resolve().parents[1] / "controls" / "controls.yaml"


class KAFAuditor:
    """
    Auditor automático de KAF.

    Uso:
        auditor = KAFAuditor()
        assessment = await auditor.assess(agent_id="agt_123")
        print(f"Nivel: {assessment.level_achieved}")
    """

    LEVEL_REQUIREMENTS: dict[str, list[str]] = {
        "KAF-1": [
            "KAF-1.1", "KAF-1.2",
            "KAF-3.1", "KAF-3.2",
            "KAF-9.1",
        ],
        "KAF-2": [
            "KAF-2.1", "KAF-2.2", "KAF-2.3", "KAF-2.4",
            "KAF-3.3", "KAF-3.4",
            "KAF-4.1", "KAF-5.1", "KAF-5.2",
            "KAF-7.3",
        ],
        "KAF-3": [
            "KAF-6.1", "KAF-6.2", "KAF-6.3", "KAF-6.4", "KAF-6.5",
            "KAF-7.1",
            "KAF-8.1", "KAF-8.2", "KAF-8.3",
            "KAF-9.3", "KAF-9.4",
            "KAF-10.2", "KAF-10.3",
            "KAF-12.3",
        ],
        "KAF-4": [
            "KAF-9.2",
            "KAF-11.1", "KAF-11.2", "KAF-11.3",
            "KAF-12.1", "KAF-12.2", "KAF-12.4",
        ],
    }

    def __init__(self) -> None:
        self.controls = self._load_controls()

    def _load_controls(self) -> dict[str, dict[str, Any]]:
        """Carga los controles desde YAML."""
        if not KAF_CONTROLS_PATH.exists():
            return {}

        with KAF_CONTROLS_PATH.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        controls: dict[str, dict[str, Any]] = {}
        for domain in data.get("domains", []):
            for ctrl in domain.get("controls", []):
                controls[ctrl["id"]] = {
                    **ctrl,
                    "domain": domain["name"],
                }
        return controls

    async def assess(self, agent_id: str) -> KAFAssessment:
        """
        Evalúa un agente y determina su nivel KAF.

        En producción consulta la DB. Por ahora evalúa con
        evidencia simulada (todos los auto_auditables pasan).
        """
        results: list[ControlResult] = []

        for ctrl_id, ctrl in self.controls.items():
            passed = await self._evaluate_control(agent_id, ctrl)
            results.append(ControlResult(
                control_id=ctrl_id,
                name=ctrl["name"],
                passed=passed,
                severity=ctrl["severity"],
                auto_auditable=ctrl.get("auto_auditable", False),
                evidence="Evaluado automáticamente" if passed else "",
            ))

        passed_ids = {r.control_id for r in results if r.passed}

        # Determinar nivel máximo alcanzado
        level = "none"
        for candidate in ["KAF-4", "KAF-3", "KAF-2", "KAF-1"]:
            required = set(self.LEVEL_REQUIREMENTS[candidate])
            # Niveles inferiores deben estar completos
            all_required: set[str] = set()
            for lvl in self.LEVEL_REQUIREMENTS:
                all_required.update(self.LEVEL_REQUIREMENTS[lvl])
                if lvl == candidate:
                    break

            if all_required.issubset(passed_ids):
                level = candidate
                break

        return KAFAssessment(
            agent_id=agent_id,
            level_achieved=level,
            controls_passed=len(passed_ids),
            controls_total=len(self.controls),
            results=results,
        )

    async def _evaluate_control(self, agent_id: str, ctrl: dict[str, Any]) -> bool:
        """
        Evalúa un control individual.

        En producción, aquí se consulta la DB y se verifica
        la evidencia real.
        """
        # Placeholder: los controles auto_auditables pasan por defecto.
        return ctrl.get("auto_auditable", False)