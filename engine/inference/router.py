"""
Atribución Engine — Router de inferencia.

Decide si una petición se procesa local o remota según política.

Políticas disponibles:
    local-only         → Solo backends locales. Si falla, error.
    local-first        → Local por defecto. Fallback remoto si autorizado.
    remote-first       → Remoto por defecto. Local si falla.
    remote-only        → Solo remotos (requiere autorización).
    cheapest           → Elige el más barato disponible.
    fastest            → Elige el de menor latencia.

Filosofía: soberanía computacional. Por defecto, local-only.

Uso:
    config = InferenceConfig(policy="local-first", allow_remote=False)
    router = InferenceRouter(config)
    router.register(LlamaCppBackend(...), priority=1)
    router.register(OpenAIBackend(...), priority=2)

    response = router.generate("Hola")
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterator


logger = logging.getLogger(__name__)


class InferencePolicy(str, Enum):
    """Políticas de routing."""

    LOCAL_ONLY = "local-only"
    LOCAL_FIRST = "local-first"
    REMOTE_FIRST = "remote-first"
    REMOTE_ONLY = "remote-only"
    CHEAPEST = "cheapest"
    FASTEST = "fastest"


@dataclass
class InferenceConfig:
    """Configuración del router."""

    policy: InferencePolicy = InferencePolicy.LOCAL_FIRST
    allow_remote: bool = False
    max_retries: int = 2
    retry_delay_seconds: float = 1.0
    timeout_seconds: float = 120.0
    log_routing_decisions: bool = True
    metrics_enabled: bool = True
    preferred_backend: str | None = None


@dataclass
class BackendEntry:
    """Backend registrado con metadata."""

    name: str
    backend: Any
    priority: int
    is_remote: bool
    requires_authorization: bool
    avg_latency_ms: float = 0.0
    call_count: int = 0
    failure_count: int = 0
    last_error: str | None = None


class InferenceRouter:
    """Router de inferencia con soporte multi-backend."""

    def __init__(self, config: InferenceConfig | None = None) -> None:
        self.config = config or InferenceConfig()
        self._backends: list[BackendEntry] = []
        self._routing_log: list[dict[str, Any]] = []
        logger.info(
            "InferenceRouter iniciado (policy=%s, allow_remote=%s)",
            self.config.policy.value,
            self.config.allow_remote,
        )

    # ─── REGISTRO ──────────────────────────────────────────────

    def register(
        self,
        backend: Any,
        priority: int = 10,
        requires_authorization: bool | None = None,
    ) -> None:
        """Registra un backend en el router."""
        name = getattr(backend, "name", backend.__class__.__name__)
        is_remote = getattr(backend, "is_remote", False)

        if requires_authorization is None:
            requires_authorization = getattr(
                backend, "requires_authorization", False
            )

        entry = BackendEntry(
            name=name,
            backend=backend,
            priority=priority,
            is_remote=is_remote,
            requires_authorization=requires_authorization,
        )
        self._backends.append(entry)
        self._backends.sort(key=lambda b: b.priority)

        logger.info(
            "Backend registrado: %s (priority=%d, remote=%s)",
            name, priority, is_remote,
        )

    def unregister(self, name: str) -> None:
        """Elimina un backend del router."""
        self._backends = [b for b in self._backends if b.name != name]

    def list_backends(self) -> list[dict[str, Any]]:
        """Lista backends registrados."""
        return [
            {
                "name": b.name,
                "priority": b.priority,
                "is_remote": b.is_remote,
                "requires_authorization": b.requires_authorization,
                "avg_latency_ms": round(b.avg_latency_ms, 1),
                "call_count": b.call_count,
                "failure_count": b.failure_count,
                "healthy": b.failure_count < 3,
            }
            for b in self._backends
        ]

    # ─── SELECCIÓN ─────────────────────────────────────────────

    def _select_backend(self) -> BackendEntry | None:
        """Selecciona el backend según política."""
        candidates = list(self._backends)

        if self.config.preferred_backend:
            for b in candidates:
                if b.name == self.config.preferred_backend:
                    return b

        policy = self.config.policy

        if policy == InferencePolicy.LOCAL_ONLY:
            candidates = [b for b in candidates if not b.is_remote]

        elif policy == InferencePolicy.LOCAL_FIRST:
            local = [b for b in candidates if not b.is_remote]
            remote = [b for b in candidates if b.is_remote]
            if local:
                return local[0]
            if self.config.allow_remote and remote:
                return remote[0]
            return None

        elif policy == InferencePolicy.REMOTE_FIRST:
            remote = [b for b in candidates if b.is_remote]
            local = [b for b in candidates if not b.is_remote]
            if self.config.allow_remote and remote:
                return remote[0]
            if local:
                return local[0]
            return None

        elif policy == InferencePolicy.REMOTE_ONLY:
            if not self.config.allow_remote:
                logger.error(
                    "Política remote-only pero allow_remote=False"
                )
                return None
            candidates = [b for b in candidates if b.is_remote]

        elif policy == InferencePolicy.CHEAPEST:
            candidates = sorted(
                candidates,
                key=lambda b: (b.is_remote, b.priority),
            )

        elif policy == InferencePolicy.FASTEST:
            healthy = [b for b in candidates if b.failure_count < 3]
            if healthy:
                candidates = sorted(healthy, key=lambda b: b.avg_latency_ms)

        if not candidates:
            return None

        return candidates[0]

    # ─── GENERATE ──────────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Genera texto usando el backend seleccionado."""
        last_error: Exception | None = None

        for attempt in range(self.config.max_retries + 1):
            backend = self._select_backend()
            if backend is None:
                raise RuntimeError("No hay backends disponibles")

            # Verificar autorización
            if backend.is_remote and not self.config.allow_remote:
                logger.warning(
                    "Backend remoto %s requiere allow_remote=True",
                    backend.name,
                )
                raise PermissionError(
                    f"Backend {backend.name} es remoto. "
                    "Activa allow_remote=True para usarlo."
                )

            start = time.time()
            try:
                result = backend.backend.generate(
                    prompt=prompt,
                    system=system,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                elapsed_ms = (time.time() - start) * 1000

                backend.call_count += 1
                backend.avg_latency_ms = (
                    backend.avg_latency_ms * 0.8 + elapsed_ms * 0.2
                )

                if self.config.log_routing_decisions:
                    self._log_routing(backend.name, elapsed_ms, success=True)

                return result

            except Exception as e:
                backend.failure_count += 1
                backend.last_error = str(e)
                last_error = e

                if self.config.log_routing_decisions:
                    self._log_routing(
                        backend.name, 0, success=False, error=str(e)
                    )

                logger.warning(
                    "Backend %s falló (intento %d/%d): %s",
                    backend.name, attempt + 1, self.config.max_retries + 1, e,
                )

                if attempt < self.config.max_retries:
                    time.sleep(self.config.retry_delay_seconds)
                    backend.failure_count = 0

        raise RuntimeError(
            f"Todos los backends fallaron. Último error: {last_error}"
        )

    def stream(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """Streaming usando el backend seleccionado."""
        backend = self._select_backend()
        if backend is None:
            raise RuntimeError("No hay backends disponibles")

        if backend.is_remote and not self.config.allow_remote:
            raise PermissionError(
                f"Backend {backend.name} es remoto. "
                "Activa allow_remote=True."
            )

        if not hasattr(backend.backend, "stream"):
            # Fallback a generate
            yield backend.backend.generate(
                prompt=prompt, system=system, max_tokens=max_tokens,
            )
            return

        yield from backend.backend.stream(
            prompt=prompt, system=system, max_tokens=max_tokens,
        )

    # ─── LOGGING ───────────────────────────────────────────────

    def _log_routing(
        self,
        backend_name: str,
        latency_ms: float,
        success: bool,
        error: str | None = None,
    ) -> None:
        from datetime import datetime, timezone

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "backend": backend_name,
            "latency_ms": round(latency_ms, 2),
            "success": success,
            "error": error,
            "policy": self.config.policy.value,
        }
        self._routing_log.append(entry)

        if len(self._routing_log) > 1000:
            self._routing_log = self._routing_log[-500:]

    def get_routing_log(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._routing_log[-limit:]

    # ─── INFO ──────────────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        return {
            "policy": self.config.policy.value,
            "allow_remote": self.config.allow_remote,
            "backends_count": len(self._backends),
            "backends": self.list_backends(),
            "routing_events": len(self._routing_log),
        }

    def close(self) -> None:
        """Cierra todos los backends."""
        for entry in self._backends:
            try:
                if hasattr(entry.backend, "close"):
                    entry.backend.close()
                elif hasattr(entry.backend, "unload"):
                    entry.backend.unload()
            except Exception as e:
                logger.warning("Error cerrando %s: %s", entry.name, e)