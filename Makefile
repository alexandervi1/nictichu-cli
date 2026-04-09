.PHONY: help install test run clean

help:
	@echo "NictichuCLI - Comandos disponibles:"
	@echo "  make install    - Instalar dependencias"
	@echo "  make test       - Ejecutar tests"
	@echo "  make run        - Ejecutar CLI"
	@echo "  make clean      - Limpiar archivos temporales"

install:
	pip install -e .

test:
	python -m pytest tests/ -v

run:
	python -m src.main interactive

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache
