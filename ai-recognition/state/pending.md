# Deuda pendiente

**Lista viva de lo que falta. Marcar 🔴 cuando se cierre.**

---

## Bloqueantes (impacto directo)

- [ ] Deploy API a Railway
- [ ] Deploy apps a GitHub Pages
- [ ] Primer certificado real en Sepolia
- [ ] Primer cliente contactado

## Archivos sin crear

### ai-recognition/
- [ ] `mcp/server.py` (funcional)
- [ ] `mcp/tools.py`
- [ ] `mcp/resources.py`
- [ ] `mcp/prompts.py`
- [ ] `mcp/config.json`

### engine/
- [ ] `inference/local/llama_cpp.py`
- [ ] `inference/local/ollama.py`
- [ ] `inference/local/mlx.py`
- [ ] `inference/local/vllm.py`
- [ ] `inference/fallback/openai.py`
- [ ] `inference/fallback/anthropic.py`
- [ ] `inference/fallback/gemini.py`
- [ ] `inference/router.py`
- [ ] `inference/quantize.py`
- [ ] `memory/episodic.py`
- [ ] `memory/semantic.py`
- [ ] `memory/procedural.py`
- [ ] `memory/vector_store.py`
- [ ] `memory/graph_store.py`
- [ ] `memory/consolidation.py`
- [ ] `reasoning/planner.py`
- [ ] `reasoning/chain_of_thought.py`
- [ ] `reasoning/tool_use.py`
- [ ] `reasoning/reflection.py`
- [ ] `reasoning/debate.py`
- [ ] `learning/local_rlhf.py`
- [ ] `learning/fine_tune.py`
- [ ] `learning/distill.py`
- [ ] `learning/experience.py`
- [ ] `runtime/sandbox.py`
- [ ] `orchestrator/context.py`

### mesh/
- [ ] `transport/quic.py`
- [ ] `transport/webrtc.py`
- [ ] `transport/nostr.py`
- [ ] `discovery/mdns.py`
- [ ] `discovery/rendezvous.py`
- [ ] `discovery/bootstrap.py`
- [ ] `consensus/raft.py`
- [ ] `consensus/byzantine.py`
- [ ] `consensus/gossip.py`
- [ ] `storage/dexie.py`
- [ ] `storage/ipfs.py`
- [ ] `storage/arweave.py`
- [ ] `storage/replication.py`
- [ ] `sync/delta.py`
- [ ] `sync/conflict.py`
- [ ] `sync/merkle_sync.py`

### guards/
- [ ] 9 `policies.yaml` (uno por guardián)
- [ ] 9 carpetas `tests/`

### kaf/
- [ ] 13 archivos `framework/KAF-XXX.md`
- [ ] `controls/evidence.yaml`
- [ ] 6 archivos `controls/mapping/*.yaml`
- [ ] `certification/nft.py`
- [ ] `certification/registry.py`

### robotics/
- [ ] `drivers/ros2.py`
- [ ] `drivers/mqtt.py`
- [ ] `drivers/modbus.py`
- [ ] `perception/vision.py`
- [ ] `perception/lidar.py`
- [ ] `perception/audio.py`
- [ ] `actuation/motors.py`
- [ ] `actuation/servos.py`
- [ ] `actuation/safety.py`

### contracts/
- [ ] `PaymentSplitter.sol`
- [ ] `KAFRegistry.sol`
- [ ] `deploy/deploy_mainnet.py`
- [ ] `deploy/config.json`

### docs/
- [ ] `index.md`
- [ ] `kaf/` (5 archivos)
- [ ] `payments/mercadopago.md`
- [ ] `payments/mxn.md`
- [ ] `security/` (5 archivos)
- [ ] `mesh/` (3 archivos)
- [ ] `engine/` (3 archivos)

### security/
- [ ] 11 archivos (compliance + policies + audits + bug-bounty)

### payments/
- [ ] 12 archivos (mercadopago, mxn, nom151)

### infra/
- [ ] terraform/
- [ ] k8s/
- [ ] vault/

### tests/
- [ ] unit/
- [ ] integration/
- [ ] e2e/
- [ ] fixtures/

### scripts/
- [ ] `seed_demo.py`
- [ ] `generate_report.py`

---

## Deuda estructural

- [ ] Consolidar `atribucion/api/` con `api/routes/`
- [ ] Verificar `sdk/js/src/crypto.ts` (no `.py`)
- [ ] Eliminar `legal/LICENSE-*` duplicados
- [ ] Eliminar `core/tests/` duplicados

---

**Total: ~160 archivos pendientes.**

**Última actualización:** 2026-10-05