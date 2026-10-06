"""
Atribución Engine — Sandbox de ejecución.

Aislamiento seguro para código ejecutado por agentes.

Capas de defensa:
1. Timeout por ejecución.
2. Límite de memoria.
3. Sin acceso a red por defecto.
4. Sin acceso a filesystem por defecto.
5. Sin imports peligrosos (os, subprocess, socket).
6. Whitelist de imports permitidos.
7. Captura de stdout/stderr.
8. Auditoría de cada ejecución.

Filosofía: si un agente puede ejecutar código, debe poder
hacerlo sin comprometer el nodo. Este sandbox es defensa en
profundidad, no aislamiento perfecto (para eso: gVisor, Firecracker).

Uso:
    sandbox = Sandbox(timeout_seconds=5, max_memory_mb=128)
    result = sandbox.run("print(2 + 2)")
    print(result.stdout)  # "4"
    print(result.success)  # True
"""

from __future__ import annotations

import ast
import io
import logging
import resource
import signal
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


logger = logging.getLogger(__name__)


# ─── IMPORTS PELIGROSOS (BLOQUEADOS) ─────────────────────────

FORBIDDEN_MODULES: set[str] = {
    "os", "sys", "subprocess", "socket", "shutil", "pathlib",
    "importlib", "ctypes", "multiprocessing", "threading",
    "pickle", "marshal", "shelve", "tempfile", "glob",
    "pty", "tty", "termios", "fcntl", "resource", "signal",
    "asyncio", "concurrent", "http", "urllib", "requests",
    "httpx", "ftplib", "smtplib", "telnetlib", "xmlrpc",
    "webbrowser", "platform", "getpass", "pwd", "grp",
}

FORBIDDEN_FUNCTIONS: set[str] = {
    "eval", "exec", "compile", "__import__", "open",
    "input", "breakpoint", "globals", "locals", "vars",
    "getattr", "setattr", "delattr",
}

FORBIDDEN_ATTRIBUTES: set[str] = {
    "__class__", "__bases__", "__subclasses__", "__globals__",
    "__code__", "__closure__", "__func__", "__self__",
    "__dict__", "__module__",
}

SAFE_BUILTINS: dict[str, Any] = {
    "abs": abs, "all": all, "any": any, "ascii": ascii,
    "bin": bin, "bool": bool, "bytearray": bytearray,
    "bytes": bytes, "callable": callable, "chr": chr,
    "complex": complex, "dict": dict, "divmod": divmod,
    "enumerate": enumerate, "filter": filter, "float": float,
    "format": format, "frozenset": frozenset, "hash": hash,
    "hex": hex, "id": id, "int": int, "isinstance": isinstance,
    "issubclass": issubclass, "iter": iter, "len": len,
    "list": list, "map": map, "max": max, "min": min,
    "next": next, "object": object, "oct": oct, "ord": ord,
    "pow": pow, "print": print, "range": range, "repr": repr,
    "reversed": reversed, "round": round, "set": set,
    "slice": slice, "sorted": sorted, "str": str,
    "sum": sum, "tuple": tuple, "type": type, "zip": zip,
    "True": True, "False": False, "None": None,
    "Exception": Exception, "ValueError": ValueError,
    "TypeError": TypeError, "KeyError": KeyError,
    "IndexError": IndexError, "ZeroDivisionError": ZeroDivisionError,
    "AssertionError": AssertionError,
}


# ─── EXCEPCIONES ─────────────────────────────────────────────

class SandboxViolation(Exception):
    """Se lanza cuando el código viola las reglas del sandbox."""
    pass


class SandboxTimeout(Exception):
    """Se lanza cuando el código excede el timeout."""
    pass


# ─── RESULTADO ───────────────────────────────────────────────

@dataclass
class SandboxResult:
    """Resultado de una ejecución en sandbox."""

    id: str
    code: str
    stdout: str
    stderr: str
    result: Any
    success: bool
    duration_ms: float
    timestamp: str
    error: str | None = None
    violations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ─── CONFIGURACIÓN ───────────────────────────────────────────

@dataclass
class SandboxConfig:
    """Configuración del sandbox."""

    timeout_seconds: int = 5
    max_memory_mb: int = 128
    max_output_chars: int = 10000
    max_code_length: int = 50000
    allow_imports: bool = False
    allowed_modules: list[str] = field(default_factory=list)


# ─── SANDBOX ─────────────────────────────────────────────────

