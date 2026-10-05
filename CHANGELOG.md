# Changelog

Todos los cambios notables en este proyecto serán documentados aquí.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [Unreleased]

### Planeado
- Deploy a Railway
- Deploy a GitHub Pages
- Primer cliente piloto
- Certificación SOC 2 Type II

---

## [0.1.0] — 2026-10-05

### Añadido

#### Core criptográfico (`core/`)
- `crypto.py` — Firmas híbridas ECDSA + ML-DSA, hashing doble SHA-256 + SHA-3
- `did.py` — Identidad descentralizada W3C
- `contract.py` — Contrato de Atribución con validación
- `vc.py` — Credenciales verificables W3C VC 2.0
- `merkle.py` — Árboles Merkle para anclaje eficiente
- `anchor.py` — Anclaje a Ethereum (modo mock/real)
- `tsa.py` — Sellado de tiempo RFC 3161

#### API (`api/`)
- `main.py` — Servidor FastAPI con security headers
- `routes/agents.py` — POST /v1/agents
- `routes/actions.py` — POST /v1/agents/{id}/actions
- `routes/proofs.py` — GET /v1/proofs/{id}
- `routes/payments.py` — Checkout + webhook + status
- `routes/reports.py` — Informes mensuales JSON + PDF
- `middleware/auth.py` — Autenticación por API key

#### Lógica de negocio (`atribucion/`)
- `billing/plans.py` — Planes Free/Pro/Bank
- `billing/mercadopago.py` — Integración Mercado Pago
- `billing/invoices.py` — Generación de facturas
- `onboarding/flow.py` — Onboarding en 4 pasos
- `dashboard/repository.py` — Persistencia JSON

#### Engine (`engine/`)
- `runtime/state_machine.py` — Máquina de estados del agente
- `runtime/scheduler.py` — Planificador con prioridades y dependencias
- `runtime/executor.py` — Ejecutor de tareas
- `runtime/agent.py` — Ciclo de vida completo
- `orchestrator/madre.py` — Orquestador multi-agente
- `orchestrator/canonical_memory.py` — Memoria canónica
- `orchestrator/handoff.py` — Handoff real entre agentes

#### Mesh (`mesh/`)
- `transport/libp2p.py` — Nodo P2P con framing JSON
- `discovery/dht.py` — DHT Kademlia simplificada
- `consensus/crdt.py` — LWWRegister + GCounter + ORSet
- `storage/sqlite.py` — Persistencia local

#### Guardianes (`guards/`)
- 9 guardianes autónomos: SHA, ACTA, TSA, PHOENIX, NEXUS, VAULT, MRR, ORACLE, SENTINEL
- `base.py` — Contrato común
- `runner.py` — Runner de los 9 guardianes

#### KAF (`kaf/`)
- `controls/controls.yaml` — 47 controles en 12 dominios
- 4 niveles: KAF-1 Verified, KAF-2 Compliant, KAF-3 Assured, KAF-4 Sovereign
- `certification/auditor.py` — Auditor automático
- `certification/certificate.py` — Emisión de certificados

#### Robotics (`robotics/`)
- `identity/hardware_id.py` — Fingerprint de hardware
- `identity/did_robot.py` — DID vinculado a hardware
- `identity/proof_presence.py` — Proof-of-physical-presence

#### SDKs (`sdk/`)
- `python/` — Cliente oficial Python
- `js/` — Cliente oficial JavaScript/TypeScript

#### Apps (`apps/`)
- `portal/` — Landing pública
- `verifier/` — Verificador de certificados
- `dashboard/` — Panel del cliente
- `checkout/` — Páginas de pago

#### Contracts (`contracts/`)
- `AttributionRegistry.sol` — Contrato de anclajes
- `deploy/deploy_sepolia.py` — Script de deploy

#### Documentación (`docs/`)
- `quickstart.md` — Integración en 5 minutos
- `compliance/eu-ai-act.md` — Guía de cumplimiento
- `api/reference.md` — Referencia del API

#### Legal (`legal/`)
- `terms.md` — Términos de servicio
- `privacy.md` — Política de privacidad

#### CI/CD (`.github/workflows/`)
- `ci.yml` — Tests automáticos
- `deploy.yml` — Deploy a Pages + Railway

#### Licencias
- MIT
- Apache 2.0
- CC-BY-4.0 (specs)
- Trademark policy

---

## Tipos de cambios

- `Added` para nuevas funcionalidades
- `Changed` para cambios en funcionalidades existentes
- `Deprecated` para funcionalidades obsoletas
- `Removed` para funcionalidades eliminadas
- `Fixed` para correcciones
- `Security` para vulnerabilidades