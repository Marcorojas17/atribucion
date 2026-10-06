# Auditorías Internas

**Última actualización:** 2026-10-06
**Frecuencia:** Trimestral
**Owner:** Marco Antonio Rojas Valdovinos

---

## Objetivo

Revisar internamente que los controles de seguridad definidos
en las políticas se están aplicando correctamente.

A diferencia de las auditorías externas, estas las ejecuta
el propio equipo (o Marco, en MVP).

---

## Alcance

| Área | Qué se audita | Frecuencia |
|---|---|---|
| **Acceso** | Usuarios activos, permisos, MFA | Trimestral |
| **Criptografía** | Algoritmos, rotación de claves, TLS | Trimestral |
| **Logs** | Integridad, retención, redacción | Trimestral |
| **Backups** | Frecuencia, restauración, cifrado | Mensual |
| **Incidentes** | Tiempo de respuesta, post-mortems | Trimestral |
| **Compliance** | GDPR, LFPDPPP, EU AI Act | Semestral |
| **Dependencias** | Vulnerabilidades, actualizaciones | Mensual |
| **Infraestructura** | Configuración, accesos, secretos | Trimestral |

---

## Checklist Trimestral

### 1. Acceso
- [ ] Listar todos los usuarios activos
- [ ] Verificar que cada uno tiene MFA activo
- [ ] Revisar permisos: ¿alguien tiene más de lo necesario?
- [ ] Verificar que no hay cuentas huérfanas
- [ ] Revisar últimos cambios de permisos en audit log

### 2. Criptografía
- [ ] Verificar que TLS 1.3 está forzado
- [ ] Revisar certificados vigentes (>30 días)
- [ ] Verificar rotación de claves al día
- [ ] Revisar algoritmos usados (no hay MD5, SHA-1)
- [ ] Verificar que firmas híbridas están activas

### 3. Logs
- [ ] Verificar integridad de logs (hash chain)
- [ ] Revisar que no hay gaps >1h
- [ ] Verificar que datos sensibles están redactados
- [ ] Confirmar retención según política (365d mínimo)

### 4. Backups
- [ ] Verificar último backup completado
- [ ] Probar restauración de un backup aleatorio
- [ ] Verificar cifrado de backups
- [ ] Confirmar ubicación geográfica separada

### 5. Incidentes
- [ ] Revisar incidentes del trimestre
- [ ] Verificar post-mortems completados
- [ ] Revisar acciones correctivas cerradas
- [ ] Actualizar runbook si aplica

### 6. Dependencias
- [ ] Correr `pip-audit` (Python)
- [ ] Correr `npm audit` (Node)
- [ ] Revisar CVEs recientes en dependencias
- [ ] Actualizar dependencias con vulnerabilidades

### 7. Infraestructura
- [ ] Revisar accesos a Railway / GitHub
- [ ] Verificar que no hay secretos en repos
- [ ] Revisar configuración de firewall
- [ ] Verificar backups de configuración

### 8. Compliance
- [ ] Verificar aviso de privacidad actualizado
- [ ] Revisar registros de tratamiento (GDPR)
- [ ] Verificar consentimientos recolectados
- [ ] Confirmar plazos de retención

---

## Cómo reportar

Cada auditoría genera un reporte en:

```text
security/audits/internal/YYYY-QX-report.md

# Auditoría Interna — YYYY QX

**Fecha:** YYYY-MM-DD
**Auditor:** Marco Antonio Rojas Valdovinos
**Duración:** X horas

## Resumen
- Controles revisados: X
- Controles OK: X
- Hallazgos: X
- Críticos: X

## Hallazgos

### Hallazgo 1
**Área:** Acceso
**Severidad:** Alta
**Descripción:** [detalle]
**Evidencia:** [links, screenshots]
**Recomendación:** [acción]

## Acciones correctivas
- [ ] Acción 1 — owner — fecha límite
- [ ] Acción 2 — owner — fecha límite

## Próxima auditoría
Fecha: YYYY-MM-DD

Script Qué hace
check_tls.sh Verifica TLS 1.3 en todos los endpoints
check_certs.sh Verifica vigencia de certificados
check_keys.sh Verifica antigüedad de claves
check_logs.py Verifica integridad de logs
check_deps.sh Corre pip-audit + npm audit
check_secrets.sh Busca secretos en el repo

Fase Mes Acción
MVP 1-3 Auditorías manuales mensuales
Beta 4-6 Scripts de automatización
Producción 7-12 Auditorías automáticas semanales
Enterprise 13+ SOC 2 + ISO 27001 internos

