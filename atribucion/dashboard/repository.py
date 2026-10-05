"""
Atribución — Repositorios de persistencia.

Implementación in-memory por ahora. Cuando haya Postgres
disponible, se reemplaza por SQLAlchemy sin cambiar la API.

Los métodos son async porque en producción consultan la DB.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


# ─────────────────────────────────────────────────────────────
# STORAGE EN DISCO (JSON)
# ─────────────────────────────────────────────────────────────

DATA_DIR = Path.home() / ".atribucion"
DATA_DIR.mkdir(exist_ok=True)


def _load_json(name: str) -> dict[str, Any]:
    path = DATA_DIR / f"{name}.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_json(name: str, data: dict[str, Any]) -> None:
    path = DATA_DIR / f"{name}.json"
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _serialize(obj: Any) -> dict[str, Any]:
    """Serializa dataclass, pydantic o dict."""
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if isinstance(obj, dict):
        return obj
    raise TypeError(f"No se puede serializar: {type(obj)}")


# ─────────────────────────────────────────────────────────────
# TENANTS
# ─────────────────────────────────────────────────────────────

class TenantRepository:
    """Persistencia de tenants."""

    _file = "tenants"

    async def save(self, tenant: Any) -> None:
        data = _load_json(self._file)
        payload = _serialize(tenant)
        data[payload["id"]] = payload
        _save_json(self._file, data)

    async def get(self, tenant_id: str) -> Any | None:
        data = _load_json(self._file)
        record = data.get(tenant_id)
        if not record:
            return None

        # Devolver como objeto simple con acceso por atributo
        from atribucion.onboarding.flow import Tenant
        return Tenant(
            id=record["id"],
            email=record["email"],
            did=record["did"],
            plan_id=record["plan_id"],
            created_at=record["created_at"],
            onboarding_step=record.get("onboarding_step", "account"),
            api_key=record.get("api_key"),
            api_key_created_at=record.get("api_key_created_at"),
            metadata=record.get("metadata", {}),
        )

    async def delete(self, tenant_id: str) -> None:
        data = _load_json(self._file)
        data.pop(tenant_id, None)
        _save_json(self._file, data)

    async def count(self) -> int:
        return len(_load_json(self._file))


# ─────────────────────────────────────────────────────────────
# AGENTS
# ─────────────────────────────────────────────────────────────

class AgentRepository:
    """Persistencia de agentes."""

    _file = "agents"

    async def save(self, agent: Any) -> None:
        data = _load_json(self._file)
        payload = _serialize(agent)
        data[payload["agent_id"]] = payload
        _save_json(self._file, data)

    async def get(self, agent_id: str) -> dict[str, Any] | None:
        return _load_json(self._file).get(agent_id)

    async def get_by_id(self, tenant_id: str, agent_id: str) -> dict[str, Any] | None:
        record = _load_json(self._file).get(agent_id)
        if not record or record.get("tenant_id") != tenant_id:
            return None
        return record

    async def count_by_tenant(self, tenant_id: str) -> int:
        data = _load_json(self._file)
        return sum(1 for a in data.values() if a.get("tenant_id") == tenant_id)

    async def delete(self, agent_id: str) -> None:
        data = _load_json(self._file)
        data.pop(agent_id, None)
        _save_json(self._file, data)


# ─────────────────────────────────────────────────────────────
# CERTIFICATES
# ─────────────────────────────────────────────────────────────

class CertificateRepository:
    """Persistencia de certificados emitidos."""

    _file = "certificates"

    async def save(
        self,
        certificate_id: str,
        tenant_id: str,
        agent_did: str,
        credential: Any,
        anchor_tx: str,
        tsa_token: str,
    ) -> None:
        data = _load_json(self._file)
        data[certificate_id] = {
            "certificate_id": certificate_id,
            "tenant_id": tenant_id,
            "agent_did": agent_did,
            "credential": _serialize(credential),
            "anchor_tx": anchor_tx,
            "tsa_token": tsa_token,
        }
        _save_json(self._file, data)

    async def get(self, certificate_id: str) -> dict[str, Any] | None:
        return _load_json(self._file).get(certificate_id)

    async def count_by_tenant(self, tenant_id: str) -> int:
        data = _load_json(self._file)
        return sum(1 for c in data.values() if c.get("tenant_id") == tenant_id)