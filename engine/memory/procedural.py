"""
Atribución Engine — Memoria procedural.

Almacena habilidades y procedimientos del agente:
- Cómo hacer X
- Pasos para Y
- Recetas y workflows
- Skills reutilizables

Es la memoria de "cómo hago las cosas".

Uso:
    mem = ProceduralMemory(agent_id="agt_123")
    skill = mem.define_skill(
        name="trade_stock",
        steps=[
            {"action": "fetch_price", "params": {"symbol": "AAPL"}},
            {"action": "check_risk", "params": {"max_loss": 100}},
            {"action": "execute", "params": {}},
        ],
    )
    skill = mem.get_skill("trade_stock")
    result = mem.execute_skill("trade_stock", handlers={...})
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4


logger = logging.getLogger(__name__)


@dataclass
class SkillStep:
    """Un paso de una skill."""

    action: str
    params: dict[str, Any] = field(default_factory=dict)
    condition: str | None = None
    on_error: str = "fail"  # fail | skip | retry


@dataclass
class Skill:
    """Una habilidad definida."""

    id: str
    name: str
    description: str
    steps: list[SkillStep]
    created_at: str
    updated_at: str
    tags: list[str] = field(default_factory=list)
    usage_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["steps"] = [asdict(s) if isinstance(s, SkillStep) else s for s in self.steps]
        return d

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


class ProceduralMemory:
    """Memoria procedural persistente."""

    def __init__(
        self,
        agent_id: str,
        state_dir: Path | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.state_dir = state_dir or (Path.home() / ".atribucion" / "memory")
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self._file = self.state_dir / f"procedural-{agent_id}.json"
        self.skills: dict[str, Skill] = {}
        self._load()

        logger.info(
            "ProceduralMemory cargada: %d skills (%s)",
            len(self.skills), agent_id,
        )

    # ─── DEFINE ────────────────────────────────────────────────

    def define_skill(
        self,
        name: str,
        description: str,
        steps: list[dict[str, Any]],
        tags: list[str] | None = None,
    ) -> Skill:
        """Define una nueva skill."""
        skill_steps = []
        for s in steps:
            if isinstance(s, SkillStep):
                skill_steps.append(s)
            else:
                skill_steps.append(SkillStep(
                    action=s.get("action", ""),
                    params=s.get("params", {}),
                    condition=s.get("condition"),
                    on_error=s.get("on_error", "fail"),
                ))

        now = datetime.now(timezone.utc).isoformat()
        existing = self.skills.get(name.lower().strip())

        skill = Skill(
            id=existing.id if existing else f"skill_{uuid4().hex[:12]}",
            name=name.lower().strip(),
            description=description,
            steps=skill_steps,
            created_at=existing.created_at if existing else now,
            updated_at=now,
            tags=tags or (existing.tags if existing else []),
            usage_count=existing.usage_count if existing else 0,
            success_count=existing.success_count if existing else 0,
            failure_count=existing.failure_count if existing else 0,
            avg_duration_ms=existing.avg_duration_ms if existing else 0.0,
        )

        self.skills[skill.name] = skill
        self._save()
        logger.info("Skill definida: %s (%d pasos)", skill.name, len(skill.steps))
        return skill

    def get_skill(self, name: str) -> Skill | None:
        return self.skills.get(name.lower().strip())

    def list_skills(self, tag: str | None = None) -> list[dict[str, Any]]:
        """Lista skills (resumen)."""
        skills = self.skills.values()
        if tag:
            skills = [s for s in skills if tag in s.tags]
        return [
            {
                "name": s.name,
                "description": s.description,
                "steps_count": len(s.steps),
                "usage_count": s.usage_count,
                "success_rate": round(s.success_rate, 2),
                "tags": s.tags,
            }
            for s in skills
        ]

    def remove_skill(self, name: str) -> bool:
        key = name.lower().strip()
        if key in self.skills:
            del self.skills[key]
            self._save()
            return True
        return False

    # ─── EXECUTE ───────────────────────────────────────────────

    def execute_skill(
        self,
        name: str,
        handlers: dict[str, Callable[[dict[str, Any]], Any]],
        initial_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Ejecuta una skill con handlers externos.

        handlers: dict mapping action → callable.
        """
        import time

        skill = self.get_skill(name)
        if not skill:
            return {"success": False, "error": f"Skill no encontrada: {name}"}

        start = time.time()
        context = dict(initial_context or {})
        results: list[dict[str, Any]] = []

        for i, step in enumerate(skill.steps):
            handler = handlers.get(step.action)
            if handler is None:
                if step.on_error == "skip":
                    results.append({
                        "step": i, "action": step.action,
                        "skipped": True, "reason": "sin handler",
                    })
                    continue
                return {
                    "success": False,
                    "error": f"Sin handler para acción: {step.action}",
                    "step_index": i,
                    "results": results,
                }

            try:
                merged_params = {**step.params, **context}
                result = handler(merged_params)
                context[f"step_{i}_result"] = result
                results.append({
                    "step": i, "action": step.action,
                    "success": True, "result": result,
                })
            except Exception as e:
                if step.on_error == "skip":
                    results.append({
                        "step": i, "action": step.action,
                        "skipped": True, "error": str(e),
                    })
                    continue
                if step.on_error == "retry":
                    try:
                        result = handler(step.params)
                        context[f"step_{i}_result"] = result
                        results.append({
                            "step": i, "action": step.action,
                            "success": True, "result": result,
                            "retried": True,
                        })
                        continue
                    except Exception as e2:
                        e = e2

                skill.failure_count += 1
                self._save()
                return {
                    "success": False,
                    "error": str(e),
                    "step_index": i,
                    "results": results,
                }

        elapsed_ms = (time.time() - start) * 1000
        skill.usage_count += 1
        skill.success_count += 1
        skill.avg_duration_ms = skill.avg_duration_ms * 0.8 + elapsed_ms * 0.2
        self._save()

        return {
            "success": True,
            "skill": name,
            "duration_ms": round(elapsed_ms, 2),
            "context": context,
            "results": results,
        }

    # ─── STATS ─────────────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        tags = Counter(t for s in self.skills.values() for t in s.tags)
        return {
            "total_skills": len(self.skills),
            "total_usages": sum(s.usage_count for s in self.skills.values()),
            "top_tags": dict(tags.most_common(5)),
            "avg_success_rate": (
                sum(s.success_rate for s in self.skills.values()) / len(self.skills)
                if self.skills else 0.0
            ),
        }

    def clear(self) -> None:
        self.skills = {}
        self._save()

    # ─── PERSISTENCIA ──────────────────────────────────────────

    def _save(self) -> None:
        data = {
            "agent_id": self.agent_id,
            "skills": {k: v.to_dict() for k, v in self.skills.items()},
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        self._file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _load(self) -> None:
        if not self._file.exists():
            return
        try:
            data = json.loads(self._file.read_text(encoding="utf-8"))
            for name, s in data.get("skills", {}).items():
                steps = [
                    SkillStep(**step) if isinstance(step, dict) else step
                    for step in s.get("steps", [])
                ]
                s["steps"] = steps
                self.skills[name] = Skill(**s)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning("Error cargando memoria procedural: %s", e)