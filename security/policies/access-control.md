# Access Control Policy

**Última actualización:** 2026-10-06
**Versión:** 1.0.0
**Owner:** Marco Antonio Rojas Valdovinos

---

## 1. Principio rector

**Zero Trust:** cada request se verifica independientemente.
Ningún servicio, usuario o agente confía en otro sin autenticación.

## 2. Clasificación de acceso

| Nivel | Quién | Qué puede hacer |
|---|---|---|
| Público | Cualquiera | Verificar certificados, ver docs |
| Autenticado | Con API key | Registrar agentes, emitir acciones |
| Admin | Marco + admins | Gestionar tenants, ver todo |
| Root | Solo Marco | Deploy, cambios infra |

## 3. Autenticación

### 3.1 Humanos
- **MFA obligatorio** para acceder al dashboard y admin.
- **Contraseñas:** mínimo 16 caracteres, 1Password/Bitwarden.
- **OAuth 2.0 + OIDC** para login web.
- **Sesiones:** expiran en 24h de inactividad.

### 3.2 API keys
- Formato: `ak_live_<64_hex>` (producción).
- Formato: `ak_test_<64_hex>` (sandbox).
- Almacenamiento: **solo hash SHA-256** en DB.
- Rotación: cada 90 días (manual en MVP, auto en v2).
- Revocación: inmediata vía dashboard.

### 3.3 Agentes IA
- **DID + firma híbrida** (ECDSA + ML-DSA).
- Contrato de Atribución firmado por 3 partes.
- Colateral depositado según nivel de autonomía.

### 3.4 Servicio a servicio
- **mTLS** obligatorio entre servicios internos.
- **Service accounts** con tokens de corta duración.
- **Vault** para secretos (roadmap mes 6).

## 4. Autorización

### 4.1 RBAC (Role-Based Access Control)

| Rol | Permisos |
|---|---|
| Viewer | Ver certificados, ver reportes |
| Developer | + registrar agentes, + emitir acciones |
| Admin | + gestionar tenants, + ver todo |
| Root | + deploy, + cambios infra |

### 4.2 Principio de mínimo privilegio
Cada rol tiene **solo** los permisos necesarios para su función.

### 4.3 Separación de funciones
Quien despliega **no** puede aprobar su propio deploy.
Quien audita **no** puede modificar logs.

## 5. Ciclo de vida del acceso

### 5.1 Alta
1. Solicitud documentada.
2. Aprobación por admin.
3. Creación de cuenta con MFA.
4. Capacitación de seguridad.
5. Firma de NDA + aceptación de políticas.

### 5.2 Cambios
- Cambios de rol requieren aprobación.
- Toda modificación se registra en audit log.
- Revisión trimestral de roles.

### 5.3 Baja
- Al terminar relación laboral: revocación **inmediata**.
- Backup de datos del usuario (si aplica).
- Rotación de secretos compartidos.
- Eliminación de credenciales en 24h.

## 6. Registro y monitoreo

### 6.1 Qué se registra
- Cada login (éxito y fallo).
- Cada cambio de permisos.
- Cada acceso a datos sensibles.
- Cada uso de API key.
- Cada intento fallido de autorización.

### 6.2 Retención
- Logs de acceso: **365 días**.
- Logs de admin: **5 años**.
- Incidentes: **5 años**.

### 6.3 Alertas automáticas
- Login desde IP nueva.
- Fallos repetidos de autenticación.
- Acceso fuera de horario.
- Cambios críticos de permisos.

## 7. Auditoría

- **Trimestral:** revisión de accesos activos.
- **Anual:** auditoría externa de controles.
- **Post-incidente:** revisión obligatoria.

## 8. Excepciones

Cualquier excepción a esta política debe:
1. Documentarse por escrito.
2. Tener aprobación de Marco.
3. Tener fecha de expiración (máximo 90 días).
4. Registrarse en audit log.

## 9. Enforcement

| Violación | Consecuencia |
|---|---|
| Compartir API key | Revocación inmediata + investigación |
| Acceso fuera de scope | Suspensión temporal |
| Ocultar incidente | Terminación de contrato |
| Reincidencia | Terminación + acción legal |

## 10. Referencias

- NIST SP 800-53 (AC family)
- ISO 27001 A.9
- OWASP ASVS V2 (Authentication)
- OWASP ASVS V4 (Access Control)