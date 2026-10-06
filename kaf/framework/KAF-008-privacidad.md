# KAF-008 — Privacidad

**Dominio 8 de 13.**

## Objetivo

Garantizar privacidad de datos personales.

## Controles

| ID | Nombre | Severidad | Auto |
|---|---|---|---|
| KAF-7.1 | GDPR compliance | Critical | ❌ |
| KAF-7.2 | LFPDPPP compliance | High | ❌ |
| KAF-7.3 | Datos personales NUNCA en cadena | Critical | ✅ |
| KAF-7.4 | Cifrado en reposo (AES-256-GCM) | High | ✅ |

## Requisitos

### GDPR (UE)

- Base legal documentada
- Derechos ARCO implementados
- DPO designado
- Registro de actividades de tratamiento

### LFPDPPP (México)

- Aviso de privacidad
- Derechos ARCO
- Medidas de seguridad

### Datos personales fuera de cadena

Regla de oro: lo que va a blockchain es solo el hash.
Los datos personales reales nunca salen del cifrado.

### Cifrado en reposo

- AES-256-GCM
- Claves en HSM
- Rotación cada 90 días

## Evidencia

- Aviso de privacidad publicado
- Registro de tratamientos
- Configuración de cifrado
- Logs de acceso a datos personales