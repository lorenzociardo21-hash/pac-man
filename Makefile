.PHONY: install run debug clean lint lint-strict

install:
	uv	venv
	uv	pip install flake8 mypy
	uv	pip install mazegenerator-2.1.0-py3-none-any.whl

run:
	uvrun python3 pac-man.py config.json

debug:
	uvrun python3 -m pdb pac-man.py config.json

clean:
	rm	-rf .venv .mypy_cache pycache

lint:
	uv	run flake8 .
	uv	run mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

lint-strict:
	uv	run flake8 .
	uv	run mypy --strict .