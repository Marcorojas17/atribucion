# Key Rotation Policy

**Última actualización:** 2026-10-06
**Versión:** 1.0.0
**Owner:** Marco Antonio Rojas Valdovinos

---

## 1. Principio rector

**Toda clave se rota periódicamente.** Ninguna clave es
perpetua. La rotación reduce el impacto de una posible
compromiso.

## 2. Frecuencia de rotación

| Tipo de clave | Frecuencia | Justificación |
|---|---|---|
| API keys (producción) | 90 días | Estándar industria |
| API keys (test) | 180 días | Menor riesgo |
| Claves de firma ECDSA | 90 días | NIST 800-57 |
| Claves ML-DSA (PQC) | 365 días | Menor presión PQC |
| TLS certificates | 90 días | Let's Encrypt |
| mTLS certificates | 90 días | Zero Trust |
| Claves simétricas AES | 90 días | NIST 800-57 |
| Claves de backup | 365 días | Mayor retención |
| JWT secrets | 30 días | Alta exposición |
| Webhook secrets | 180 días | Por proveedor |
| HSM master keys | 365 días | Rotación compleja |
| Root CA | 5-10 años | Inmutabilidad requerida |

## 3. Proceso de rotación

### 3.1 Fase 1 — Preparación (D-7)
- Notificar a afectados.
- Generar nuevas claves.
- Almacenar de forma segura.
- Preparar plan de rollback.

### 3.2 Fase 2 — Publicación (D-3)
- Publicar nuevas claves públicas.
- Actualizar DID Documents.
- Añadir nueva clave a keyring.
- **Mantener** clave vieja activa.

### 3.3 Fase 3 — Transición (D-0 a D+30)
- Nuevas firmas usan clave nueva.
- Verificación acepta ambas claves.
- Logs indican qué clave se usó.
- Detección de uso de clave vieja.

### 3.4 Fase 4 — Retiro (D+30)
- Retirar clave vieja del keyring.
- Marcar como "revoked" en DID Document.
- Publicar aviso.
- Archivar clave vieja (sin uso).

### 3.5 Fase 5 — Destrucción (D+90)
- Sobrescritura segura de la clave vieja.
- Registro de destrucción.
- Audit log actualizado.

## 4. Rotación automática

### 4.1 Alcance
- ✅ API keys
- ✅ TLS certificates
- ✅ JWT secrets
- ✅ Webhook secrets
- 🟡 Claves de firma (semi-auto, requiere confirmación)
- 🔴 HSM master keys (manual)

### 4.2 Implementación
```python
# Cron job diario
if key.age_days >= key.rotation_days - 7:
    notify_owner(key)
if key.age_days >= key.rotation_days:
    if key.auto_rotate:
        rotate_key(key)
    else:
        block_usage(key)

```

4.3 Roadmap

· Mes 3: rotación automática de API keys.
· Mes 6: rotación automática de TLS + JWT.
· Mes 9: rotación semi-auto de claves de firma.
· Mes 12: HSM real con rotación controlada.

5. Rotación de emergencia

Se activa cuando:

· Sospecha de compromiso.
· Detección de uso anómalo.
· Empleado con acceso termina relación.
· Auditoría detecta exposición.

Proceso:

1. Rotación inmediata (no esperar ciclo normal).
2. Notificación urgente a afectados.
3. Revocación de clave comprometida.
4. Investigación de causa.
5. Post-mortem.

Plazo: máximo 4 horas desde detección.

6. Backup de claves

6.1 Antes de rotar

· Backup cifrado de la clave vieja.
· Almacenar en ubicación separada.
· Registro en audit log.

6.2 Retención

· Claves de firma: 7 años (legal).
· Claves simétricas: 2 años.
· API keys: 90 días post-revocación.
· TLS: 1 año post-expiración.

6.3 Acceso a backups

· Solo Marco (o admin designado).
· Doble autenticación obligatoria.
· Auditoría de cada acceso.

7. Verificación

7.1 Checklist semanal

☐ ¿Alguna clave cerca de expirar?
☐ ¿Rotaciones automáticas funcionaron?
☐ ¿Alguna clave revocada sigue en uso?

7.2 Métricas

· % de claves rotadas a tiempo: objetivo 100%.
· Días promedio de retraso: objetivo < 1 día.
· Rotaciones de emergencia: objetivo 0 por trimestre.

8. Comunicación de rotación

8.1 Interna

· Aviso con 7 días de anticipación.
· Recordatorio con 1 día.
· Confirmación post-rotación.

8.2 Clientes

· Clientes API: aviso 30 días antes (con período de gracia).
· Aviso de cambios en headers/firmas.
· Guía de migración si aplica.

8.3 Pública

· Aviso en blog si afecta a terceros.
· Changelog con fecha exacta.

9. Excepciones

Cualquier excepción (saltarse rotación) debe:

1. Documentarse.
2. Aprobarse por Marco.
3. Tener fecha de expiración (máximo 30 días).
4. Incluir plan de mitigación.

10. Herramientas

Herramienta Uso Estado
HashiCorp Vault Gestión + rotación Roadmap mes 6
AWS KMS Alternativa cloud Roadmap mes 12
YubiHSM HSM físico Roadmap mes 6
Let's Encrypt TLS auto-rotación ✅ Activo
GitHub Actions Cron de rotación ✅ Activo

11. Referencias

· NIST SP 800-57 (Key Management)
· NIST SP 800-133 (Key Generation)
· ISO 27001 A.10.1.2
· PCI DSS 3.5-3.7 (Key management, si aplica)
· Mercado Pago: webhook secret rotation

```