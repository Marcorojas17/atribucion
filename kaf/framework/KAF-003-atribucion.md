# KAF-003 — Atribución

**Dominio 3 de 13.**

## Objetivo

Garantizar que existe un Contrato de Atribución firmado y que
las responsabilidades están claramente definidas.

## Controles

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-2.1 | Contrato firmado (agente + creador + operador) | Critical | ✅ |
| KAF-2.2 | Colateral depositado en escrow | Critical | ✅ |
| KAF-2.3 | Nivel de autonomía declarado | High | ✅ |
| KAF-2.4 | Límite de daño configurado | High | ✅ |

## Contrato de Atribución

Debe incluir:

- DID del agente
- DID del creador
- DID del operador
- Nivel de autonomía (supervisado / semi-autonomo / autonomo)
- Límite de daño en KRN
- Colateral en escrow
- Causas excluyentes y agravantes

## Niveles de autonomía y colateral

| Nivel | Colateral mínimo | Límite de daño |
|---|---|---|
| Supervisado | 0 KRN | 5.000 KRN |
| Semi-autónomo | 2.000 KRN | 10.000 KRN |
| Autónomo | 10.000 KRN | 50.000 KRN |

## Evidencia

- Contrato firmado (hash + firma)
- Transacción de depósito de colateral
- Log de validaciones