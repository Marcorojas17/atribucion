"""
Atribución — Core criptográfico y de identidad.

Protocolo de certificación de agentes IA para compliance
con EU AI Act (Art. 12, 14, 22).

Módulos:
    crypto    → Firmas híbridas ECDSA + ML-DSA
    did       → Identidad descentralizada (W3C DID)
    contract  → Contrato de Atribución
    vc        → Credenciales verificables (W3C VC 2.0)
    merkle    → Árboles Merkle para anclaje eficiente
    anchor    → Anclaje a Ethereum (mock / real)
    tsa       → Sellado de tiempo RFC 3161
"""

__version__ = "0.1.0"
__author__ = "Marco Antonio Rojas Valdivín"
__license__ = "MIT OR Apache-2.0"

__all__ = [
    "anchor",
    "contract",
    "crypto",
    "did",
    "merkle",
    "tsa",
    "vc",
]