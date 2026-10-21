"""Persistent top 10 highscore system stored in a JSON file."""

import re
import json
from pydantic import BaseModel, Field, ValidationError


class InputHighscore(BaseModel):
    """A validated highscore entry.

    The name has 1 to 10 characters (letters, digits and spaces
    only) and the score is a non-negative integer.
    """

    name: str = Field(max_length=10, pattern=r"^[A-Za-z0-9 ]+$")
    score: int = Field(ge=0)


class Highscores:
    """Top 10 scores, loaded from and saved to a JSON file."""

    def __init__(self, filename: str) -> None:
        """Load the scores from file.

        Args:
            filename: Path of the JSON highscore file.
        """
        self.filename = filename
        self.inputs: list[InputHighscore] = []
        self.load()

    def load(self) -> None:
        """Load the scores, ignoring a bad file and invalid entries."""

        self.inputs = []
        try:
            with open(self.filename, "r") as f:
                raw = json.load(f)
        except (OSError, ValueError):
            return
        if not isinstance(raw, list):
            return
        for item in raw:
            try:
                """ ** fa unpacking del dict in arg/key e value"""
                self.inputs.append(InputHighscore(**item))
            except (ValidationError, TypeError):
                continue
        self._trim()

    def add(self, name: str, score: int) -> bool:
        """Add a score and save the file.

        The name is cleaned (allowed chars only, max 10, 'Player' if
        empty).

        Args:
            name: Player name.
            score: Final score.

        Returns:
            True if the score was added, False if it is invalid.
        """

        name = re.sub(r"[^A-Za-z0-9 ]", "", name).strip()[:10]
        if not name:
            name = "Player"
        try:
            self.inputs.append(InputHighscore(name=name, score=score))
        except ValidationError:
            return False
        self._trim()
        self.save()
        return True

    def save(self) -> None:
        """Write the scores to file; an error is printed, not raised."""

        try:
            with open(self.filename, "w") as f:
                json.dump([i.model_dump() for i in self.inputs], f)
        except OSError as e:
            print(f"[highscore] non puo salvare: {e}")

    def _trim(self) -> None:
        """Sort by score (highest first) and keep only the top 10."""

        self.inputs.sort(key=lambda i: i.score, reverse=True)
        self.inputs = self.inputs[:10]

    def get_top(self) -> list[tuple[str, int]]:
        """Return the scores as a list of (name, score) tuples."""
        return [(i.name, i.score) for i in self.inputs]
