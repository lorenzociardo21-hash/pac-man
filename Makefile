.PHONY: install run debug clean lint lint-strict

install:
	uv venv
	uv pip install pydantic pygame flake8 mypy
	uv pip install mazegenerator-2.1.0-py3-none-any.whl

run:
	uv run python3 andrea/pac-man.py andrea/config.json

debug:
	uv run python3 -m pdb pac-man.py config.json

clean:
	rm -rf .venv .mypy_cache __pycache__

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict
