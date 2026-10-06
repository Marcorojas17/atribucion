# SOC 2 Type II — Compliance

## Estado

🔴 **Pendiente de certificación.**

Roadmap:
- SOC 2 Type I: mes 4-6
- SOC 2 Type II: mes 10-12

## Qué certifica

Auditoría independiente de controles de servicio.
A diferencia de ISO 27001, SOC 2 es específico para
proveedores de servicios (SaaS, cloud).

## Los 5 Trust Services Criteria

### 1. Security (obligatorio)
- Protección contra accesos no autorizados
- Firewalls, MFA, cifrado
- Monitoreo continuo

### 2. Availability (opcional)
- Disponibilidad del sistema según SLA
- Redundancia y failover
- Monitoreo de uptime

### 3. Processing Integrity (opcional)
- Procesamiento completo y preciso
- Validación de inputs/outputs
- Detección de errores

### 4. Confidentiality (opcional)
- Protección de información confidencial
- Cifrado en tránsito y reposo
- Control de acceso

### 5. Privacy (opcional)
- Cumplimiento GDPR/LFPDPPP
- Derechos ARCO
- Consentimiento

**Atribución aplica: 1, 2, 3, 4, 5.**

## Type I vs Type II

| | Type I | Type II |
|---|---|---|
| **Qué evalúa** | Diseño de controles | Diseño + operación efectiva |
| **Período** | Punto en el tiempo | 6-12 meses |
| **Costo** | $15.000 | $25.000 |
| **Vigencia** | 12 meses | 12 meses |
| **Requisito clientes** | Startups | Enterprise |

## Controles implementados

| Control | Estado | Implementación |
|---|---|---|
| Control de acceso | ✅ | API key + OAuth |
| Cifrado en tránsito | ✅ | TLS 1.3 |
| Cifrado en reposo | ✅ | AES-256-GCM |
| Logs inmutables | ✅ | Audit middleware |
| Monitoreo | ✅ | Guards + Prometheus |
| Gestión de cambios | ✅ | GitHub PRs + CI |
| Gestión de incidentes | 🟡 | `SECURITY.md` |
| Backups | ✅ | Diarios + retención 30d |
| Continuidad | ✅ | `guards/phoenix/` |
| Capacitación | 🔴 | Pendiente documentar |

## Roadmap

| Mes | Hito |
|---|---|
| 1-3 | Implementar controles faltantes |
| 4 | Iniciar SOC 2 Type I |
| 5-6 | Completar Type I |
| 7-12 | Período de observación (6 meses) |
| 12 | Certificación Type II |

## Plataformas de compliance

- **Vanta** — Automatización + monitoreo continuo
- **Drata** — Alternativa popular
- **Secureframe** — Más económico
- **Tugboat Logic** — Para startups

**Recomendación:** Vanta (~$8.000/año).

## Costo estimado

- **Plataforma:** $8.000/año
- **Auditoría Type I:** $15.000
- **Auditoría Type II:** $25.000
- **Total año 1:** $48.000
- **Mantenimiento año 2+:** $15.000

## Auditores acreditados

- Prescient Assurance
- Johanson Group
- Sensiba
- A-LIGN

## Referencias

- AICPA SOC 2 Trust Services Criteria
- AICPA Guide: Reporting on an Examination of Controls