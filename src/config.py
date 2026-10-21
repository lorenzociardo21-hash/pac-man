"""Game configuration: model, defaults and JSON loading."""

import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import json  # noqa: E402
import sys  # noqa: E402
from typing import Any  # noqa: E402
from pydantic import BaseModel, Field, ValidationError  # noqa: E402


class Config(BaseModel):
    """Game parameters with their defaults and limits."""
    highscore_filename: str = "highscores.json"
    """min e max sono random, si possono anche non mettere"""
    width: int = Field(14, ge=5, le=200)
    height: int = Field(14, ge=5, le=200)
    """min e max sono random, si possono anche non mettere"""
    lives: int = Field(3, ge=1, le=99)
    pacgum: int = Field(42, ge=1)
    points_per_pacgum: int = Field(10, ge=0)
    points_per_super_pacgum: int = Field(50, ge=0)
    points_per_ghost: int = Field(200, ge=0)
    seed: int = 42
    level_max_time: int = Field(90, ge=1)


def load_config(filename: str) -> Config:
    """Load the JSON config file (lines starting with # are comments).

    The program exits with a message if the file cannot be read or
    is not a JSON object. Invalid values are dropped and replaced
    by their defaults.

    Args:
        filename: Path of the config file.

    Returns:
        The validated Config.
    """

    try:
        with open(filename, "r", encoding="utf-8") as f:
            text = "".join(
                line for line in f if not line.lstrip().startswith("#")
            )
        data: Any = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"giasone invalids: {e}")
        sys.exit(1)
    except (OSError, ValueError) as e:
        print(f"no puedo leggere file: {e}")
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
