"""
Atribución Engine — Backend vLLM.

vLLM es el backend de más alto rendimiento para GPUs:
- PagedAttention (gestión eficiente de memoria)
- Continuous batching (múltiples requests simultáneos)
- 10-24x más throughput que HuggingFace transformers
- Compatible con API OpenAI

Requiere: pip install vllm (necesita GPU NVIDIA con CUDA)
Requiere: GPU con 16GB+ VRAM para modelos 7B+

Uso:
    backend = VLLMBackend(model="meta-llama/Llama-3.1-8B-Instruct")
    backend.load()
    response = backend.generate("Hola")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Iterator


logger = logging.getLogger(__name__)


@dataclass
class VLLMConfig:
    """Configuración del backend vLLM."""

    model: str = "meta-llama/Llama-3.1-8B-Instruct"
    tensor_parallel_size: int = 1
    gpu_memory_utilization: float = 0.90
    max_model_len: int = 8192
    dtype: str = "auto"
    trust_remote_code: bool = False
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.95
    extra_args: dict[str, Any] = field(default_factory=dict)


class VLLMBackend:
    """Backend de inferencia con vLLM (GPU de alta performance)."""

    name = "vllm"

    def __init__(self, config: VLLMConfig | None = None) -> None:
        self.config = config or VLLMConfig()
        self._engine: Any = None
        self._sampling_params: Any = None
        self._loaded = False

        logger.info("VLLMBackend configurado: %s", self.config.model)

    # ─── LIFECYCLE ─────────────────────────────────────────────

    def load(self) -> None:
        """Carga el modelo vLLM en memoria GPU."""
        if self._loaded:
            return

        try:
            from vllm import LLM, SamplingParams
        except ImportError as e:
            raise RuntimeError(
                "vllm no instalado o GPU no disponible. "
                "pip install vllm"
            ) from e

        logger.info("Cargando modelo vLLM (esto tarda 1-3 min)...")

        self._engine = LLM(
            model=self.config.model,
            tensor_parallel_size=self.config.tensor_parallel_size,
            gpu_memory_utilization=self.config.gpu_memory_utilization,
            max_model_len=self.config.max_model_len,
            dtype=self.config.dtype,
            trust_remote_code=self.config.trust_remote_code,
            **self.config.extra_args,
        )

        self._sampling_params = SamplingParams(
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            max_tokens=self.config.max_tokens,
        )

        self._loaded = True
        logger.info("Modelo vLLM cargado")

    def unload(self) -> None:
        """Libera el modelo de memoria GPU."""
        if self._engine is not None:
            del self._engine
            self._engine = None
        self._loaded = False

        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass

        logger.info("Modelo vLLM descargado")

    # ─── GENERATE ──────────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Genera texto con vLLM."""
        self.load()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # vLLM acepta prompts con chat template
        formatted = self._format_chat(messages)

        sampling = self._sampling_params
        if max_tokens or temperature is not None:
            from vllm import SamplingParams
            sampling = SamplingParams(
                temperature=temperature or self.config.temperature,
                top_p=self.config.top_p,
                max_tokens=max_tokens or self.config.max_tokens,
            )

        outputs = self._engine.generate([formatted], sampling)
        return outputs[0].outputs[0].text.strip()

    def generate_batch(
        self,
        prompts: list[str],
        max_tokens: int | None = None,
    ) -> list[str]:
        """Genera múltiples respuestas en paralelo (batching real)."""
        self.load()

        sampling = self._sampling_params
        if max_tokens:
            from vllm import SamplingParams
            sampling = SamplingParams(
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                max_tokens=max_tokens,
            )

        outputs = self._engine.generate(prompts, sampling)
        return [o.outputs[0].text.strip() for o in outputs]

    # ─── HELPERS ───────────────────────────────────────────────

    def _format_chat(self, messages: list[dict[str, str]]) -> str:
        """Formatea mensajes con el chat template del modelo."""
        parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            parts.append(f"<|{role}|>\n{content}")
        parts.append("<|assistant|>\n")
        return "\n".join(parts)

    # ─── INFO ──────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        return self._loaded

    def get_info(self) -> dict[str, Any]:
        info = {
            "name": self.name,
            "model": self.config.model,
            "loaded": self._loaded,
            "tensor_parallel_size": self.config.tensor_parallel_size,
            "gpu_memory_utilization": self.config.gpu_memory_utilization,
        }

        try:
            import torch
            info["cuda_available"] = torch.cuda.is_available()
            if torch.cuda.is_available():
                info["gpu_count"] = torch.cuda.device_count()
                info["gpu_name"] = torch.cuda.get_device_name(0)
        except ImportError:
            info["cuda_available"] = False

        return info