from lorenzo.models import Maze
from lorenzo.player import Player
import random
from math import sqrt


class Ghost():

    contatore_fantasmi: int = 0

    def __init__(self, maze: Maze,
                 start_position: tuple[int, int],
                 player: Player):
        self.x: int = start_position[0]
        self.y: int = start_position[1]
        self.id: int = Ghost.contatore_fantasmi
        self.direzione: str = ""
        self.maze: Maze = maze
        Ghost.contatore_fantasmi += 1
        self.player: Player = player

    def move_id0(self) -> None:
        cella_corrente = self.maze.mappa[(self.x, self.y)]
        list_direzioni: list[str] = cella_corrente.what_dir_is_walkable()
        dict_dir_contrario: dict[str, str] = {
            "up": "down",
            "down": "up",
            "right": "left",
            "left": "right",
            "": "",
        }
        dir_contro: str = dict_dir_contrario[self.direzione]
        if dir_contro in list_direzioni and len(list_direzioni) > 1:
            list_direzioni.remove(dir_contro)
        self.direzione = random.choice(list_direzioni)
        if self.direzione == 'up':
            self.y -= 1
        elif self.direzione == 'down':
            self.y += 1
        elif self.direzione == 'left':
            self.x -= 1
        elif self.direzione == 'right':
            self.x += 1

    def move_id1(self) -> None:
        cella_corrente = self.maze.mappa[(self.x, self.y)]
        list_direzioni: list[str] = cella_corrente.what_dir_is_walkable()
        dir_piu_corta: list[tuple[tuple[int, int], int]] = []
        for direzione in list_direzioni:
            x: int = self.x
            y: int = self.y
            if direzione == 'up':
                y -= 1
            elif direzione == 'down':
                y += 1
            elif direzione == 'left':
                x -= 1
            elif direzione == 'right':
                x += 1
            distanz: float = sqrt((self.player.x-x)**2+(self.player.y-y)**2)
            dir_piu_corta.append(((x, y), distanz))
        coordinate_minime = min(dir_piu_corta,
                                key=lambda elemento: elemento[1])[0]

        self.x, self.y = coordinate_minime

    def move(self) -> None:
        if self.id == 0:
            self.move_id1()
        elif self.id == 1:
            self.move_id1()
        if self.id == 2:
            self.move_id1()
        elif self.id == 3:
            self.move_id1()
