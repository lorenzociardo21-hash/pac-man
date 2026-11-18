.PHONY: install run debug clean fclear lint lint-strict package itch-push

# itch.io target "user/game", e.g.: make itch-push ITCH_TARGET=myuser/pac-man
ITCH_TARGET ?=

install:
	uv sync

run:
	uv run python3 pac-man.py config.json

debug:
	uv run python3 -m pdb pac-man.py config.json

clean:
	rm -rf .venv .mypy_cache __pycache__ build dist

fclear: clean
	rm -f uv.lock

lint:
	uv run flake8 pac-man.py src/
	uv run mypy pac-man.py src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 pac-man.py src/
	uv run mypy pac-man.py src/ --strict

# Build the standalone game (for the OS you are running on) in dist/pac-man/
# and a zip of it in dist/pac-man-linux.zip
package:
	uv run --with pyinstaller pyinstaller --noconfirm --clean pac-man.spec
	cp config.json dist/pac-man/config.json
	cp packaging/README.txt dist/pac-man/README.txt
	uv run python3 -c "import shutil; shutil.make_archive('dist/pac-man-linux', 'zip', 'dist', 'pac-man')"
	@echo "Package ready: dist/pac-man/  and  dist/pac-man-linux.zip"

# Upload dist/pac-man/ to itch.io on the "linux" channel (needs butler)
itch-push:
	@test -n "$(ITCH_TARGET)" || (echo "Usage: make itch-push ITCH_TARGET=user/game" && exit 1)
	butler push dist/pac-man $(ITCH_TARGET):linux
