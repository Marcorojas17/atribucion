# KAF-002 — Identidad

**Dominio 2 de 13.**

## Objetivo

Garantizar que cada agente tiene una identidad criptográfica
verificable, ligada a un creador humano u organización.

## Controles

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-1.1 | DID registrado | Critical | ✅ |
| KAF-1.2 | VC vigente | Critical | ✅ |
| KAF-1.3 | Claves rotadas ≤90 días | High | ✅ |
| KAF-1.4 | DID Document público | Medium | ✅ |

## Requisitos técnicos

### DID

Formato: `did:kronos:<tipo>:0x<40_hex>`

Tipos soportados: `agent`, `human`, `robot`, `org`.

### VC (Verifiable Credential)

Compatible con W3C VC Data Model 2.0.

### Rotación de claves

Automática cada ≤90 días. Notificación previa 7 días.

## Evidencia

- DID Document en `/.well-known/did.json`
- Certificado VC firmado
- Log de rotaciones