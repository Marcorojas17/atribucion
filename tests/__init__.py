"""Suite de tests de Atribución."""

import sys
from pathlib import Path

# Añadir core/src al path para importar el core
CORE_SRC = Path(__file__).resolve().parents[1] / "core" / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))