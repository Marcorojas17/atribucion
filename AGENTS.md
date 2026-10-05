# AGENTS.md

**Contrato para agentes IA que operen en este repositorio.**

---

## Identidad del proyecto

**Atribución** — Compliance EU AI Act para agentes IA en un solo endpoint.

Construido por Marco Antonio Rojas Valdovinos, desde México.

---

## Principios innegociables

1. **Realidad sobre marketing.** Si dices "handoff real", debe existir código.
2. **Estándar sobre invención.** Usa W3C DID, VC 2.0, RFC 3161, NIST PQC.
3. **Trazabilidad total.** Cada acción: DID + firma + log + anclaje.
4. **Post-cuántico desde el día 1.** Firmas híbridas ECDSA + ML-DSA.
5. **Legal por diseño.** Cumple EU AI Act, GDPR, eIDAS 2.0.
6. **Cero deuda estructural.** Sin duplicados, sin typos, sin huérfanos.
7. **Ningún vacío sin nombre.** Deuda explícita con 🔴.

---

## Arquitectura canónica

```text
core/         → Protocolo criptográfico
api/          → Endpoints HTTP
atribucion/   → Lógica de negocio (billing, onboarding, dashboard)
engine/       → Motor de agentes + MADRE
mesh/         → Malla P2P
guards/       → 9 guardianes autónomos
kaf/          → Estándar de certificación
robotics/     → Interfaz con hardware
sdk/          → SDKs (Python + JS)
apps/         → Frontend estático
contracts/    → Solidity
docs/         → Documentación
legal/        → Términos y privacidad


---

Stack obligatorio

· Python 3.11+
· FastAPI + Pydantic v2
· cryptography + web3
· Node 18+ + TypeScript
· SQLite (dev) → Postgres (prod)
· Ethereum Sepolia → Mainnet
· Docker + docker-compose

---

Anti-patrones prohibidos

· ❌ "Sería bueno considerar..." → propón o cállate.
· ❌ Duplicar conceptos (agentes x2, evidence-os x2).
· ❌ Carpetas numeradas mezcladas con semánticas.
· ❌ Más de 6 workflows en .github/.
· ❌ Claims sin código que los respalde.
· ❌ Reinventar crypto, DID, VCs, timestamping.

---

Formato de respuesta obligatorio

1. DIAGNÓSTICO — qué falta y por qué importa.
2. DISEÑO — estructura concreta con rutas.
3. IMPLEMENTACIÓN — código completo.
4. RIESGOS — qué puede fallar.
5. SIGUIENTE PASO — acción concreta.

---

Continuidad entre sesiones

Antes de responder en sesión nueva:

1. Lee AI-CONTEXT.md.
2. Revisa el estado actual del repo.
3. Pregunta "¿en qué trabajamos hoy?".
4. No reinicies desde cero.

---

Frase guía: Atribución no compite con Microsoft, Google u OpenAI. Construye la capa que todas ellas necesitarán adoptar.

```