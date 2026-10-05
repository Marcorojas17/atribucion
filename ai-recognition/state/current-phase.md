# Estado Actual del Proyecto

**Fase:** 0 → 1 (transición)
**Progreso global:** ~50%
**Última actualización:** 2026-10-05

---

## 📊 Progreso por dominio

| Dominio | Progreso | Estado |
|---|---|---|
| **Documentación legal** | 80% | 🟢 Constitución, marco, ciudadanía, moneda, tribunales |
| **Core criptográfico** | 100% | 🟢 7 módulos completos |
| **API** | 95% | 🟢 6 routers + middleware |
| **Tests** | 80% | 🟢 31 tests |
| **SDK Python** | 100% | 🟢 Completo |
| **SDK JS** | 100% | 🟢 Completo |
| **Guardianes** | 80% | 🟡 9 agentes, faltan policies |
| **Engine** | 60% | 🟡 Runtime + orchestrator, falta inference |
| **Mesh** | 40% | 🟡 P2P + DHT + CRDT + SQLite |
| **KAF** | 60% | 🟡 Framework definido, falta mapping |
| **Robotics** | 30% | 🟡 Identity, faltan drivers |
| **AI Recognition** | 30% | 🟡 Perfiles + estado, falta MCP |
| **Producto (apps)** | 90% | 🟢 4 apps HTML |
| **Deploy** | 0% | 🔴 Sin producción |
| **Primer cliente** | 0% | 🔴 Sin cliente |

**Total ponderado: ~50%**

---

## ✅ Lo que ya está hecho

- Constitución completa (KONSTITUTION.md)
- Marco de responsabilidad de agentes
- Schema JSON del Contrato de Atribución
- Territorio criptográfico (4 capas)
- Ciudadanía (4 tipos)
- Moneda KRN (5 Proofs)
- Tribunales (3 niveles)
- Core criptográfico (7 módulos, 36 tests)
- API completa (6 routers + 4 middleware)
- Billing + Onboarding + Dashboard
- SDK Python + SDK JS
- 9 guardianes con motor real
- Engine (runtime + MADRE)
- Mesh (P2P + DHT + CRDT)
- KAF (niveles + 47 controles)
- Robotics (identity)
- 4 apps HTML (portal, verifier, dashboard, checkout)
- Docs (quickstart, EU AI Act, API reference)
- Legal (terms, privacy)

## 🔴 Lo que falta (priorizado)

### Prioridad 1 (bloquea el negocio)
- [ ] Deploy de API a Railway
- [ ] Deploy de apps a GitHub Pages
- [ ] Primer certificado real en Sepolia
- [ ] Primer cliente contactado

### Prioridad 2 (bloquea el producto)
- [ ] ai-recognition/mcp/server.py funcional
- [ ] engine/inference (llama.cpp, ollama)
- [ ] guards/*/policies.yaml
- [ ] kaf/controls/mapping (6 archivos)

### Prioridad 3 (visión)
- [ ] engine/memory (6 archivos)
- [ ] engine/reasoning (5 archivos)
- [ ] mesh ampliaciones (QUIC, Raft, IPFS)
- [ ] robotics drivers

---

## 🚦 Próxima acción

**Esta semana:**
1. Terminar `ai-recognition/` (MCP funcional).
2. Deploy del API a Railway.
3. Landing en GitHub Pages.
4. Primer `curl` real end-to-end.

**Próximas 4 semanas:**
1. Primer cliente contactado.
2. Post de LinkedIn.
3. 30 empresas europeas contactadas.

---

**Próxima revisión:** al desplegar en producción.