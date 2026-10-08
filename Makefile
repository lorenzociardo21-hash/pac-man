.PHONY: install run debug clean fclear lint lint-strict

install:
	uv sync

run:
	uv run python3 pac-man.py config.json

debug:
	uv run python3 -m pdb pac-man.py config.json

clean:
	rm -rf .venv .mypy_cache __pycache__

fclear: clean
	rm -f uv.lock

lint:
	uv run flake8 pac-man.py src/
	uv run mypy pac-man.py src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 pac-man.py src/
	uv run mypy pac-man.py src/ --strict
