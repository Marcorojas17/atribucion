"""
Atribución — Deploy de AttributionRegistry a Sepolia.

Uso:
    python contracts/deploy/deploy_sepolia.py

Requiere en .env:
    SEPOLIA_RPC_URL=https://rpc.sepolia.org
    SEPOLIA_PRIVATE_KEY=0x...
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from eth_account import Account
from web3 import Web3


# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "contracts" / "AttributionRegistry.sol"
BUILD_PATH = ROOT / "contracts" / "build" / "AttributionRegistry.json"


def load_env() -> dict[str, str]:
    env = {}
    env_path = ROOT / ".env"
    if not env_path.exists():
        return env
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


# ─────────────────────────────────────────────────────────────
# DEPLOY
# ─────────────────────────────────────────────────────────────

def main() -> int:
    env = load_env()
    rpc_url = env.get("SEPOLIA_RPC_URL", "https://rpc.sepolia.org")
    private_key = env.get("SEPOLIA_PRIVATE_KEY", "").strip()

    if not private_key:
        print("❌ SEPOLIA_PRIVATE_KEY no configurada en .env")
        print("   Añade tu clave privada de MetaMask (con 0x delante).")
        print("   ⚠️  NUNCA la compartas. Solo vive en tu .env local.")
        return 1

    # Asegurar 0x al inicio
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key

    # Conectar
    print(f"🔌 Conectando a {rpc_url}...")
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    if not w3.is_connected():
        print("❌ No se pudo conectar a Sepolia.")
        return 1

    account = Account.from_key(private_key)
    balance = w3.eth.get_balance(account.address)
    balance_eth = w3.from_wei(balance, "ether")

    print(f"✅ Conectado.")
    print(f"   Cuenta:  {account.address}")
    print(f"   Balance: {balance_eth} ETH")

    if balance_eth == 0:
        print("❌ Balance 0 ETH. Consigue ETH de Sepolia en:")
        print("   https://sepolia-faucet.pk910.de")
        return 1

    # Verificar que existe el ABI compilado
    if not BUILD_PATH.exists():
        print(f"❌ No existe {BUILD_PATH}")
        print("   Compila primero con:  pnpm hardhat compile")
        print("   O usa Remix IDE: https://remix.ethereum.org")
        print()
        print("📋 Alternativa manual con Remix:")
        print("   1. Abre https://remix.ethereum.org")
        print("   2. Pega el contenido de contracts/AttributionRegistry.sol")
        print("   3. Compila con Solidity ^0.8.24")
        print("   4. En Deploy: Environment = Injected Provider (MetaMask)")
        print("   5. Click Deploy → copia la dirección")
        print("   6. Pégala en .env como ANCHOR_CONTRACT_ADDRESS")
        return 1

    # Cargar ABI + bytecode
    with BUILD_PATH.open() as f:
        build = json.load(f)

    abi = build["abi"]
    bytecode = build["bytecode"]

    # Crear contrato
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Construir transacción
    print("📝 Construyendo transacción de deploy...")
    nonce = w3.eth.get_transaction_count(account.address)
    gas_price = w3.eth.gas_price

    tx = Contract.constructor().build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gasPrice": gas_price,
        "chainId": 11155111,
    })

    # Firmar
    signed = account.sign_transaction(tx)

    # Enviar
    print("📤 Enviando transacción...")
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"   TX: {tx_hash.hex()}")

    # Esperar confirmación
    print("⏳ Esperando confirmación...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)

    contract_address = receipt["contractAddress"]
    print(f"✅ Contrato desplegado en: {contract_address}")
    print(f"   Block: {receipt['blockNumber']}")
    print(f"   Gas usado: {receipt['gasUsed']}")
    print()
    print("📌 Añade esto a tu .env:")
    print(f"   ANCHOR_CONTRACT_ADDRESS={contract_address}")
    print()
    print(f"🔍 Ver en Etherscan:")
    print(f"   https://sepolia.etherscan.io/address/{contract_address}")

    return 0


if __name__ == "__main__":
    sys.exit(main())