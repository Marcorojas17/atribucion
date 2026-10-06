# KAF-010 — Criptografía

**Dominio 10 de 13.**

## Objetivo

Garantizar criptografía resistente a computación cuántica.

## Controles

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-9.1 | Firmas híbridas (ECDSA + ML-DSA) | Critical | ✅ |
| KAF-9.2 | PQC completo (ML-KEM + ML-DSA + SLH-DSA) | Critical | ✅ |
| KAF-9.3 | Rotación de claves ≤90 días | High | ✅ |
| KAF-9.4 | TLS 1.3 obligatorio | High | ✅ |

## Algoritmos obligatorios

### Firmas

- Clásico: ECDSA secp256k1
- Post-cuántico: ML-DSA-65 (Dilithium3)
- Híbrido: ambos

### Cifrado

- Clásico: X25519
- Post-cuántico: ML-KEM-768 (Kyber768)
- Híbrido: ambos

### Hash

- SHA-256 + SHA-3-256
- SLH-DSA (SPHINCS+) para firma de respaldo

### Transporte

- TLS 1.3 obligatorio
- TLS 1.2 solo con justificación documentada
- HSTS con `includeSubDomains; preload`

## Estándares

- NIST FIPS 203 (ML-KEM)
- NIST FIPS 204 (ML-DSA)
- NIST FIPS 205 (SLH-DSA)
- RFC 8446 (TLS 1.3)

## Evidencia

- Configuración criptográfica
- Inventario de claves
- Log de rotaciones
- Test de conectividad TLS