```markdown
# Engine — Motor de agentes

**Soberanía computacional: el motor corre en tu nodo.**

---

## Filosofía

No dependemos de OpenAI, Anthropic ni Google para operar.
El motor corre local, con fallback remoto solo si se autoriza.

---

## Componentes

| Componente | Propósito |
|---|---|
| **runtime/** | Ciclo de vida, scheduler, executor, sandbox |
| **inference/** | LLMs locales + fallbacks remotos |
| **memory/** | Episódica, semántica, procedural, vectorial |
| **reasoning/** | Planner, CoT, tools, reflexión, debate |
| **learning/** | RLHF, fine-tuning, distill, experience |
| **orchestrator/** | MADRE (multi-agente) |

---

## Inferencia

### Backends locales

| Backend | Requisito | Cuándo usar |
|---|---|---|
| **llama.cpp** | Ninguno | CPU, Termux, móvil |
| **Ollama** | Ollama instalado | Desktop, fácil setup |
| **MLX** | Apple Silicon | Mac optimizado |
| **vLLM** | GPU NVIDIA | Producción alta perf |

### Fallbacks remotos

| Backend | Requisito | Cuándo usar |
|---|---|---|
| **OpenAI** | API key + autorización | Tareas complejas |
| **Anthropic** | API key + autorización | Razonamiento |
| **Gemini** | API key + autorización | Multimodal |

**NUNCA** se activan sin autorización explícita.

### Router

```python
from engine.inference import InferenceRouter, InferenceConfig, InferencePolicy

config = InferenceConfig(
    policy=InferencePolicy.LOCAL_FIRST,
    allow_remote=False,
)
router = InferenceRouter(config)
router.register(LlamaCppBackend(...), priority=1)
router.register(OllamaBackend(...), priority=2)

response = router.generate("Hola")
```

---

Memoria

Episódica — qué hice

```python
from engine.memory.episodic import EpisodicMemory

mem = EpisodicMemory(agent_id="agt_123")
mem.record("action", {"action": "trade", "result": "filled"})
recent = mem.get_recent(limit=10)
```

Semántica — qué sé

```python
from engine.memory.semantic import SemanticMemory

mem = SemanticMemory(agent_id="agt_123")
mem.add_fact("El usuario prefiere respuestas cortas")
facts = mem.search_facts("preferencias")
```

Procedural — cómo hago

```python
from engine.memory.procedural import ProceduralMemory

mem = ProceduralMemory(agent_id="agt_123")
mem.define_skill(
    name="trade_stock",
    description="Ejecuta una operación de trading",
    steps=[
        {"action": "fetch_price", "params": {"symbol": "AAPL"}},
        {"action": "check_risk", "params": {"max_loss": 100}},
        {"action": "execute", "params": {}},
    ],
)
```

Vectorial — búsqueda semántica

```python
from engine.memory.vector_store import VectorStore

store = VectorStore(agent_id="agt_123")
store.add("El usuario prefiere respuestas cortas")
results = store.search("preferencias", top_k=5)
```

---

Razonamiento

Chain of Thought

```python
from engine.reasoning.chain_of_thought import ChainOfThought

cot = ChainOfThought()
result = cot.reason("¿Debo invertir en AAPL?", llm_call=llm.generate)
print(result.conclusion)
```

Planner

```python
from engine.reasoning.planner import Planner

planner = Planner()
plan = planner.plan("Maximizar rendimiento del portafolio")
```

Debate

```python
from engine.reasoning.debate import Debate

debate = Debate()
debate.add_debater("optimista", "Eres optimista...")
debate.add_debater("pesimista", "Eres pesimista...")
result = debate.run("¿Invertir en AAPL?", llm_call=llm.call)
```

---

MADRE — Orquestación

```python
from engine.orchestrator.madre import MADRE, MotoAgent

madre = MADRE(session_id="proyecto-x")
madre.register(MotoAgent("Codex", call_codex))
madre.register(MotoAgent("Claude Code", call_claude))

# Broadcast
responses = await madre.broadcast("Diseñen un endpoint")

# Secuencia con handoff
responses = await madre.sequence(
    task="Refactorizar crypto.py",
    order=["Codex", "Claude Code"],
)
```

---

Sandbox

```python
from engine.runtime.sandbox import Sandbox

sandbox = Sandbox(timeout_seconds=5)
result = sandbox.run("print(2 + 2)")
print(result.stdout)  # "4"
```

---

Casos de uso

Caso Componentes
Bot de trading runtime + reasoning + memory
Asistente personal inference + memory + tools
Auditoría de agentes runtime + sandbox + memory
Multi-agente colaborativo orchestrator + MADRE

---

Roadmap

Fase Mes Componentes
1 1-3 runtime + orchestrator ✅
2 4-6 inference local ✅
3 7-12 memory + reasoning ✅
4 13+ learning + multi-nodo

---

Regla: el engine es opcional. Atribución funciona sin él.
Se usa cuando el cliente quiere soberanía computacional.

```