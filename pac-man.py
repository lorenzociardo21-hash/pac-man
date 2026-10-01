import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import json  # noqa: E402
import sys  # noqa: E402
from typing import Any  # noqa: E402
from window import Window  # noqa: E402
from highscores import Highscores  # noqa: E402
from pydantic import BaseModel, Field, ValidationError  # noqa: E402


class Config(BaseModel):
    """mOdeLL011 base per config"""
    highscore_filename: str = "highscores.json"
    level: list[int] = list(range(1, 11))
    """min e max sono random, si possono anche non mettere"""
    width: int = Field(50, ge=5, le=200)
    height: int = Field(50, ge=5, le=200)
    """min e max sono random, si possono anche non mettere"""
    lives: int = Field(3, ge=1, le=99)
    pacgum: int = Field(42, ge=1)
    points_per_pacgum: int = Field(10, ge=0)
    points_per_super_pacgum: int = Field(50, ge=0)
    points_per_ghost: int = Field(200, ge=0)
    seed: int = 42
    level_max_time: int = Field(90, ge=1)


def load_config(filename: str) -> Config:
    """Loaddo il file, exit file sbagliato, valori default se key sbagliata"""

    try:
        with open(filename, "r") as f:
            text = "".join(
                line for line in f if not line.lstrip().startswith("#")
            )
        data: Any = json.loads(text)
    except OSError as e:
        print(f"no puedo leggere file: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"giasone invalids: {e}")
        sys.exit(1)
    if not isinstance(data, dict):
        print("config root deve essere giasone")
        sys.exit(1)
    while True:
        try:
            return Config(**data)
        except ValidationError as e:
            for err in e.errors():
                key = str(err["loc"][0])
                print(f"[config] invalid '{key}': {err['msg']}; using default")
                data.pop(key, None)


def main() -> None:
    """python3 pac-man.py config.json da terminale"""

    if len(sys.argv) != 2:
        print(">>> python3 pac-man.py config.json")
        sys.exit(1)
    if not sys.argv[1].endswith(".json"):
        print("File non giasone")
        sys.exit(1)
    config = load_config(sys.argv[1])
    highscores = Highscores(config.highscore_filename)
    # highscores.add("Riso", 100)
    # highscores.add("Patate", 200)
    # highscores.add("Cozze", 300)
    # highscores.add("Peposo", 500)
    # highscores.add("Pane!=Sale", 400)
    # print(config)
    # """Ogni volta che rimandi make run aggiunge al json esistente..."""
    print(highscores.inputs)
    finestra = Window(800, 600, "PACCO-MANNO")
    finestra.avvia()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
