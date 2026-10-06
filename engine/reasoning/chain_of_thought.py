"""
Atribución Engine — Chain of Thought (CoT).

Razonamiento paso a paso. Descompone una pregunta en
pensamientos intermedios antes de llegar a la conclusión.

Cumple con EU AI Act Art. 22 (explicabilidad de decisiones).

Uso:
    cot = ChainOfThought()
    result = cot.reason(
        question="¿Debo invertir en AAPL?",
        llm_call=lambda prompt: llm.generate(prompt),
    )
    print(result.conclusion)
    print(result.steps)
"""

from __future__ import annotations

import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4


logger = logging.getLogger(__name__)


@dataclass
class ThoughtStep:
    """Un paso del razonamiento."""

    index: int
    content: str
    type: str = "thought"  # thought | observation | conclusion
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CoTResult:
    """Resultado completo de un razonamiento CoT."""

    id: str
    question: str
    steps: list[ThoughtStep]
    conclusion: str
    confidence: float
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "steps": [s.to_dict() for s in self.steps],
            "conclusion": self.conclusion,
            "confidence": round(self.confidence, 3),
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    def to_reasoning_str(self) -> str:
        """Formato legible para incluir en certificados."""
        lines = [f"Pregunta: {self.question}"]
        for step in self.steps:
            lines.append(f"  [{step.index}] {step.content}")
        lines.append(f"Conclusión: {self.conclusion}")
        lines.append(f"Confianza: {self.confidence:.0%}")
        return "\n".join(lines)


class ChainOfThought:
    """Razonamiento paso a paso."""

    def __init__(self, max_steps: int = 8) -> None:
        self.max_steps = max_steps
        self.history: list[CoTResult] = []
        logger.info("ChainOfThought listo (max_steps=%d)", max_steps)

    # ─── REASON ────────────────────────────────────────────────

    def reason(
        self,
        question: str,
        llm_call: Callable[[str], str],
        metadata: dict[str, Any] | None = None,
    ) -> CoTResult:
        """
        Ejecuta razonamiento CoT.

        llm_call: función que recibe un prompt y devuelve texto.
        """
        steps: list[ThoughtStep] = []

        # Paso 1: comprensión
        understanding = self._understand(question, llm_call)
        steps.append(ThoughtStep(
            index=1,
            content=understanding,
            type="thought",
        ))

        # Pasos 2-N: razonamiento iterativo
        for i in range(2, self.max_steps + 1):
            prompt = self._build_step_prompt(question, steps)
            thought = llm_call(prompt).strip()

            if self._is_conclusion(thought):
                break

            steps.append(ThoughtStep(
                index=i,
                content=thought,
                type="thought",
            ))

        # Paso final: conclusión
        conclusion = self._conclude(question, steps, llm_call)
        steps.append(ThoughtStep(
            index=len(steps) + 1,
            content=conclusion,
            type="conclusion",
        ))

        confidence = self._estimate_confidence(steps)

        result = CoTResult(
            id=f"cot_{uuid4().hex[:12]}",
            question=question,
            steps=steps,
            conclusion=conclusion,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )
        self.history.append(result)
        logger.info(
            "CoT completado: %s (%d pasos, %.0f%% confianza)",
            result.id, len(steps), confidence * 100,
        )
        return result

    # ─── INTERNAL ──────────────────────────────────────────────

    def _understand(self, question: str, llm: Callable[[str], str]) -> str:
        prompt = (
            f"Analiza esta pregunta y explica qué se está pidiendo "
            f"exactamente, en 2-3 frases:\n\n{question}"
        )
        return llm(prompt).strip()

    def _build_step_prompt(
        self,
        question: str,
        steps: list[ThoughtStep],
    ) -> str:
        reasoning_so_far = "\n".join(
            f"[{s.index}] {s.content}" for s in steps
        )
        return (
            f"Pregunta original: {question}\n\n"
            f"Razonamiento hasta ahora:\n{reasoning_so_far}\n\n"
            f"Continúa el razonamiento con el siguiente paso lógico. "
            f"Si ya tienes suficiente información para concluir, "
            f"responde empezando con 'CONCLUSIÓN:'."
        )

    def _is_conclusion(self, thought: str) -> bool:
        return thought.upper().startswith("CONCLUSIÓN:")

    def _conclude(
        self,
        question: str,
        steps: list[ThoughtStep],
        llm: Callable[[str], str],
    ) -> str:
        reasoning_so_far = "\n".join(
            f"[{s.index}] {s.content}" for s in steps
        )
        prompt = (
            f"Pregunta: {question}\n\n"
            f"Razonamiento completo:\n{reasoning_so_far}\n\n"
            f"Da la conclusión final en 1-2 frases claras y directas."
        )
        response = llm(prompt).strip()
        # Limpiar prefijo "CONCLUSIÓN:" si lo incluye
        return re.sub(r"^CONCLUSI[ÓO]N:\s*", "", response, flags=re.IGNORECASE)

    def _estimate_confidence(self, steps: list[ThoughtStep]) -> float:
        """
        Estima confianza del razonamiento.

        Heurística simple:
        - Más pasos = mayor confianza (hasta 5 pasos).
        - Presencia de conclusión clara = +0.2.
        """
        base = min(1.0, len([s for s in steps if s.type == "thought"]) / 5)
        if any(s.type == "conclusion" for s in steps):
            base = min(1.0, base + 0.2)
        return round(base, 2)

    # ─── HISTORY ───────────────────────────────────────────────

    def get_history(self, limit: int = 10) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self.history[-limit:]]

    def clear_history(self) -> None:
        self.history = []