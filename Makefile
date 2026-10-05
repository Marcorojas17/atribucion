# ─────────────────────────────────────────────────────────────
# ATRIBUCIÓN — Atajos de desarrollo
# ─────────────────────────────────────────────────────────────

.PHONY: help install dev test lint format clean build docker docker-down docker-logs deploy

# Colores
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
BLUE   := $(shell tput -Txterm setaf 4)
RESET  := $(shell tput -Txterm sgr0)

help: ## Muestra esta ayuda
	@echo ''
	@echo '${BLUE}Atribución — Comandos disponibles:${RESET}'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  ${GREEN}%-18s${RESET} %s\n", $$1, $$2}'
	@echo ''

# ─────────────────────────────────────────────────────────────
# INSTALACIÓN
# ─────────────────────────────────────────────────────────────

install: ## Instala dependencias en .venv
	@echo "${BLUE}→ Creando entorno virtual...${RESET}"
	python3 -m venv .venv
	@echo "${BLUE}→ Instalando dependencias...${RESET}"
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "${GREEN}✓ Listo${RESET}"

# ─────────────────────────────────────────────────────────────
# DESARROLLO
# ─────────────────────────────────────────────────────────────

dev: ## Arranca el servidor en modo desarrollo
	.venv/bin/uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

test: ## Corre todos los tests
	.venv/bin/pytest tests/ -v --tb=short

test-cov: ## Tests con cobertura
	.venv/bin/pytest tests/ -v --cov=core --cov=api --cov-report=html

lint: ## Corre ruff
	.venv/bin/ruff check core/src api tests

format: ## Formatea con ruff
	.venv/bin/ruff format core/src api tests

# ─────────────────────────────────────────────────────────────
# BUILD
# ─────────────────────────────────────────────────────────────

build: ## Construye el paquete Python
	.venv/bin/pip install build
	.venv/bin/python -m build

clean: ## Limpia artefactos
	@echo "${YELLOW}→ Limpiando...${RESET}"
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "${GREEN}✓ Limpio${RESET}"

# ─────────────────────────────────────────────────────────────
# DOCKER
# ─────────────────────────────────────────────────────────────

docker: ## Levanta el stack completo
	docker-compose up --build -d
	@echo "${GREEN}✓ Stack levantado${RESET}"
	@echo "  API:     http://localhost:8000"
	@echo "  Docs:    http://localhost:8000/docs"
	@echo "  Portal:  http://localhost:8080"

docker-down: ## Baja el stack
	docker-compose down

docker-logs: ## Logs del stack
	docker-compose logs -f

# ─────────────────────────────────────────────────────────────
# DEPLOY
# ─────────────────────────────────────────────────────────────

deploy: ## Deploy a Railway (requiere CLI)
	railway up

# ─────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────

check: lint test ## Lint + tests (pre-commit)
	@echo "${GREEN}✓ Todo OK${RESET}"

.DEFAULT_GOAL := help