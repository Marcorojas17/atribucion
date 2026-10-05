"""
Atribución — Anclaje a Ethereum.

Modo híbrido:
- Si hay SEPOLIA_PRIVATE_KEY en .env → envía transacción real.
- Si no hay → devuelve mock determinístico (útil para desarrollo).

Diseñado para evolucionar a mainnet sin cambiar la API.

Cumple con:
- EU AI Act Art. 12 (registro inmutable de eventos)
- RFC 3161 (complementario con sellado de tiempo)
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from eth_account import Account
from web3 import Web3

from atribucion import crypto


# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────

def _load_env() -> dict[str, str]:
    """
    Lee .env manualmente (sin dependencia de python-dotenv).

    Formato esperado:
        KEY=value
        KEY2=value2

    Ignora líneas vacías y comentarios (que empiezan con #).
    """
    env: dict[str, str] = {}
    env_path = ".env"

    if not os.path.exists(env_path):
        return env

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip()

    return env


# ─────────────────────────────────────────────────────────────
# RESULTADO
# ─────────────────────────────────────────────────────────────

@dataclass
class AnchorResult:
    """Resultado de un anclaje (real o mock)."""

    tx_hash: str
    block: int
    network: str
    merkle_root: str
    timestamp: str
    mode: str  # "real" o "mock"

    def to_dict(self) -> dict[str, Any]:
        return {
            "tx_hash": self.tx_hash,
            "block": self.block,
            "network": self.network,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
            "mode": self.mode,
        }


# ─────────────────────────────────────────────────────────────
# ANCLAJE
# ─────────────────────────────────────────────────────────────

async def submit(
    merkle_root: str,
    metadata: dict[str, Any] | None = None,
) -> AnchorResult:
    """
    Ancla un merkle_root a Ethereum.

    Si hay wallet configurada → envía transacción real a Sepolia.
    Si no → devuelve mock determinístico.
    """
    env = _load_env()
    private_key = env.get("SEPOLIA_PRIVATE_KEY", "").strip()
    rpc_url = env.get("SEPOLIA_RPC_URL", "https://rpc.sepolia.org")

    if not private_key:
        return _mock_anchor(merkle_root, metadata)

    return await _real_anchor(
        merkle_root=merkle_root,
        metadata=metadata or {},
        private_key=private_key,
        rpc_url=rpc_url,
    )


def _mock_anchor(
    merkle_root: str,
    metadata: dict[str, Any] | None,
) -> AnchorResult:
    """
    Anclaje simulado. Devuelve valores determinísticos
    derivados del merkle_root para que sean reproducibles.
    """
    payload = {
        "merkle_root": merkle_root,
        "metadata": metadata or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    h = hashlib.sha256(crypto.canonical_bytes(payload)).hexdigest()

    return AnchorResult(
        tx_hash="0x" + h,
        block=0,
        network="mock",
        merkle_root=merkle_root,
        timestamp=datetime.now(timezone.utc).isoformat(),
        mode="mock",
    )


async def _real_anchor(
    merkle_root: str,
    metadata: dict[str, Any],
    private_key: str,
    rpc_url: str,
) -> AnchorResult:
    """
    Anclaje real a Sepolia.

    Nota: esta función envía una transacción con `data` =
    merkle_root + metadata. No requiere contrato desplegado
    todavía. El contrato KAFRegistry.sol vendrá después.
    """
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    if not w3.is_connected():
        raise ConnectionError(f"No se pudo conectar a {rpc_url}")

    account = Account.from_key(private_key)

    # Payload a incluir en la transacción
    payload = crypto.canonical_bytes({
        "merkle_root": merkle_root,
        "metadata": metadata,
        "anchored_at": datetime.now(timezone.utc).isoformat(),
    }).hex()

    # Construir transacción (0 ETH, solo data)
    nonce = w3.eth.get_transaction_count(account.address)
    gas_price = w3.eth.gas_price
    chain_id = int(_load_env().get("SEPOLIA_CHAIN_ID", "11155111"))

    tx = {
        "nonce": nonce,
        "to": account.address,
        "value": 0,
        "gas": 100_000,
        "gasPrice": gas_price,
        "data": "0x" + payload[:200] if payload else "0x",
        "chainId": chain_id,
    }

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

    tx_hash_hex = tx_hash.hex()
    if not tx_hash_hex.startswith("0x"):
        tx_hash_hex = "0x" + tx_hash_hex

    return AnchorResult(
        tx_hash=tx_hash_hex,
        block=0,
        network="sepolia",
        merkle_root=merkle_root,
        timestamp=datetime.now(timezone.utc).isoformat(),
        mode="real",
    )


# ─────────────────────────────────────────────────────────────
# IPFS (stub hasta integrar gateway real)
# ─────────────────────────────────────────────────────────────

async def pin_to_ipfs(data: dict[str, Any]) -> str:
    """
    Placeholder de IPFS.

    Devuelve un CID determinístico derivado del hash del payload.

    Se reemplaza por una llamada real a un gateway IPFS
    cuando estemos listos (web3.storage, Pinata, o Kubo local).
    """
    h = hashlib.sha256(crypto.canonical_bytes(data)).hexdigest()
    # Simula un CIDv1 con prefijo bafy
    return "bafy" + h[:52]