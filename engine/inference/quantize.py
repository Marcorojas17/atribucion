"""
Atribución Engine — Cuantización de modelos.

Reduce el tamaño y requisitos de memoria de un modelo LLM.

Tipos de cuantización:
    4-bit  → 25% del tamaño original, calidad aceptable
    5-bit  → 31% del tamaño, mejor calidad
    8-bit  → 50% del tamaño, casi sin pérdida
    Q4_K_M → 4-bit mixto (recomendado para uso general)
    Q5_K_M → 5-bit mixto (mejor calidad)

Ejemplo: Llama 3 8B
    FP16:  ~16 GB
    Q8_0:  ~8 GB
    Q5_K_M: ~5.5 GB
    Q4_K_M: ~4.5 GB
    Q4_0:  ~4 GB

Uso:
    quantizer = ModelQuantizer()
    quantizer.quantize("model.gguf", "model-q4.gguf", quant_type="Q4_K_M")
"""

from __future__ import annotations

import logging
import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)


class QuantType(str, Enum):
    """Tipos de cuantización."""

    Q2_K = "Q2_K"
    Q3_K_S = "Q3_K_S"
    Q3_K_M = "Q3_K_M"
    Q3_K_L = "Q3_K_L"
    Q4_0 = "Q4_0"
    Q4_1 = "Q4_1"
    Q4_K_S = "Q4_K_S"
    Q4_K_M = "Q4_K_M"
    Q5_0 = "Q5_0"
    Q5_1 = "Q5_1"
    Q5_K_S = "Q5_K_S"
    Q5_K_M = "Q5_K_M"
    Q6_K = "Q6_K"
    Q8_0 = "Q8_0"
    F16 = "F16"
    F32 = "F32"


@dataclass
class QuantResult:
    """Resultado de una cuantización."""

    input_path: str
    output_path: str
    quant_type: str
    input_size_mb: float
    output_size_mb: float
    compression_ratio: float
    duration_seconds: float
    success: bool
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_path": self.input_path,
            "output_path": self.output_path,
            "quant_type": self.quant_type,
            "input_size_mb": round(self.input_size_mb, 2),
            "output_size_mb": round(self.output_size_mb, 2),
            "compression_ratio": round(self.compression_ratio, 2),
            "duration_seconds": round(self.duration_seconds, 2),
            "success": self.success,
            "error": self.error,
        }


