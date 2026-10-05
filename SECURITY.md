
```markdown
# Contribuir a Atribución

Gracias por tu interés. Este proyecto sigue reglas estrictas
para mantener calidad y coherencia.

---

## Antes de empezar

1. Lee `README.md` para entender el proyecto.
2. Lee `AGENTS.md` si eres una IA.
3. Abre un issue antes de hacer cambios grandes.

---

## Setup local

```bash
# Clonar
git clone https://github.com/Marcorojas17/atribucion.git
cd atribucion

# Crear entorno
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar .env
cp .env.example .env
# Editar .env con tus valores

# Ejecutar tests
pytest tests/ -v

# Levantar API
uvicorn api.main:app --reload
```

---

Flujo de contribución

1. Fork del repo.
2. Crear rama: git checkout -b feat/mi-feature.
3. Hacer cambios.
4. Ejecutar tests: pytest tests/ -v.
5. Ejecutar linter: ruff check ..
6. Commit con formato: feat: 🎯 descripción.
7. Push a tu fork.
8. Abrir PR contra develop.

---

Formato de commits

Usamos Conventional Commits con emoji.

Tipos

Emoji Tipo Cuándo
🚀 feat: Nueva funcionalidad
🐛 fix: Corrección de bug
📚 docs: Documentación
🎨 style: Formato, sin lógica
♻️ refactor: Reorganización
🧪 test: Tests
🔧 chore: Configuración
⚡ perf: Rendimiento
🔒 security: Seguridad
🗑️ chore: Eliminación

Ejemplos

```text
feat: 🚀 añadir endpoint de reportes
fix: 🐛 corregir validación de DID
docs: 📚 actualizar quickstart
test: 🧪 añadir test de handoff
chore: 🔧 actualizar dependencias
```

---

Estándares de código

Python

· Python 3.11+
· Type hints obligatorios
· Docstrings en todas las funciones públicas
· Ruff para linting
· Pytest para tests

JavaScript/TypeScript

· TypeScript strict mode
· ES2022+
· Vitest para tests

General

· Sin emojis en código (excepto en strings de UI).
· Sin print(), usar logging.
· Sin secretos en código (usar .env).
· Sin dependencias innecesarias.

---

Arquitectura

Antes de añadir archivos, consulta la estructura canónica
en AGENTS.md. No dupliques conceptos. No crees archivos
sueltos en la raíz.

---

Tests

Todo PR debe incluir tests para la funcionalidad nueva.

```bash
# Correr todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=core --cov=api --cov-report=html
```

---

Code review

Los PRs requieren:

· 1 approval (develop) o 2 approvals (main).
· CI verde.
· Sin conflictos.
· Sin TODO sin issue asociado.

---

Conducta

Este proyecto sigue un código de conducta simple:

· Sé profesional.
· Crítica el código, no a la persona.
· No spam.
· No autopromoción sin contexto.
· Respeta el trabajo de otros.

Violaciones resultan en bloqueo inmediato.

---

Preguntas

· Issues: GitHub Issues
· Email: hola@atribucion.io

---

Marco Antonio Rojas Valdovinos