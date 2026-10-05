"""
Atribución SDK — Cliente HTTP.

Uso:

    from atribucion_sdk import AtribucionClient

    client = AtribucionClient(api_key="ak_live_...")

    agent = client.register_agent(
        name="MiAgente",
        autonomy_level="semi-autonomo",
        proveedor_modelo="anthropic",
        operator_did="did:kronos:human:0x...",
        public_key_pem=pub_pem.decode(),
    )

    cert = client.record_action(
        agent_id=agent.agent_id,
        action="trade_executed",
        input={"symbol": "AAPL"},
        output={"status": "filled"},
        reasoning="Señal alcista.",
        autonomy_level="semi-autonomo",
        private_key_pem=priv_pem,
    )
"""

from __future__ import annotations

from typing import Any

import httpx

from atribucion_sdk.crypto import (
    sign_hybrid_pqc_placeholder,
    sign_payload,
)
from atribucion_sdk.types import (
    ActionResponse,
    AgentInfo,
    AgentRegistrationResponse,
    ProofResponse,
)


DEFAULT_BASE_URL = "https://api.atribucion.io"


class AtribucionClient:
    """Cliente oficial de Atribución."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "atribucion-sdk-python/0.1.0",
            },
            timeout=timeout,
        )

    def __enter__(self) -> "AtribucionClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    # ─── AGENTES ────────────────────────────────────────────────

    def register_agent(
        self,
        *,
        name: str,
        autonomy_level: str,
        proveedor_modelo: str,
        operator_did: str,
        public_key_pem: str,
        metadata: dict[str, Any] | None = None,
    ) -> AgentRegistrationResponse:
        """Registra un nuevo agente y devuelve su información."""
        response = self._client.post(
            "/v1/agents",
            json={
                "name": name,
                "autonomy_level": autonomy_level,
                "proveedor_modelo": proveedor_modelo,
                "operator_did": operator_did,
                "public_key_pem": public_key_pem,
                "metadata": metadata or {},
            },
        )
        response.raise_for_status()
        data = response.json()

        return AgentRegistrationResponse(
            agent_id=data["agent_id"],
            agent_did=data["agent_did"],
            contract_id=data["contract_id"],
            contract_url=data["contract_url"],
            created_at=data["created_at"],
            autonomy_level=data["autonomy_level"],
            colateral_krn=data["colateral_krn"],
            limite_dano_krn=data["limite_dano_krn"],
        )

    def get_agent(self, agent_id: str) -> AgentInfo:
        """Devuelve información pública de un agente."""
        response = self._client.get(f"/v1/agents/{agent_id}")
        response.raise_for_status()
        data = response.json()

        return AgentInfo(
            agent_id=data["agent_id"],
            agent_did=data["agent_did"],
            name=data["name"],
            autonomy_level=data["autonomy_level"],
            proveedor_modelo=data["proveedor_modelo"],
            created_at=data["created_at"],
            active=data["active"],
        )

    # ─── ACCIONES ───────────────────────────────────────────────

    def record_action(
        self,
        *,
        agent_id: str,
        action: str,
        input: dict[str, Any],
        output: dict[str, Any],
        autonomy_level: str,
        private_key_pem: bytes,
        reasoning: str | None = None,
        human_approval: dict[str, Any] | None = None,
    ) -> ActionResponse:
        """
        Registra una acción del agente y devuelve el certificado.

        Firma el payload localmente antes de enviarlo.
        """
        payload = {
            "action": action,
            "input": input,
            "output": output,
            "reasoning": reasoning,
            "autonomy_level": autonomy_level,
            "human_approval": human_approval,
        }

        sig_classic = sign_payload(private_key_pem, payload)
        sig_pqc = sign_hybrid_pqc_placeholder(payload)

        response = self._client.post(
            f"/v1/agents/{agent_id}/actions",
            json=payload,
            headers={
                "X-Agent-Signature": sig_classic,
                "X-Agent-Signature-PQC": sig_pqc,
            },
        )
        response.raise_for_status()
        data = response.json()

        return ActionResponse(
            certificate_id=data["certificate_id"],
            proof_url=data["proof_url"],
            compliance=data["compliance"],
            anchor=data["anchor"],
            timestamp_rfc3161=data["timestamp_rfc3161"],
            signature=data["signature"],
        )

    # ─── VERIFICACIÓN ───────────────────────────────────────────

    def verify_certificate(self, certificate_id: str) -> ProofResponse:
        """
        Verifica un certificado (público, sin auth).

        Nota: usa un cliente sin Authorization para reflejar
        que es un endpoint público.
        """
        with httpx.Client(base_url=self.base_url, timeout=30.0) as public:
            response = public.get(f"/v1/proofs/{certificate_id}")
            response.raise_for_status()
            data = response.json()

        return ProofResponse(
            certificate_id=data["certificate_id"],
            status=data["status"],
            issued_at=data["issued_at"],
            agent_did=data["agent_did"],
            action=data["action"],
            autonomy_level=data["autonomy_level"],
            hashes=data["hashes"],
            anchor=data["anchor"],
            timestamp=data["timestamp"],
            verification_url=data["verification_url"],
        )

    # ─── REPORTES ───────────────────────────────────────────────

    def get_monthly_report(self, period: str) -> dict[str, Any]:
        """Devuelve el informe mensual en JSON (period: YYYY-MM)."""
        response = self._client.get(f"/v1/reports/{period}")
        response.raise_for_status()
        return response.json()

    def download_monthly_report_pdf(self, period: str, path: str) -> None:
        """Descarga el informe mensual en PDF."""
        response = self._client.get(f"/v1/reports/{period}.pdf")
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)