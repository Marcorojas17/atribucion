"""
Tests de Merkle trees.

Verifica:
- Cálculo de root
- Generación de proofs
- Verificación de proofs
- Detección de manipulaciones
"""

import pytest

from atribucion import merkle


# ─────────────────────────────────────────────────────────────
# ROOT
# ─────────────────────────────────────────────────────────────

def test_root_lista_vacia() -> None:
    root = merkle.root_of([])
    assert root.startswith("0x")
    assert len(root) == 66  # 0x + 64 hex


def test_root_un_item() -> None:
    root = merkle.root_of([{"a": 1}])
    assert root.startswith("0x")


def test_root_cuatro_items() -> None:
    items = [{"id": i} for i in range(4)]
    root = merkle.root_of(items)
    assert root.startswith("0x")


def test_root_deterministico() -> None:
    items = [{"id": 1}, {"id": 2}]
    assert merkle.root_of(items) == merkle.root_of(items)


def test_root_cambia_con_items() -> None:
    r1 = merkle.root_of([{"a": 1}])
    r2 = merkle.root_of([{"a": 2}])
    assert r1 != r2


def test_root_10k_items_rapido() -> None:
    import time

    items = [{"id": i} for i in range(10_000)]
    start = time.time()
    merkle.root_of(items)
    elapsed = time.time() - start
    assert elapsed < 2.0  # menos de 2 segundos


# ─────────────────────────────────────────────────────────────
# PROOF
# ─────────────────────────────────────────────────────────────

def test_proof_valida_indice_0() -> None:
    items = [{"id": i} for i in range(4)]
    p = merkle.proof_for(items, 0)
    assert merkle.verify_proof(p) is True


def test_proof_valida_todos() -> None:
    items = [{"id": i} for i in range(4)]
    for i in range(4):
        p = merkle.proof_for(items, i)
        assert merkle.verify_proof(p) is True


def test_proof_indice_fuera_de_rango() -> None:
    items = [{"id": 1}]
    with pytest.raises(IndexError):
        merkle.proof_for(items, 5)


def test_proof_lista_vacia() -> None:
    with pytest.raises(ValueError):
        merkle.proof_for([], 0)


def test_proof_manipulada_falla() -> None:
    items = [{"id": i} for i in range(4)]
    p = merkle.proof_for(items, 0)
    p.siblings[0] = "0x" + "00" * 32
    assert merkle.verify_proof(p) is False