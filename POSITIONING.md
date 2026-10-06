# Atribución — Qué es, para quién, por qué importa

> Documento de posicionamiento. Una página. Para inversores, clientes,
> reguladores o cualquier persona que pregunte "¿qué haces?" en 30 segundos.

---

## En una frase

**Atribución certifica agentes de IA para cumplir con el EU AI Act,
con prueba criptográfica inmutable y sin que los datos salgan del
dispositivo del cliente.**

---

## El problema

En agosto de 2026, el **EU AI Act** entra en su fase más estricta:
todo sistema de IA de alto riesgo desplegado en Europa deberá poder
**demostrar** sus capacidades, sus límites y su historial de
comportamiento. Multas: hasta **35M€ o 7% del facturación global**.

Hoy las empresas resuelven esto con:
- **Consultoras** (lentas, caras, no verificables).
- **Auditorías anuales** (foto del momento, obsoletas al mes siguiente).
- **Promesas internas** (documentos que nadie puede verificar).

**Nadie ofrece certificación continua, verificable por terceros,
sin exponer datos sensibles a un proveedor externo.**

---

## La solución

Atribución ofrece **certificación KAF** en 4 niveles:

| Nivel | Nombre | Qué garantiza |
|---|---|---|
| **KAF-1** | Verified | El agente existe, tiene identidad DID, responde |
| **KAF-2** | Compliant | Cumple controles básicos del EU AI Act |
| **KAF-3** | Assured | Auditoría continua con 9 guardianes automáticos |
| **KAF-4** | Sovereign | Inferencia local, datos nunca salen del cliente |

Cada certificado:
- Se **ancla en Ethereum** (prueba pública, inmutable, sin permiso).
- Se **verifica en 1 clic** desde `verifier.atribucion.io` sin login.
- Se **revoca públicamente** si el agente falla (historial transparente).

---

## Los 3 diferenciadores reales

### 1. Soberanía computacional
El motor de inferencia corre **en el hardware del cliente**
(llama.cpp, Ollama, MLX, vLLM). Ningún dato se envía a OpenAI,
Anthropic o Google. Fallback a APIs remotas **solo con autorización
explícita y registro auditable**.

### 2. Prueba criptográfica, no promesas
No entregamos un PDF firmado. Entregamos un **registro on-chain**
que cualquier regulador, cliente o competidor puede verificar sin
pedirnos permiso. Si revocamos un certificado, queda en el historial
para siempre.

### 3. Compliance continuo, no anual
9 guardianes corren cada 2 minutos auditando:
- Integridad SHA-256/SHA-3 de certificados
- Detección de replay attacks
- Integridad Merkle de anclajes on-chain
- Bruteforce y fuzzing en logs
- Fugas de claves privadas y credenciales AWS
- Métricas de negocio (MRR, tenants inactivos)
- Consistencia de DIDs y credenciales verificables

Si algo falla, el certificado se congela automáticamente y se notifica
al equipo de seguridad.

---

## Para quién es

**Cliente primario:**
- Empresas europeas que despliegan IA de alto riesgo
  (salud, finanzas, RRHH, educación, infraestructura crítica).
- Fecha límite: **2 de agosto de 2026**.

**Cliente secundario:**
- Startups de IA que quieren diferenciarse por compliance.
- Integradores de IA que necesitan certificar los agentes
  que despliegan para sus clientes.
- Gobiernos y reguladores que necesitan verificar sin
  acceso privilegiado.

**Mercado inicial:**
- España, México, Argentina, Colombia (hispanohablantes, AI Act aplica
  a cualquiera que opere en la UE).
- Pricing en EUR/USD. Pagos vía MercadoPago en LATAM.

---

## Modelo de negocio

| Plan | Precio | Qué incluye |
|---|---|---|
| **Starter** | €99/mes | KAF-1 y KAF-2, verificación pública |
| **Pro** | €499/mes | KAF-3, 9 guardianes, anclaje on-chain |
| **Enterprise** | €2,500/mes | KAF-4, inferencia local, SLA, soporte |
| **Auditoría puntual** | €5,000 | Certificación one-shot, sin suscripción |

Margen bruto estimado: **>85%** (infraestructura on-chain ~€0.50 por
certificado; coste dominante es desarrollo, no operación).

---

## La demo de 5 minutos

1. Un agente de IA quiere certificarse.
2. Se conecta a `api.atribucion.io`, obtiene DID y VC.
3. Corre los 9 guardianes.
4. Si pasa: certificado KAF-3 emitido y **anclado en Ethereum**.
5. Un regulador entra a `verifier.atribucion.io`, pega el ID,
   ve **✅ válido, emitido el 6 de oct 2026, nunca revocado**.
6. Si el agente falla en el futuro: **se revoca automáticamente**,
   y el regulador ve el historial completo.

**Sin login. Sin permiso. Sin confiar en nosotros.**

---

## Qué NO somos

- **No somos un LLM.** No entrenamos modelos.
- **No somos una consultora.** No vendemos horas.
- **No somos una auditoría anual.** Somos continuos.
- **No custodiamos datos.** El cliente mantiene todo en su hardware.

---

## Estado actual

- Arquitectura completa: 150+ archivos.
- Core, guards, contracts, robotics, API, SDK: funcionales.
- En construcción: motor de inferencia local (llama.cpp, Ollama,
  MLX, vLLM).
- **Falta:** primer cliente piloto, demo pública, auditoría externa
  de los contratos on-chain.

---

## Contacto

**Marco Antonio Rojas Valdovinos** — fundador
`marco.a.rojas.v@hotmail.com

Más info: `docs/quickstart.md`