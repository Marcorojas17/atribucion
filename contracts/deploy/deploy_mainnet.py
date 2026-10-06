"""
Atribución — Deploy a Ethereum Mainnet.

ADVERTENCIA: Esto cuesta ETH real. Verifica TODO antes.

Uso:
    python contracts/deploy/deploy_mainnet.py --confirm
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from eth_account import Account
from web3 import Web3


ROOT = Path(__file__).resolve().parents[2]
BUILD_DIR = ROOT / "contracts" / "build"
CONTRACTS = ["AttributionRegistry", "KAFRegistry", "PaymentSplitter"]


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
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


def check_requirements() -> tuple[Web3, Account, str]:
    """Verifica prerequisitos para deploy a Mainnet."""
    env = load_env()

    rpc_url = env.get("MAINNET_RPC_URL", "").strip()
    private_key = env.get("MAINNET_PRIVATE_KEY", "").strip()

    if not rpc_url:
        print("❌ MAINNET_RPC_URL no configurada en .env")
        sys.exit(1)
    if not private_key:
        print("❌ MAINNET_PRIVATE_KEY no configurada en .env")
        sys.exit(1)
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key

    print(f"🔌 Conectando a {rpc_url[:40]}...")
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    if not w3.is_connected():
        print("❌ No se pudo conectar a Mainnet")
        sys.exit(1)

    account = Account.from_key(private_key)
    balance_wei = w3.eth.get_balance(account.address)
    balance_eth = w3.from_wei(balance_wei, "ether")

    print(f"✅ Conectado a Mainnet")
    print(f"   Cuenta:  {account.address}")
    print(f"   Balance: {balance_eth} ETH")

    if balance_eth < 0.05:
        print(f"❌ Balance insuficiente. Necesitas ≥0.05 ETH.")
        print(f"   Tienes: {balance_eth} ETH")
        sys.exit(1)

    return w3, account, private_key


def deploy_contract(
    w3: Web3,
    account: Account,
    private_key: str,
    contract_name: str,
) -> str:
    """Despliega un contrato a Mainnet."""
    build_path = BUILD_DIR / f"{contract_name}.json"
    if not build_path.exists():
        print(f"⚠️  {contract_name}: no existe {build_path}, saltando")
        return ""

    with build_path.open() as f:
        build = json.load(f)

    abi = build["abi"]
    bytecode = build["bytecode"]

    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(account.address)
    gas_price = w3.eth.gas_price

    print(f"\n📝 Desplegando {contract_name}...")
    print(f"   Gas price: {w3.from_wei(gas_price, 'gwei')} gwei")

    tx = Contract.constructor().build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gasPrice": gas_price,
        "chainId": 1,
    })

    # Estimación de gas
    estimated_gas = w3.eth.estimate_gas(tx)
    tx["gas"] = int(estimated_gas * 1.2)
    print(f"   Gas estimado: {estimated_gas}")

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"   TX: {tx_hash.hex()}")

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
    address = receipt["contractAddress"]

    print(f"✅ {contract_name} en: {address}")
    print(f"   Block: {receipt['blockNumber']}")
    print(f"   Gas usado: {receipt['gasUsed']}")
    print(f"   Etherscan: https://etherscan.io/address/{address}")

    return address


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", action="store_true",
                       help="Confirmar deploy a Mainnet (obligatorio)")
    parser.add_argument("--contract", default=None,
                       help="Desplegar solo un contrato específico")
    args = parser.parse_args()

    if not args.confirm:
        print("⚠️  DEPLOY A MAINNET REQUIERE CONFIRMACIÓN")
        print()
        print("   Este comando gastará ETH REAL.")
        print("   Verifica que:")
        print("   1. Los contratos están auditados")
        print("   2. Tienes ≥0.05 ETH en la cuenta")
        print("   3. El RPC está configurado")
        print()
        print("   Para continuar: añade --confirm")
        return 1

    w3, account, private_key = check_requirements()

    contracts_to_deploy = [args.contract] if args.contract else CONTRACTS
    deployed: dict[str, str] = {}

    for contract_name in contracts_to_deploy:
        try:
            address = deploy_contract(w3, account, private_key, contract_name)
            if address:
                deployed[contract_name] = address
            time.sleep(3)  # esperar entre deploys
        except Exception as e:
            print(f"❌ Error desplegando {contract_name}: {e}")
            continue

    print("\n" + "=" * 60)
    print("📋 CONTRATOS DESPLEGADOS")
    print("=" * 60)
    for name, addr in deployed.items():
        print(f"   {name}: {addr}")

    print("\n📌 Añade esto a tu .env:")
    for name, addr in deployed.items():
        env_key = f"{name.upper()}_ADDRESS"
        print(f"   {env_key}={addr}")

    return 0


if __name__ == "__main__":
    sys.exit(main())