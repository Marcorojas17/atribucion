"""
Atribución Engine — Tool Use.

Registro y ejecución de herramientas que el agente puede usar.

Una "tool" es una función con esquema, validación y auditoría.
Cada uso se registra para EU AI Act Art. 12.

Uso:
    registry = ToolRegistry()

    @registry.register(
        name="fetch_price",
        description="Obtiene el precio actual de un símbolo",
        params={"symbol": "str"},
    )
    def fetch_price(symbol: str) -> float:
        return 175.32

    result = registry.call("fetch_price", {"symbol": "AAPL"})
"""

from __future__ import annotations

import inspect
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4


logger = logging.getLogger(__name__)


@dataclass
class ToolDefinition:
    """Definición de una herramienta."""

    name: str
    description: str
    params_schema: dict[str, str]
    returns_schema: str
    handler: Callable[..., Any]
    requires_auth: bool = False
    rate_limit_per_min: int | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class ToolCall:
    """Registro de una llamada a herramienta."""

    id: str
    tool_name: str
    params: dict[str, Any]
    result: Any
    success: bool
    duration_ms: float
    timestamp: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ToolRegistry:
    """Registro y ejecución de herramientas."""

    def __init__(self) -> None:
        self.tools: dict[str, ToolDefinition] = {}
        self.call_log: list[ToolCall] = []
        logger.info("ToolRegistry listo")

    # ─── REGISTER ──────────────────────────────────────────────

    def register(
        self,
        name: str,
        description: str,
        params: dict[str, str] | None = None,
        returns: str = "any",
        requires_auth: bool = False,
        rate_limit_per_min: int | None = None,
        tags: list[str] | None = None,
    ) -> Callable[[Callable], Callable]:
        """
        Decorador para registrar una herramienta.

        Uso:
            @registry.register(name="foo", description="bar")
            def foo(x: int) -> int:
                return x * 2
        """
        def decorator(func: Callable) -> Callable:
            tool = ToolDefinition(
                name=name,
                description=description,
                params_schema=params or self._infer_params(func),
                returns_schema=returns,
                handler=func,
                requires_auth=requires_auth,
                rate_limit_per_min=rate_limit_per_min,
                tags=tags or [],
            )
            self.tools[name] = tool
            logger.info("Tool registrada: %s", name)
            return func
        return decorator

    def _infer_params(self, func: Callable) -> dict[str, str]:
        """Infiere parámetros desde type hints."""
        sig = inspect.signature(func)
        return {
            name: (
                param.annotation.__name__
                if hasattr(param.annotation, "__name__")
                else str(param.annotation)
            )
            for name, param in sig.parameters.items()
        }

    def unregister(self, name: str) -> bool:
        if name in self.tools:
            del self.tools[name]
            return True
        return False

    # ─── CALL ──────────────────────────────────────────────────

    def call(
        self,
        name: str,
        params: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> Any:
        """Ejecuta una herramienta por nombre."""
        import time

        tool = self.tools.get(name)
        if not tool:
            raise ValueError(f"Tool no existe: {name}")

        if tool.requires_auth and not (context or {}).get("authorized"):
            raise PermissionError(f"Tool {name} requiere autenticación")

        params = params or {}
        start = time.time()

        try:
            result = tool.handler(**params)
            elapsed_ms = (time.time() - start) * 1000

            self._log_call(ToolCall(
                id=f"call_{uuid4().hex[:12]}",
                tool_name=name,
                params=params,
                result=result,
                success=True,
                duration_ms=elapsed_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
            ))

            return result

        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            self._log_call(ToolCall(
                id=f"call_{uuid4().hex[:12]}",
                tool_name=name,
                params=params,
                result=None,
                success=False,
                duration_ms=elapsed_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
                error=str(e),
            ))
            raise

    def _log_call(self, call: ToolCall) -> None:
        self.call_log.append(call)
        if len(self.call_log) > 10000:
            self.call_log = self.call_log[-5000:]

    # ─── INFO ──────────────────────────────────────────────────

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "params": t.params_schema,
                "returns": t.returns_schema,
                "requires_auth": t.requires_auth,
                "tags": t.tags,
            }
            for t in self.tools.values()
        ]

    def get_tool(self, name: str) -> ToolDefinition | None:
        return self.tools.get(name)

    def get_call_log(self, limit: int = 50) -> list[dict[str, Any]]:
        return [c.to_dict() for c in self.call_log[-limit:]]

    def get_stats(self) -> dict[str, Any]:
        total = len(self.call_log)
        success = sum(1 for c in self.call_log if c.success)
        return {
            "tools_registered": len(self.tools),
            "total_calls": total,
            "successful_calls": success,
            "failed_calls": total - success,
            "success_rate": success / total if total > 0 else 0.0,
        }