class ModelQuantizer:
    """Cuantizador de modelos GGUF."""

    # Tamaños aproximados por parámetro (MB)
    SIZE_MB_PER_B_PARAM: dict[str, float] = {
        "F32": 4000.0,
        "F16": 2000.0,
        "Q8_0": 1000.0,
        "Q6_K": 825.0,
        "Q5_K_M": 685.0,
        "Q5_K_S": 662.0,
        "Q5_1": 644.0,
        "Q5_0": 611.0,
        "Q4_K_M": 590.0,
        "Q4_K_S": 571.0,
        "Q4_1": 548.0,
        "Q4_0": 528.0,
        "Q3_K_L": 465.0,
        "Q3_K_M": 442.0,
        "Q3_K_S": 408.0,
        "Q2_K": 350.0,
    }

    def __init__(self, llama_cpp_path: str | None = None) -> None:
        """
        Inicializa el cuantizador.

        llama_cpp_path: ruta al binario `quantize` de llama.cpp.
        Si no se especifica, busca en PATH.
        """
        self.llama_cpp_path = llama_cpp_path or self._find_quantize_binary()

    def _find_quantize_binary(self) -> str | None:
        """Busca el binario `quantize` de llama.cpp."""
        candidates = [
            "quantize",
            "llama-quantize",
            "/usr/local/bin/llama-quantize",
            "/usr/bin/llama-quantize",
            str(Path.home() / "llama.cpp" / "build" / "bin" / "llama-quantize"),
        ]
        for c in candidates:
            try:
                if Path(c).exists() or self._which(c):
                    return c
            except Exception:
                continue
        return None

    @staticmethod
    def _which(name: str) -> str | None:
        """Equivalente a `which name`."""
        for path_dir in os.environ.get("PATH", "").split(os.pathsep):
            full = Path(path_dir) / name
            if full.exists() and os.access(full, os.X_OK):
                return str(full)
        return None

    # ─── QUANTIZE ──────────────────────────────────────────────

    def quantize(
        self,
        input_path: str,
        output_path: str,
        quant_type: QuantType = QuantType.Q4_K_M,
        n_threads: int | None = None,
    ) -> QuantResult:
        """
        Cuantiza un modelo GGUF.

        Requiere el binario `quantize` de llama.cpp instalado.
        """
        import time

        start = time.time()

        input_path_obj = Path(os.path.expanduser(input_path))
        output_path_obj = Path(os.path.expanduser(output_path))

        if not input_path_obj.exists():
            return QuantResult(
                input_path=str(input_path_obj),
                output_path=str(output_path_obj),
                quant_type=quant_type.value,
                input_size_mb=0,
                output_size_mb=0,
                compression_ratio=0,
                duration_seconds=0,
                success=False,
                error=f"Archivo no existe: {input_path_obj}",
            )

        input_size_mb = input_path_obj.stat().st_size / (1024 * 1024)

        if not self.llama_cpp_path:
            # No podemos cuantizar sin el binario
            # Pero podemos devolver la estimación
            return QuantResult(
                input_path=str(input_path_obj),
                output_path=str(output_path_obj),
                quant_type=quant_type.value,
                input_size_mb=input_size_mb,
                output_size_mb=input_size_mb,  # sin cambio
                compression_ratio=1.0,
                duration_seconds=time.time() - start,
                success=False,
                error=(
                    "Binario `quantize` de llama.cpp no encontrado. "
                    "Instala llama.cpp o especifica llama_cpp_path."
                ),
            )

        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.llama_cpp_path,
            str(input_path_obj),
            str(output_path_obj),
            quant_type.value,
        ]
        if n_threads:
            cmd.extend(["--threads", str(n_threads)])

        try:
            logger.info(
                "Cuantizando %s → %s (%s)",
                input_path_obj.name, output_path_obj.name, quant_type.value,
            )
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600,
                check=False,
            )

            if result.returncode != 0:
                return QuantResult(
                    input_path=str(input_path_obj),
                    output_path=str(output_path_obj),
                    quant_type=quant_type.value,
                    input_size_mb=input_size_mb,
                    output_size_mb=0,
                    compression_ratio=0,
                    duration_seconds=time.time() - start,
                    success=False,
                    error=result.stderr[:500],
                )

            output_size_mb = output_path_obj.stat().st_size / (1024 * 1024)

            return QuantResult(
                input_path=str(input_path_obj),
                output_path=str(output_path_obj),
                quant_type=quant_type.value,
                input_size_mb=input_size_mb,
                output_size_mb=output_size_mb,
                compression_ratio=input_size_mb / output_size_mb,
                duration_seconds=time.time() - start,
                success=True,
            )

        except subprocess.TimeoutExpired:
            return QuantResult(
                input_path=str(input_path_obj),
                output_path=str(output_path_obj),
                quant_type=quant_type.value,
                input_size_mb=input_size_mb,
                output_size_mb=0,
                compression_ratio=0,
                duration_seconds=time.time() - start,
                success=False,
                error="Timeout (60 min)",
            )

    # ─── ESTIMATE ──────────────────────────────────────────────

    def estimate_size(
        self,
        model_params_b: float,
        quant_type: QuantType,
    ) -> float:
        """
        Estima el tamaño en MB de un modelo cuantizado.

        model_params_b: tamaño en miles de millones de parámetros.
        Ejemplo: Llama 3 8B → 8.0
        """
        mb_per_b = self.SIZE_MB_PER_B_PARAM.get(quant_type.value)
        if mb_per_b is None:
            return 0.0
        return model_params_b * mb_per_b

    def recommend_quant(
        self,
        model_params_b: float,
        available_ram_gb: float,
        min_quality: str = "balanced",
    ) -> QuantType:
        """
        Recomienda el mejor tipo de cuantización según RAM.

        min_quality: "fast" | "balanced" | "quality"
        """
        available_mb = available_ram_gb * 1024 * 0.7  # dejar 30% libre

        if min_quality == "fast":
            preferred = [
                QuantType.Q2_K,
                QuantType.Q3_K_M,
                QuantType.Q4_K_M,
                QuantType.Q5_K_M,
                QuantType.Q8_0,
            ]
        elif min_quality == "quality":
            preferred = [
                QuantType.Q8_0,
                QuantType.Q6_K,
                QuantType.Q5_K_M,
                QuantType.Q4_K_M,
                QuantType.Q3_K_M,
            ]
        else:  # balanced
            preferred = [
                QuantType.Q5_K_M,
                QuantType.Q4_K_M,
                QuantType.Q5_K_S,
                QuantType.Q4_K_S,
                QuantType.Q3_K_M,
                QuantType.Q2_K,
            ]

        for qt in preferred:
            if self.estimate_size(model_params_b, qt) <= available_mb:
                return qt

        return QuantType.Q2_K  # último recurso

    # ─── INFO ──────────────────────────────────────────────────

    def list_quant_types(self) -> list[dict[str, Any]]:
        """Lista todos los tipos de cuantización disponibles."""
        return [
            {
                "type": qt.value,
                "size_mb_per_b_param": self.SIZE_MB_PER_B_PARAM.get(qt.value, 0),
            }
            for qt in QuantType
        ]

    def get_info(self) -> dict[str, Any]:
        return {
            "llama_cpp_available": self.llama_cpp_path is not None,
            "llama_cpp_path": self.llama_cpp_path,
            "quant_types_count": len(QuantType),
        }