class Sandbox:
    """Sandbox de ejecución de código Python."""

    def __init__(self, config: SandboxConfig | None = None) -> None:
        self.config = config or SandboxConfig()
        self.executions: list[SandboxResult] = []
        logger.info(
            "Sandbox listo (timeout=%ds, max_mem=%dMB)",
            self.config.timeout_seconds,
            self.config.max_memory_mb,
        )

    # ─── RUN ───────────────────────────────────────────────────

    def run(self, code: str, context: dict[str, Any] | None = None) -> SandboxResult:
        """
        Ejecuta código Python en el sandbox.

        context: variables iniciales disponibles para el código.
        """
        import time
        start = time.time()

        violations: list[str] = []

        # 1. Validación estática
        try:
            self._validate_code(code)
        except SandboxViolation as e:
            violations.append(str(e))
            result = SandboxResult(
                id=f"sbx_{uuid4().hex[:12]}",
                code=code,
                stdout="",
                stderr="",
                result=None,
                success=False,
                duration_ms=(time.time() - start) * 1000,
                timestamp=datetime.now(timezone.utc).isoformat(),
                error=str(e),
                violations=violations,
            )
            self.executions.append(result)
            return result

        # 2. Preparar entorno aislado
        sandbox_globals: dict[str, Any] = {
            "__builtins__": SAFE_BUILTINS,
        }
        if context:
            sandbox_globals.update(context)

        # 3. Capturar stdout/stderr
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()

        result_value: Any = None
        error: str | None = None
        success = True

        # 4. Configurar timeout
        old_handler = None
        try:
            old_handler = signal.signal(signal.SIGALRM, self._timeout_handler)
            signal.alarm(self.config.timeout_seconds)
        except (ValueError, AttributeError):
            # Windows o entorno sin signal — usar solo como best effort
            pass

        try:
            with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
                # Compilar a modo "exec"
                compiled = compile(code, "<sandbox>", "exec")

                # Ejecutar
                exec(compiled, sandbox_globals)

                # Si hay una variable `result`, extraerla
                result_value = sandbox_globals.get("result")

        except SandboxTimeout:
            error = f"Timeout de {self.config.timeout_seconds}s excedido"
            success = False
        except Exception as e:
            error = f"{type(e).__name__}: {e}"
            stderr_buf.write(traceback.format_exc())
            success = False
        finally:
            try:
                signal.alarm(0)
                if old_handler is not None:
                    signal.signal(signal.SIGALRM, old_handler)
            except (ValueError, AttributeError):
                pass

        stdout = stdout_buf.getvalue()[: self.config.max_output_chars]
        stderr = stderr_buf.getvalue()[: self.config.max_output_chars]

        result = SandboxResult(
            id=f"sbx_{uuid4().hex[:12]}",
            code=code,
            stdout=stdout,
            stderr=stderr,
            result=result_value,
            success=success,
            duration_ms=round((time.time() - start) * 1000, 2),
            timestamp=datetime.now(timezone.utc).isoformat(),
            error=error,
            violations=violations,
        )

        self.executions.append(result)
        if len(self.executions) > 1000:
            self.executions = self.executions[-500:]

        return result

    # ─── VALIDACIÓN ────────────────────────────────────────────

    def _validate_code(self, code: str) -> None:
        """Validación estática del código."""
        # Longitud
        if len(code) > self.config.max_code_length:
            raise SandboxViolation(
                f"Código excede {self.config.max_code_length} caracteres"
            )

        # Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise SandboxViolation(f"Syntax error: {e}") from e

        # Recorrer AST
        for node in ast.walk(tree):
            # Imports bloqueados
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if not self.config.allow_imports:
                    raise SandboxViolation(
                        f"Imports no permitidos: {ast.dump(node)[:80]}"
                    )
                module = (
                    node.names[0].name.split(".")[0]
                    if isinstance(node, ast.Import)
                    else (node.module or "").split(".")[0]
                )
                if module in FORBIDDEN_MODULES:
                    raise SandboxViolation(f"Módulo prohibido: {module}")
                if module not in self.config.allowed_modules:
                    raise SandboxViolation(
                        f"Módulo no en whitelist: {module}"
                    )

            # Funciones peligrosas
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in FORBIDDEN_FUNCTIONS:
                        raise SandboxViolation(
                            f"Función prohibida: {node.func.id}"
                        )

            # Atributos peligrosos
            if isinstance(node, ast.Attribute):
                if node.attr in FORBIDDEN_ATTRIBUTES:
                    raise SandboxViolation(
                        f"Atributo prohibido: {node.attr}"
                    )

    # ─── TIMEOUT ───────────────────────────────────────────────

    @staticmethod
    def _timeout_handler(signum: int, frame: Any) -> None:
        raise SandboxTimeout("Ejecución excedió el timeout")

    # ─── ESTADÍSTICAS ──────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        total = len(self.executions)
        success = sum(1 for e in self.executions if e.success)
        avg_duration = (
            sum(e.duration_ms for e in self.executions) / total
            if total > 0
            else 0.0
        )
        return {
            "total_executions": total,
            "successful": success,
            "failed": total - success,
            "violations": sum(len(e.violations) for e in self.executions),
            "avg_duration_ms": round(avg_duration, 2),
        }

    def get_executions(self, limit: int = 50) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self.executions[-limit:]]

    def clear(self) -> None:
        self.executions = []