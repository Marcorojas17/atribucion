"""
Atribución Engine — Inferencia.

Soberanía computacional: el motor corre en el nodo del ciudadano.
Local-first, con fallback a APIs remotas solo si el usuario lo autoriza.

Módulos:
    local/     → llama.cpp, Ollama, MLX, vLLM
    fallback/  → OpenAI, Anthropic, Gemini (solo si se autoriza)
    router.py  → Decide local vs remoto según política
    quantize.py → Cuantización de modelos

Uso:
    from engine.inference import InferenceRouter, InferenceConfig

    router = InferenceRouter(InferenceConfig(policy="local-first"))
    response = await router.generate("Hola, ¿cómo estás?")
"""

from engine.inference.router import InferenceConfig, InferenceRouter, InferencePolicy

__version__ = "0.1.0"

__all__ = ["InferenceConfig", "InferenceRouter", "InferencePolicy"]