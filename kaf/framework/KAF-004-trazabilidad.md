# KAF-004 — Trazabilidad

**Dominio 4 de 13.**

## Objetivo

Garantizar que cada acción de un agente es registrable,
verificable y auditable (EU AI Act Art. 12).

## Controles

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-3.1 | Log inmutable (append-only) | Critical | ✅ |
| KAF-3.2 | Firma por cada acción | Critical | ✅ |
| KAF-3.3 | Anclaje Ethereum ≤6h | Critical | ✅ |
| KAF-3.4 | Hash doble (SHA-256 + SHA-3) | High | ✅ |
| KAF-3.5 | IPFS archival | Medium | ✅ |

## Flujo de trazabilidad

1. Acción del agente
2. Firma ECDSA + ML-DSA
3. Hash doble SHA-256 + SHA-3
4. Inclusión en Merkle tree
5. Anclaje Ethereum
6. Archivo IPFS + Arweave
7. Índice en Proofs Registry

## Retención

- Logs: mínimo 10 años
- Anclajes: permanente (blockchain)
- Archivo IPFS: permanente (Arweave)

## Verificación pública

Cualquier ciudadano puede verificar sin permiso:

```bash
curl https://api.atribucion.io/v1/proofs/{cert_id}