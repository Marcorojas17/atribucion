# Incident Response Policy

**Última actualización:** 2026-10-06
**Versión:** 1.0.0
**Owner:** Marco Antonio Rojas Valdovinos

---

## 1. Principio rector

**Detectar rápido, contener rápido, aprender rápido.**
Ningún incidente se oculta. Todos se documentan.

## 2. Clasificación de severidad

| Nivel | Descripción | Respuesta |
|---|---|---|
| **SEV-1 (Crítico)** | Brecha de claves, caída total, pérdida de datos | Inmediata (15 min) |
| **SEV-2 (Alto)** | Exposición de datos limitada, degradación severa | <1 hora |
| **SEV-3 (Medio)** | Bug de seguridad no explotado, degradación menor | <4 horas |
| **SEV-4 (Bajo)** | Hallazgo de pentesting, mejora de seguridad | <48 horas |

## 3. Equipo de respuesta

### 3.1 Roles
| Rol | Quién | Responsabilidad |
|---|---|---|
| **Incident Commander** | Marco | Coordinar respuesta |
| **Communications** | Marco | Notificar afectados |
| **Technical Lead** | Marco | Diagnóstico técnico |
| **Legal** | Externo (roadmap) | Cumplimiento legal |

### 3.2 Contactos
- **Marco:** marco@atribucion.io / +52 xxx
- **Security:** security@atribucion.io
- **Legal:** legal@atribucion.io (roadmap)

## 4. Flujo de respuesta

### 4.1 Detección
Fuentes:
- Guards (SENTINEL, VAULT, ACTA).
- Alertas de servicios externos.
- Reportes de usuarios.
- Bug bounty.

### 4.2 Clasificación
1. Identificar tipo de incidente.
2. Asignar severidad (SEV-1 a SEV-4).
3. Activar equipo correspondiente.
4. Abrir ticket de incidente.

### 4.3 Contención
**Objetivo:** detener la propagación.

Acciones inmediatas:
- Bloquear IPs sospechosas.
- Revocar tokens comprometidos.
- Aislar servicios afectados.
- Preservar evidencia (logs, snapshots).

### 4.4 Erradicación
- Identificar causa raíz.
- Eliminar vulnerabilidad.
- Actualizar sistemas.
- Rotar claves afectadas.

### 4.5 Recuperación
- Restaurar servicios.
- Verificar integridad.
- Monitorear durante 7 días.
- Confirmar con stakeholders.

### 4.6 Lecciones aprendidas
- Post-mortem obligatorio (48h).
- Documentar timeline.
- Identificar mejoras.
- Actualizar políticas.

## 5. Notificaciones

### 5.1 Internas
| Nivel | Canal | Tiempo |
|---|---|---|
| SEV-1 | PagerDuty + llamada | Inmediato |
| SEV-2 | Slack + email | <1h |
| SEV-3 | Slack | <4h |
| SEV-4 | Email | <48h |

### 5.2 Externas
| Afectado | Plazo | Método |
|---|---|---|
| Usuarios afectados | <72h | Email |
| Autoridades UE (GDPR) | <72h | Formulario oficial |
| Autoridades MX (LFPDPPP) | <72h | Oficio |
| Clientes enterprise | <24h | Llamada + email |
| Público | Variable | Post de blog |

## 6. Preservación de evidencia

### 6.1 Qué preservar
- Logs (todos los servicios).
- Snapshots de disco.
- Tráfico de red (si aplica).
- Configuración en el momento.
- Emails/Slack relacionados.

### 6.2 Cadena de custodia
- Cada evidencia se hashea (SHA-256).
- Se almacena en copia inmutable.
- Se documenta quién accedió y cuándo.

## 7. Comunicación pública

### 7.1 Qué comunicar
- Qué pasó (sin detalles técnicos sensibles).
- A quién afecta.
- Qué estamos haciendo.
- Qué deben hacer los usuarios.
- Próximos pasos y fechas.

### 7.2 Qué NO comunicar
- Detalles técnicos explotables.
- Nombres de empleados.
- Especulación sobre causa.
- Promesas sin sustento.

### 7.3 Canal
- Blog oficial: `atribucion.io/security/incidents`
- Estado: `status.atribucion.io` (roadmap)
- Twitter/X: `@atribucion`

## 8. Post-mortem

### 8.1 Cuándo
- SEV-1: obligatorio en 48h.
- SEV-2: obligatorio en 7 días.
- SEV-3: opcional.
- SEV-4: no requiere.

### 8.2 Formato
```markdown
## Incidente: [título]
**Fecha:** YYYY-MM-DD
**Severidad:** SEV-X
**Duración:** X horas
**Impacto:** [descripción]

### Timeline
- 10:00 — Detección
- 10:15 — Contención
- 11:30 — Erradicación
- 12:00 — Recuperación

### Causa raíz
[descripción]

### Lecciones aprendidas
1. ...
2. ...

### Acciones correctivas
- [ ] Acción 1 — owner — fecha
- [ ] Acción 2 — owner — fecha

### Publicación
- [x] Blog post publicado
- [x] Notificado a afectados
- [x] Notificado a autoridades