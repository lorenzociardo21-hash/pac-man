import re
import json
from pydantic import BaseModel, Field, ValidationError


class InputHighscore(BaseModel):
    """Dati highscore su una riga:
    in r"^[A-Za-z0-9 ]+$", r sta per raw string cioe se scrivo \n
    non va a capo ma scrive proprio 'barra incovercio'+'n'.
    "^[A-Za-z0-9 ]+$" questo invece vuol dire: dall'inizio alla
    fine, solo lettere, numeri e spazi, almeno un carattere e max 10.
    crazy la tecnologia eh?
    tung tung sahur"""

    name: str = Field(max_length=10, pattern=r"^[A-Za-z0-9 ]+$")
    score: int = Field(ge=0)


class Highscores:
    """Top 10 punteggi, inseriti nel json"""

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.inputs: list[InputHighscore] = []
        self.load()

    def load(self) -> None:
        """Loadda punteggi, skippa file non buoni"""

        try:
            with open(self.filename, "r") as f:
                raw = json.load(f)
        except (OSError, json.JSONDecodeError):
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
        """Aggiungo punteggio agli highscore, se invalido > False
        re.sub sostituisce caratteri non autorizzanti con il nulla cosmico"""

        name = re.sub(r"[^A-Za-z0-9 ]", "", name).strip()[:10]
        try:
            self.inputs.append(InputHighscore(name=name, score=score))
        except ValidationError:
            return False
        self._trim()
        self.save()
        return True

    def save(self) -> None:
        """salvo punteggi, evito i crashez"""

        try:
            with open(self.filename, "w") as f:
                json.dump([i.model_dump() for i in self.inputs], f)
        except OSError as e:
            print(f"[highscore] non puo salvare: {e}")

    def _trim(self) -> None:
        """Fa il ranking e tiene solo i primi 10"""

        self.inputs.sort(key=lambda i: i.score, reverse=True)
        self.inputs = self.inputs[:10]
