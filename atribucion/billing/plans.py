"""
Atribución — Planes de suscripción.

Define los 3 planes del producto con sus límites, precios y
características.

| Plan  | Precio      | Agentes | Acciones  | SLA      |
|-------|-------------|---------|-----------|----------|
| Free  | €0/mes      | 1       | 1.000/mes | Sin SLA  |
| Pro   | €990/mes    | 10      | ∞         | 99.5%    |
| Bank  | €9.900/mes  | ∞       | ∞         | 99.99%   |
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal


# ─────────────────────────────────────────────────────────────
# MODELO
# ─────────────────────────────────────────────────────────────

PlanID = Literal["free", "pro", "bank"]


@dataclass(frozen=True)
class Plan:
    """Plan de suscripción."""

    id: PlanID
    name: str
    description: str
    price_eur: Decimal
    price_mxn: Decimal
    agent_limit: int
    actions_limit: int | None  # None = ilimitado
    sla_uptime: str
    support: str
    features: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_free(self) -> bool:
        return self.price_eur == Decimal("0")

    @property
    def is_enterprise(self) -> bool:
        return self.id == "bank"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price_eur": str(self.price_eur),
            "price_mxn": str(self.price_mxn),
            "agent_limit": self.agent_limit,
            "actions_limit": self.actions_limit,
            "sla_uptime": self.sla_uptime,
            "support": self.support,
            "features": list(self.features),
        }


# ─────────────────────────────────────────────────────────────
# CATÁLOGO
# ─────────────────────────────────────────────────────────────

PLANS: dict[PlanID, Plan] = {
    "free": Plan(
        id="free",
        name="Free",
        description="Para probar Atribución sin compromiso.",
        price_eur=Decimal("0"),
        price_mxn=Decimal("0"),
        agent_limit=1,
        actions_limit=1_000,
        sla_uptime="Sin SLA",
        support="Comunidad",
        features=(
            "1 agente",
            "1.000 acciones/mes",
            "Certificado verificable",
            "Anclaje en Sepolia (testnet)",
            "Sello de tiempo mock",
        ),
    ),
    "pro": Plan(
        id="pro",
        name="Pro",
        description="Para empresas con agentes en producción.",
        price_eur=Decimal("990"),
        price_mxn=Decimal("19900"),
        agent_limit=10,
        actions_limit=None,
        sla_uptime="99.5%",
        support="Email 24h",
        features=(
            "10 agentes",
            "Acciones ilimitadas",
            "Anclaje en Ethereum mainnet",
            "Sello DigiCert RFC 3161",
            "Informe PDF mensual",
            "Verificador público",
            "Soporte prioritario",
        ),
    ),
    "bank": Plan(
        id="bank",
        name="Bank",
        description="Para bancos, gobiernos e infraestructura crítica.",
        price_eur=Decimal("9900"),
        price_mxn=Decimal("199000"),
        agent_limit=999_999,
        actions_limit=None,
        sla_uptime="99.99%",
        support="24/7 + Slack",
        features=(
            "Agentes ilimitados",
            "SLA contractual 99.99%",
            "HSM dedicado",
            "Auditoría trimestral externa",
            "Compliance CNBV + eIDAS",
            "Onboarding asistido",
            "Gestor de cuenta dedicado",
        ),
    ),
}


# ─────────────────────────────────────────────────────────────
# API PÚBLICA
# ─────────────────────────────────────────────────────────────

def get_plan(plan_id: str) -> Plan:
    """
    Obtiene un plan por ID.

    Lanza KeyError si el plan no existe.
    """
    if plan_id not in PLANS:
        raise KeyError(f"Plan no encontrado: {plan_id}")
    return PLANS[plan_id]


def list_plans() -> list[Plan]:
    """Devuelve todos los planes ordenados por precio."""
    return sorted(PLANS.values(), key=lambda p: p.price_eur)