# KAF-009 — Continuidad

**Dominio 9 de 13.**

## Objetivo

Garantizar continuidad del servicio.

## Controles

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-8.1 | Backups diarios (≥30 días) | High | ✅ |
| KAF-8.2 | Disaster recovery plan probado | High | ❌ |
| KAF-8.3 | SLA ≥99.5% sostenido | Medium | ✅ |

## Requisitos

### Backups

- Frecuencia: diaria
- Retención: ≥30 días
- Ubicación: separada del datacenter principal
- Cifrado: AES-256-GCM
- Prueba de restauración: mensual

### DR Plan

- RTO (Recovery Time Objective): ≤4 horas
- RPO (Recovery Point Objective): ≤1 hora
- Prueba: trimestral
- Documentación actualizada

### SLA

- Free: sin SLA
- Pro: 99.5% mensual
- Bank: 99.99% mensual
- Compensación: proporcional al downtime

## Evidencia

- Log de backups
- Reportes de pruebas de restauración
- Reporte mensual de uptime
- Documento DR actualizado