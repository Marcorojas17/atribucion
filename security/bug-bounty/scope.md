# Bug Bounty Scope

**Última actualización:** 2026-10-06
**Programa:** Atribución Bug Bounty

---

## In Scope

### 1. API de producción

| Endpoint | Descripción | URL |
|---|---|---|
| API principal | Endpoints públicos | `https://api.atribucion.io` |
| Verificador | Verificación pública | `https://atribucion.io/verify/*` |
| Docs | Documentación | `https://docs.atribucion.io` |
| Status | Estado del sistema | `https://status.atribucion.io` |

**Tipos de vulnerabilidad aceptados:**
- Autenticación / autorización
- Inyección (SQL, NoSQL, comandos)
- SSRF, XXE, deserialización
- IDOR, privilege escalation
- Exposición de datos sensibles
- Race conditions
- Business logic flaws
- Criptografía débil

### 2. Aplicaciones web

| App | URL | Estado |
|---|---|---|
| Portal | `https://atribucion.io` | Producción |
| Dashboard | `https://atribucion.io/dashboard` | Producción |
| Verificador | `https://atribucion.io/verify` | Producción |
| Checkout | `https://atribucion.io/checkout` | Producción |

### 3. SDKs

| SDK | Repositorio | Estado |
|---|---|---|
| Python | `github.com/Marcorojas17/atribucion/sdk/python` | Producción |
| JavaScript | `github.com/Marcorojas17/atribucion/sdk/js` | Producción |

### 4. Contratos inteligentes

| Contrato | Red | Estado |
|---|---|---|
| AttributionRegistry | Sepolia | Testnet |
| KAFRegistry | Sepolia | Testnet |
| PaymentSplitter | Sepolia | Testnet |

**Nota:** Bug bounty específico para smart contracts. Ver reglas adicionales.

---

## Out of Scope

### 1. Infraestructura

- Railway (hosting)
- GitHub (repositorio)
- Cloudflare (CDN)
- Proveedores de terceros

**Razón:** vulnerabilidades de terceros deben reportarse a ellos.

### 2. Dependencias

- Vulnerabilidades con CVE público
- Librerías obsoletas sin exploit específico en Atribución
- Frameworks (FastAPI, React, etc.)

**Razón:** no están bajo nuestro control directo.

### 3. Tipos específicos

| Tipo | Por qué está fuera |
|---|---|
| Self-XSS | Requiere interacción manual del usuario |
| Missing rate limiting sin exploit | Sin impacto demostrable |
| Missing security headers | Sin impacto específico |
| Clickjacking sin PoC | Bajo impacto |
| CSRF en endpoints sin auth | Sin impacto |
| Email spoofing | Bajo impacto |
| SPF/DKIM/DMARC | Fuera de scope |
| DNS rebinding | Caso por caso |
| Bugs de UI/UX | No son seguridad |
| Missing `autocomplete="off"` | Informativo |
| Version disclosure | Informativo |
| SSL/TLS config sin exploit | Informativo |

### 4. Físicos

- Acceso físico a servidores
- Ingeniería social a empleados
- Ataques a infraestructura de terceros

**Prohibido explícitamente.**

### 5. DoS/DDoS

- Ataques volumétricos
- Agotamiento de recursos
- Rate limit abuse sin contexto

**Prohibido explícitamente.**

---

## Reglas para pruebas

### ✅ Permitido
- Testear solo con cuentas propias.
- Usar PoC mínimos.
- Documentar cada paso.
- Reportar inmediatamente.
- Coordinar divulgación.

### ⚠️ Requiere autorización previa
- Tests automatizados (scanners).
- Pruebas de carga.
- Fuzzing agresivo.
- Tests con múltiples IPs.

### ❌ Prohibido
- Dañar datos.
- Acceder a datos de otros usuarios.
- Modificar el sistema sin autorización.
- Retener vulnerabilidad sin reportar.
- Vender la vulnerabilidad.

---

## Programa de recompensas

| Severidad | CVSS | Recompensa |
|---|---|---|
| Crítica | 9.0-10.0 | $5.000 |
| Alta | 7.0-8.9 | $1.500 |
| Media | 4.0-6.9 | $500 |
| Baja | 0.1-3.9 | $100 |
| Informativa | 0.0 | Crédito |

**Bonos:**
- +50% por cadenas de vulnerabilidades.
- +25% si está en producción.
- +100% si es zero-day.

---

## Scope específico: Smart Contracts

### In scope
- `AttributionRegistry.sol`
- `KAFRegistry.sol`
- `PaymentSplitter.sol`

### Tipos aceptados
- Reentrancy
- Integer overflow/underflow
- Access control flaws
- Front-running
- Gas optimization bugs con impacto
- Logic errors

### Recompensas específicas
| Severidad | Recompensa |
|---|---|
| Crítica | $10.000 |
| Alta | $3.000 |
| Media | $1.000 |

### Redes
- Solo testnet (Sepolia) hasta deploy en Mainnet.
- Una vez en Mainnet, recompensas se duplican.

---

## Scope específico: Cryptography

### In scope
- Firmas híbridas (ECDSA + ML-DSA)
- Implementación de Merkle trees
- DID Document verification
- VC 2.0 implementation

### Tipos aceptados
- Timing attacks
- Fault attacks
- Side-channel leaks
- Weak randomness
- Incorrect padding
- Algorithm confusion

### Recompensas específicas
| Severidad | Recompensa |
|---|---|
| Crítica | $7.500 |
| Alta | $2.500 |
| Media | $750 |

---

## Cómo reportar

### Canal principal
**HackerOne:** hackerone.com/atribucion

### Canal alternativo (crítico)
**Email:** security@atribucion.io
**PGP:** (publicar en mes 6)

### Formato requerido
```markdown
## Título
[descripción corta]

## Severidad
[crítica | alta | media | baja]

## CVSS
[score]

## Pasos para reproducir
1. ...
2. ...
3. ...

## PoC
[código, screenshots, video]

## Impacto
[qué puede hacer un atacante]

## Fix sugerido
[opcional]

## Metadata
- URL afectada:
- Fecha de descubrimiento:
- Herramientas usadas:

Fase Plazo
Confirmación de recepción 24h
Triaje inicial 72h
Fix (crítico) 7 días
Fix (alto) 30 días
Fix (medio) 60 días
Fix (bajo) 90 días
Pago 15 días post-fix
Divulgación pública 90 días post-fix

