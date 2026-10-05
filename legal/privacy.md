# Política de Privacidad

**Última actualización:** 4 de octubre de 2026

---

## 1. Resumen ejecutivo

Atribución es un servicio técnico de compliance. Nuestra
política es simple:

- **Datos de acciones:** se anclan a Ethereum (hashes).
- **Datos personales:** NUNCA se anclan. Solo hashes.
- **Contenido real:** cifrado, almacenado en IPFS, controlado
  por ti.
- **Derecho al olvido:** sí, con limitaciones (blockchain es
  inmutable, pero el contenido se puede borrar).

---

## 2. Responsable del tratamiento

**Atribución** — operado por Marco Antonio Rojas Valdovinos.
Ciudad de México, México.
Email: privacy@atribucion.io

---

## 3. Qué datos recopilamos

### 3.1. Datos de cuenta

- Email
- Nombre de la empresa
- País
- Contraseña (hasheada, nunca en texto plano)

### 3.2. Datos de agente

- Nombre del agente
- Nivel de autonomía
- Proveedor del modelo LLM
- Clave pública (nunca la privada)
- DID (identificador público)

### 3.3. Datos de acciones

- Nombre de la acción
- Input y output (hasheados)
- Razonamiento (hasheado)
- Timestamp
- Prueba criptográfica (firmas, hashes, anclajes)

### 3.4. Datos de uso

- IP (hasheada a los 30 días)
- User agent
- Endpoints consultados
- Errores y latencia

---

## 4. Cómo usamos los datos

| Uso | Base legal | Retención |
|---|---|---|
| Prestar el servicio | Contrato | Mientras la cuenta esté activa |
| Cumplir obligaciones legales | Obligación legal | 10 años (registros fiscales) |
| Prevenir fraude | Interés legítimo | 2 años |
| Mejorar el servicio | Interés legítimo | 2 años |
| Enviar emails transaccionales | Contrato | Mientras la cuenta esté activa |
| Enviar emails de marketing | Consentimiento | Hasta revocación |

---

## 5. Derecho al olvido

Tienes derecho a solicitar la eliminación de tus datos.
Pero hay una limitación técnica:

**La blockchain es inmutable.** Un hash anclado en Ethereum
no se puede borrar. Sin embargo:

- El **hash** no contiene información personal por sí mismo.
- El **contenido real** está cifrado y vive en IPFS, controlado
  por ti.
- Si revocas el acceso, el contenido se vuelve inaccesible.
- Los hashes permanecen, pero sin contenido asociado.

**Resultado:** cumplimos con GDPR Art. 17 dentro de las
posibilidades técnicas de una blockchain.

---

## 6. Compartición con terceros

**No vendemos tus datos.** Nunca.

Compartimos datos con:

| Tercero | Qué | Por qué |
|---|---|---|
| Ethereum | Hashes | Anclaje inmutable |
| IPFS/Arweave | Contenido cifrado | Almacenamiento permanente |
| DigiCert | Hashes | Sellado de tiempo RFC 3161 |
| Mercado Pago | Datos de pago | Procesar pagos |
| Railway | Datos de aplicación | Hosting del API |
| Cloudflare | Datos de tráfico | DDoS + CDN |

Todos los terceros cumplen con GDPR y tienen acuerdos de
procesamiento de datos firmados.

---

## 7. Transferencias internacionales

Los datos pueden transferirse a:

- Estados Unidos (Railway, Cloudflare, Ethereum nodes)
- Unión Europea (DigiCert, nodos Ethereum)
- México (Atribución HQ)

Usamos **Standard Contractual Clauses (SCCs)** aprobadas por
la Comisión Europea para transferencias fuera del EEE.

---

## 8. Seguridad

Implementamos:

- **Cifrado en tránsito:** TLS 1.3
- **Cifrado en reposo:** AES-256-GCM
- **Firmas híbridas:** ECDSA + ML-DSA (post-cuántico)
- **HSM:** claves privadas nunca salen del hardware seguro
- **Zero Trust:** verificación en cada request
- **Auditoría:** logs inmutables de todos los accesos
- **Pentesting:** auditoría externa anual

---

## 9. Cookies

Usamos cookies solo para:

- **Sesión:** mantenerte logueado.
- **CSRF:** prevenir ataques cross-site.
- **Preferencias:** idioma, tema.

**No usamos cookies de tracking ni publicidad.**

---

## 10. Menores

El servicio no está destinado a menores de 16 años.
No recopilamos conscientemente datos de menores.

---

## 11. Tus derechos (GDPR)

Si estás en la UE, tienes derecho a:

- **Acceso:** solicitar copia de tus datos.
- **Rectificación:** corregir datos inexactos.
- **Supresión:** solicitar eliminación (con limitaciones).
- **Portabilidad:** exportar tus datos en formato JSON.
- **Oposición:** oponerte al tratamiento.
- **Limitación:** restringir el tratamiento.

**Ejercer derechos:** privacy@atribucion.io
**Respuesta:** en 30 días máximo.

---

## 12. Tus derechos (LFPDPPP — México)

Si estás en México, tienes derecho a (derechos ARCO):

- **Acceso:** conocer tus datos personales.
- **Rectificación:** corregir datos inexactos.
- **Cancelación:** solicitar eliminación.
- **Oposición:** oponerte al tratamiento.

**Ejercer derechos:** privacy@atribucion.io

---

## 13. Cambios a esta política

Notificaremos cambios por email con 30 días de antelación.
La versión más reciente siempre está en:

```text
https://atribucion.io/legal/privacy

---

14. Contacto

· Privacidad: marco.a.rojas.v@hotmail.com
· DPO: marco.a.rojas.v@hotmail.com
· Quejas: ante la autoridad de protección de datos de
  tu país.

---

Atribución — Marco Antonio Rojas Valdovinos

```