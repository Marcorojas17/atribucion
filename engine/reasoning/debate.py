"""
Atribución Engine — Debate multi-agente.

Múltiples agentes debaten una pregunta. Cada uno defiende
una postura. Un moderador sintetiza.

Sirve para:
- Reducir sesgos individuales
- Explorar múltiples perspectivas
- Generar mejores decisiones en casos ambiguos

Uso:
    debate = Debate()
    debate.add_debater("optimista", "Eres optimista...")
    debate.add_debater("pesimista", "Eres pesimista...")
    debate.add_debater("realista", "Eres realista...")
    result = debate.run("¿Debo invertir en AAPL?", llm_call=...)
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4


logger = logging.getLogger(__name__)


@dataclass
class Debater:
    """Un participante del debate."""

    name: str
    system_prompt: str
    stance: str = "neutral"


@dataclass
class DebateTurn:
    """Un turno de un debater."""

    debater: str
    round: int
    content: str
    timestamp: str


@dataclass
class DebateResult:
    """Resultado completo de un debate."""

    id: str
    question: str
    turns: list[DebateTurn]
    synthesis: str
    consensus: str | None
    dissent: list[str]
    rounds: int
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "rounds": self.rounds,
            "turns": [asdict(t) for t in self.turns],
            "synthesis": self.synthesis,
            "consensus": self.consensus,
            "dissent": self.dissent,
            "timestamp": self.timestamp,
        }


class Debate:
    """Orquestador de debates multi-agente."""

    def __init__(self, max_rounds: int = 2) -> None:
        self.max_rounds = max_rounds
        self.debaters: list[Debater] = []
        self.history: list[DebateResult] = []
        logger.info("Debate listo (max_rounds=%d)", max_rounds)

    # ─── SETUP ─────────────────────────────────────────────────

    def add_debater(
        self,
        name: str,
        system_prompt: str,
        stance: str = "neutral",
    ) -> None:
        self.debaters.append(Debater(
            name=name,
            system_prompt=system_prompt,
            stance=stance,
        ))
        logger.info("Debater añadido: %s (%s)", name, stance)

    def clear_debaters(self) -> None:
        self.debaters = []

    # ─── RUN ───────────────────────────────────────────────────

    def run(
        self,
        question: str,
        llm_call: Callable[[str, str], str],
        metadata: dict[str, Any] | None = None,
    ) -> DebateResult:
        """
        Ejecuta un debate completo.

        llm_call: función (system_prompt, user_prompt) → str.
        """
        if len(self.debaters) < 2:
            raise ValueError("Se requieren al menos 2 debaters")

        turns: list[DebateTurn] = []

        for round_num in range(1, self.max_rounds + 1):
            for debater in self.debaters:
                content = self._ask_debater(
                    debater=debater,
                    question=question,
                    previous_turns=turns,
                    round_num=round_num,
                    llm_call=llm_call,
                )
                turns.append(DebateTurn(
                    debater=debater.name,
                    round=round_num,
                    content=content,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                ))

        synthesis, consensus, dissent = self._synthesize(
            question, turns, llm_call,
        )

        result = DebateResult(
            id=f"debate_{uuid4().hex[:12]}",
            question=question,
            turns=turns,
            synthesis=synthesis,
            consensus=consensus,
            dissent=dissent,
            rounds=self.max_rounds,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )
        self.history.append(result)
        logger.info(
            "Debate completado: %s (%d turnos)", result.id, len(turns),
        )
        return result

    # ─── INTERNAL ──────────────────────────────────────────────

    def _ask_debater(
        self,
        debater: Debater,
        question: str,
        previous_turns: list[DebateTurn],
        round_num: int,
        llm_call: Callable[[str, str], str],
    ) -> str:
        context = ""
        if previous_turns:
            context = "Turnos previos:\n" + "\n".join(
                f"[{t.debater} r{t.round}]: {t.content[:300]}"
                for t in previous_turns[-6:]
            )

        user_prompt = (
            f"Pregunta: {question}\n\n"
            f"{context}\n\n"
            f"Ronda {round_num}. Da tu posición desde tu perspectiva. "
            f"Sé específico y breve (máximo 150 palabras)."
        )
        return llm_call(debater.system_prompt, user_prompt).strip()

    def _synthesize(
        self,
        question: str,
        turns: list[DebateTurn],
        llm_call: Callable[[str, str], str],
    ) -> tuple[str, str | None, list[str]]:
        """Sintetiza el debate en una conclusión."""
        all_turns = "\n".join(
            f"[{t.debater}]: {t.content}" for t in turns
        )

        system = (
            "Eres un moderador imparcial. Sintetizas debates "
            "extrayendo el consenso y los puntos de disenso."
        )
        user = (
            f"Pregunta: {question}\n\n"
            f"Turnos del debate:\n{all_turns}\n\n"
            f"Proporciona:\n"
            f"1. SÍNTESIS: resumen equilibrado en 3-4 frases.\n"
            f"2. CONSENSO: la conclusión si hay acuerdo (o 'ninguno').\n"
            f"3. DISENSO: puntos donde no hay acuerdo, uno por línea."
        )

        response = llm_call(system, user)

        synthesis = self._extract_section(response, "SÍNTESIS", "CONSENSO")
        consensus = self._extract_section(response, "CONSENSO", "DISENSO")
        dissent_text = self._extract_section(response, "DISENSO", None)
        dissent = [
            l.strip().lstrip("-•*0123456789. )")
            for l in dissent_text.split("\n")
            if l.strip() and len(l.strip()) > 5
        ][:5]

        if consensus and consensus.lower().startswith("ninguno"):
            consensus = None

        return synthesis or response, consensus, dissent

    def _extract_section(
        self,
        text: str,
        start_marker: str,
        end_marker: str | None,
    ) -> str:
        """Extrae una sección entre dos marcadores."""
        upper = text.upper()
        start_idx = upper.find(start_marker.upper())
        if start_idx == -1:
            return ""
        start_idx = text.find(":", start_idx) + 1
        if end_marker:
            end_idx = upper.find(end_marker.upper(), start_idx)
            if end_idx == -1:
                end_idx = len(text)
        else:
            end_idx = len(text)
        return text[start_idx:end_idx].strip()

    # ─── INFO ──────────────────────────────────────────────────

    def get_history(self, limit: int = 10) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self.history[-limit:]]

    def get_stats(self) -> dict[str, Any]:
        return {
            "debaters": len(self.debaters),
            "total_debates": len(self.history),
            "max_rounds": self.max_rounds,
        }