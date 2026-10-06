# KAF-007 — Seguridad

**Dominio 7 de 13.**

## Objetivo

Garantizar seguridad de nivel enterprise.

## Controles

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-6.1 | ISO 27001 vigente | Critical | ❌ |
| KAF-6.2 | SOC 2 Type II | High | ❌ |
| KAF-6.3 | Pentesting anual | High | ❌ |
| KAF-6.4 | HSM para claves privadas | Critical | ❌ |
| KAF-6.5 | Zero Trust | High | ✅ |

## Requisitos

### ISO 27001

Certificación vigente (no autoevaluación).
Auditoría externa en últimos 12 meses.

### SOC 2 Type II

Auditoría de controles operativos sobre ventana de 6-12 meses.

### Pentesting

Auditoría de penetración anual por firma reconocida.

### HSM

Claves privadas nunca salen del Hardware Security Module.
Soporta: AWS CloudHSM, Azure Dedicated HSM, YubiHSM, Thales Luna.

### Zero Trust

Cada request verificada independientemente.
Ningún servicio confía en otro sin autenticación.

## Evidencia

- Certificados vigentes (PDF)
- Reporte de pentesting
- Configuración de HSM
- Diagrama de arquitectura Zero Trust