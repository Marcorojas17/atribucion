"""
Tests de sellado de tiempo RFC 3161.

Verifica:
- Sellado en modo mock
- Determinismo
- Verificación
- Detección de payload alterado
"""

import asyncio

from atribucion import tsa


# ─────────────────────────────────────────────────────────────
# SELLADO
# ─────────────────────────────────────────────────────────────

def test_seal_modo_mock() -> None:
    async def _run() -> None:
        result = await tsa.seal(b"test payload")
        assert result.mode == "mock"
        assert result.authority == "mock-tsa"
        assert result.token.startswith("0x")
        assert len(result.token) == 66  # 0x + 64 hex

    asyncio.run(_run())


def test_seal_sha256_por_defecto() -> None:
    async def _run() -> None:
        result = await tsa.seal(b"test")
        assert result.hash_algorithm == "sha256"

    asyncio.run(_run())


def test_seal_algoritmo_personalizado() -> None:
    async def _run() -> None:
        result = await tsa.seal(b"test", hash_algorithm="sha3_256")
        assert result.hash_algorithm == "sha3_256"

    asyncio.run(_run())


# ─────────────────────────────────────────────────────────────
# VERIFICACIÓN
# ─────────────────────────────────────────────────────────────

def test_verify_seal_ok() -> None:
    async def _run() -> None:
        payload = b"test payload"
        result = await tsa.seal(payload)
        assert tsa.verify_seal(payload, result) is True

    asyncio.run(_run())


def test_verify_seal_payload_alterado() -> None:
    async def _run() -> None:
        payload = b"test payload"
        result = await tsa.seal(payload)
        assert tsa.verify_seal(b"otro payload", result) is False

    asyncio.run(_run())


def test_verify_seal_token_alterado() -> None:
    async def _run() -> None:
        payload = b"test"
        result = await tsa.seal(payload)
        result.token = "0x" + "0" * 64
        assert tsa.verify_seal(payload, result) is False

    asyncio.run(_run())