```markdown
# Data Processing Agreement (DPA)

**Última actualización:** 2026-10-06

---

## 1. Partes

**Procesador:** Atribución, operado por Marco Antonio Rojas Valdovinos.
**Responsable:** El cliente que contrata los servicios de Atribución.

---

## 2. Objeto

Atribución procesa datos personales por cuenta del Responsable,
conforme al Reglamento General de Protección de Datos (GDPR)
y la Ley Federal de Protección de Datos Personales en Posesión
de los Particulares (LFPDPPP, México).

---

## 3. Datos procesados

| Categoría | Ejemplos | Finalidad |
|---|---|---|
| Identificativos | Email, nombre, país | Cuenta |
| De contacto | Email, teléfono | Comunicación |
| De facturación | RFC, dirección fiscal | Facturación |
| De uso | IP, user agent, endpoints | Seguridad |
| De agentes | DID, contratos, acciones | Servicio |

**NO se procesan:**
- Datos de salud
- Datos biométricos
- Datos de menores
- Datos de origen racial o étnico
- Opiniones políticas o religiosas

---

## 4. Obligaciones del Procesador

Atribución se compromete a:

1. Procesar datos **solo** según instrucciones del Responsable.
2. Mantener **confidencialidad** de los datos.
3. Implementar **medidas de seguridad** técnicas y organizativas.
4. **Notificar brechas** en menos de 72 horas.
5. **Asistir** al Responsable en el cumplimiento de derechos ARCO.
6. **Eliminar** los datos al terminar el contrato (con excepciones legales).
7. **No subcontratar** sin autorización previa.
8. **Permitir auditorías** del Responsable.

---

## 5. Subencargados

Atribución usa los siguientes subencargados:

| Subencargado | País | Servicio |
|---|---|---|
| Railway | USA | Hosting |
| Cloudflare | USA | CDN + DDoS |
| GitHub | USA | Repositorio |
| Ethereum Foundation | Global | Blockchain |
| Arweave | Global | Almacenamiento |
| Mercado Pago | México | Pagos |
| DigiCert | USA | TSA |

Todos cumplen GDPR o tienen SCCs firmadas.

---

## 6. Transferencias internacionales

Los datos pueden transferirse a:

- **USA:** Railway, Cloudflare, GitHub, DigiCert
- **México:** Atribución HQ, Mercado Pago
- **Global:** Ethereum, Arweave

**Base legal:** Standard Contractual Clauses (SCCs) aprobadas
por la Comisión Europea (Decisión 2021/914).

---

## 7. Medidas de seguridad

Atribución implementa:

- **Cifrado en tránsito:** TLS 1.3
- **Cifrado en reposo:** AES-256-GCM
- **Firmas híbridas:** ECDSA + ML-DSA
- **Control de acceso:** Zero Trust + RBAC + MFA
- **Auditoría:** logs inmutables (append-only)
- **Backups:** diarios cifrados
- **Continuidad:** DR plan probado
- **Bug bounty:** activo (mes 6)

---

## 8. Derechos ARCO

Atribución asiste al Responsable en:

- **Acceso:** recuperar copia de datos.
- **Rectificación:** corregir datos inexactos.
- **Cancelación:** eliminar datos (con limitaciones blockchain).
- **Oposición:** oponerse al tratamiento.

**Plazo de respuesta:** 20 días hábiles.

---

## 9. Notificación de brechas

En caso de brecha, Atribución notifica al Responsable:

- **Plazo:** 24 horas desde detección.
- **Contenido:**
  - Descripción de la brecha.
  - Datos afectados.
  - Número de titulares afectados.
  - Medidas tomadas.
  - Recomendaciones.

El Responsable notifica a las autoridades si aplica:
- **GDPR:** 72 horas.
- **LFPDPPP:** 72 horas.

---

## 10. Duración

Este DPA es efectivo desde la firma del contrato principal.

Termina cuando:
- El contrato principal termina.
- El Responsable solicita cancelación.

**Eliminación:** 30 días post-terminación (excepto retención legal).

---

## 11. Auditoría

El Responsable puede auditar a Atribución:

- **Frecuencia:** máximo 1 vez/año (o post-incidente).
- **Aviso previo:** 30 días.
- **Alcance:** limitado a datos del Responsable.
- **Costo:** a cargo del Responsable.
- **Confidencialidad:** NDA previo.

---

## 12. Responsabilidad

Atribución responde por daños derivados de:

- Incumplimiento de este DPA.
- Violación de GDPR/LFPDPPP.
- Negligencia en medidas de seguridad.

**Límite:** el monto pagado por el Responsable en los últimos
12 meses.

---

## 13. Ley aplicable

Este DPA se rige por:
- **GDPR** (si el Responsable está en la UE).
- **LFPDPPP** (si el Responsable está en México).
- **Leyes del Estado de México** (para disputas).

---

## 14. Anexo: Detalles técnicos

### Ubicación de datos

| Dato | Ubicación | Cifrado |
|---|---|---|
| Cuenta | Postgres (Railway) | AES-256-GCM |
| Contraseñas | Argon2id hash | — |
| API keys | SHA-256 hash | — |
| Logs | Railway + IPFS | AES-256-GCM |
| Certificados | IPFS + Arweave | Firma + hash |
| Blockchain | Ethereum | Público (solo hash) |

### Retención

| Dato | Retención |
|---|---|
| Cuenta activa | Mientras dure |
| Post-cancelación | 30 días |
| Facturación | 10 años (legal) |
| Logs de acceso | 365 días |
| Logs admin | 5 años |
| Certificados | Permanente |
| Blockchain | Permanente |

---

## 15. Firma

**Procesador:** Atribución
Marco Antonio Rojas Valdovinos
Ciudad de México, México

**Fecha:** _(al firmar con el cliente)_

**Responsable:** _(el cliente)_

---

**Contacto:** legal@atribucion.io
```
