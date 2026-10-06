"""
Atribución Engine — Reflection.

Auto-crítica y mejora continua. El agente evalúa su propio
trabajo y extrae lecciones para futuras ejecuciones.

Cumple con: mejora continua, ISO 42001, NIST AI RMF.

Uso:
    reflector = Reflector()
    critique = reflector.reflect(
        task="Trade ejecutado",
        result={"profit": 150},
        llm_call=lambda prompt: llm.generate(prompt),
    )
    print(critique.lessons)
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4


logger = logging.getLogger(__name__)


@dataclass
class Critique:
    """Resultado de una reflexión."""

    id: str
    task: str
    result_summary: str
    what_worked: list[str]
    what_failed: list[str]
    lessons: list[str]
    next_actions: list[str]
    score: float
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Reflector:
    """Sistema de reflexión y auto-crítica."""

    def __init__(self) -> None:
        self.critiques: list[Critique] = []
        self.lessons_learned: list[str] = []
        logger.info("Reflector listo")

    # ─── REFLECT ───────────────────────────────────────────────

    def reflect(
        self,
        task: str,
        result: Any,
        llm_call: Callable[[str], str],
        expected: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Critique:
        """
        Reflexiona sobre el resultado de una tarea.

        llm_call: función que recibe prompt y devuelve texto.
        """
        result_str = str(result)[:1000]

        # Análisis guiado por LLM
        what_worked = self._analyze_successes(task, result_str, llm_call)
        what_failed = self._analyze_failures(task, result_str, expected, llm_call)
        lessons = self._extract_lessons(task, what_worked, what_failed, llm_call)
        next_actions = self._suggest_actions(lessons, llm_call)

        score = self._score(what_worked, what_failed)

        critique = Critique(
            id=f"crit_{uuid4().hex[:12]}",
            task=task,
            result_summary=result_str[:200],
            what_worked=what_worked,
            what_failed=what_failed,
            lessons=lessons,
            next_actions=next_actions,
            score=score,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )

        self.critiques.append(critique)
        self.lessons_learned.extend(lessons)

        logger.info(
            "Reflexión completada: %s (score=%.2f, %d lecciones)",
            critique.id, score, len(lessons),
        )
        return critique

    # ─── INTERNAL ──────────────────────────────────────────────

    def _analyze_successes(
        self, task: str, result: str, llm: Callable[[str], str]
    ) -> list[str]:
        prompt = (
            f"Tarea: {task}\n"
            f"Resultado: {result}\n\n"
            f"Lista 2-3 cosas que funcionaron bien, una por línea. "
            f"Solo las líneas, sin numeración ni bullets."
        )
        return self._parse_lines(llm(prompt), max_items=3)

    def _analyze_failures(
        self,
        task: str,
        result: str,
        expected: str | None,
        llm: Callable[[str], str],
    ) -> list[str]:
        expected_str = expected or "(no especificado)"
        prompt = (
            f"Tarea: {task}\n"
            f"Resultado: {result}\n"
            f"Esperado: {expected_str}\n\n"
            f"Lista 2-3 cosas que NO funcionaron o podrían mejorar, "
            f"una por línea."
        )
        return self._parse_lines(llm(prompt), max_items=3)

    def _extract_lessons(
        self,
        task: str,
        successes: list[str],
        failures: list[str],
        llm: Callable[[str], str],
    ) -> list[str]:
        prompt = (
            f"Tarea: {task}\n"
            f"Éxitos: {successes}\n"
            f"Fallos: {failures}\n\n"
            f"Extrae 2-3 lecciones generales aplicables a futuras "
            f"tareas similares, una por línea."
        )
        return self._parse_lines(llm(prompt), max_items=3)

    def _suggest_actions(
        self, lessons: list[str], llm: Callable[[str], str]
    ) -> list[str]:
        if not lessons:
            return []
        prompt = (
            f"Basado en estas lecciones:\n" +
            "\n".join(f"- {l}" for l in lessons) +
            "\n\nSugiere 1-2 acciones concretas para la próxima vez, "
            "una por línea."
        )
        return self._parse_lines(llm(prompt), max_items=2)

    def _parse_lines(self, text: str, max_items: int = 3) -> list[str]:
        """Convierte output del LLM en lista."""
        lines = []
        for line in text.split("\n"):
            line = line.strip()
            # Quitar bullets/números
            line = line.lstrip("-•*0123456789. )")
            line = line.strip()
            if line and len(line) > 5:
                lines.append(line)
            if len(lines) >= max_items:
                break
        return lines

    def _score(self, successes: list[str], failures: list[str]) -> float:
        """Score 0-1 basado en éxitos vs fallos."""
        s = len(successes)
        f = len(failures)
        total = s + f
        if total == 0:
            return 0.5
        return round(s / total, 2)

    # ─── LESSONS ───────────────────────────────────────────────

    def get_lessons(self, limit: int = 20) -> list[str]:
        return self.lessons_learned[-limit:]

    def get_critiques(self, limit: int = 10) -> list[dict[str, Any]]:
        return [c.to_dict() for c in self.critiques[-limit:]]

    def get_stats(self) -> dict[str, Any]:
        if not self.critiques:
            return {
                "total_reflections": 0,
                "avg_score": 0.0,
                "total_lessons": 0,
            }
        return {
            "total_reflections": len(self.critiques),
            "avg_score": round(
                sum(c.score for c in self.critiques) / len(self.critiques), 2
            ),
            "total_lessons": len(self.lessons_learned),
        }