from src.models import Maze
from src.player import Player
import random
from math import sqrt


class Ghost():

    contatore_fantasmi: int = 0

    def __init__(self, maze: Maze,
                 start_position: tuple[int, int],
                 player: Player):
        self.x: int = start_position[0]
        self.y: int = start_position[1]
        self.start_x: int = start_position[0]
        self.start_y: int = start_position[1]
        self.id: int = Ghost.contatore_fantasmi
        self.direzione: str = ""
        self.maze: Maze = maze
        Ghost.contatore_fantasmi += 1
        if Ghost.contatore_fantasmi > 3:
            Ghost.contatore_fantasmi = 0
        self.player: Player = player
        self.passi: int = 0
        self.stupid: bool = False
        self.stupid_time: int = 30
        self.dead: bool = False
        self.home_timer: int = 10

    def _muovi(self, direzione: str) -> None:
        cella = self.maze.mappa[(self.x, self.y)]
        if direzione not in cella.what_dir_is_walkable():
            return
        if direzione == 'up':
            self.y -= 1
        elif direzione == 'down':
            self.y += 1
        elif direzione == 'left':
            self.x -= 1
        elif direzione == 'right':
            self.x += 1

    def get_bfs_direction(self, target_x: int, target_y: int) -> str:
        if self.x == target_x and self.y == target_y:
            return ""
        cella_corrente = self.maze.mappa[(self.x, self.y)]
        direzioni_iniziali: list[str] = cella_corrente.what_dir_is_walkable()
        dict_dir_contrario: dict[str, str] = {
            "up": "down", "down": "up", "right": "left", "left": "right",
            "": ""
        }
        dir_contro: str = dict_dir_contrario[self.direzione]
        if dir_contro in direzioni_iniziali and len(direzioni_iniziali) > 1:
            direzioni_iniziali.remove(dir_contro)

        coda: list[tuple[int, int, str]] = []
        visitati: set[tuple[int, int]] = set()
        visitati.add((self.x, self.y))
        for d in direzioni_iniziali:
            nx, ny = self.x, self.y
            if d == 'up':
                ny -= 1
            elif d == 'down':
                ny += 1
            elif d == 'left':
                nx -= 1
            elif d == 'right':
                nx += 1

            if nx == target_x and ny == target_y:
                return d

            coda.append((nx, ny, d))
            visitati.add((nx, ny))
        direzione_scelta: str = ""
        while coda:
            cx, cy, mossa_iniziale = coda.pop(0)
            if cx == target_x and cy == target_y:
                direzione_scelta = mossa_iniziale
                break
            cella_espansione = self.maze.mappa[(cx, cy)]
            dir_espansione = cella_espansione.what_dir_is_walkable()
            for d in dir_espansione:
                nx, ny = cx, cy
                if d == 'up':
                    ny -= 1
                elif d == 'down':
                    ny += 1
                elif d == 'left':
                    nx -= 1
                elif d == 'right':
                    nx += 1

                if (nx, ny) not in visitati:
                    visitati.add((nx, ny))
                    coda.append((nx, ny, mossa_iniziale))
        if direzione_scelta == "":
            if direzioni_iniziali:
                return random.choice(direzioni_iniziali)
            return ""
        return direzione_scelta

    def move_id0(self) -> None:
        cella_corrente = self.maze.mappa[(self.x, self.y)]
        list_direzioni: list[str] = cella_corrente.what_dir_is_walkable()
        dict_dir_contrario: dict[str, str] = {
            "up": "down", "down": "up", "right": "left", "left": "right",
            "": ""
        }
        dir_contro: str = dict_dir_contrario[self.direzione]
        if dir_contro in list_direzioni and len(list_direzioni) > 1:
            list_direzioni.remove(dir_contro)

        self.direzione = random.choice(list_direzioni)
        self._muovi(self.direzione)

    def move_id1(self) -> None:
        cella_corrente = self.maze.mappa[(self.x, self.y)]
        list_direzioni: list[str] = cella_corrente.what_dir_is_walkable()
        dict_dir_contrario: dict[str, str] = {
            "up": "down", "down": "up", "right": "left", "left": "right",
            "": ""
        }
        dir_contro: str = dict_dir_contrario[self.direzione]
        if dir_contro in list_direzioni and len(list_direzioni) > 1:
            list_direzioni.remove(dir_contro)
        dir_piu_corta: list[tuple[tuple[int, int], str, float]] = []
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
            dir_piu_corta.append(((x, y), direzione, distanz))
        scelta_migliore = min(dir_piu_corta, key=lambda elemento: elemento[2])
        self.x, self.y = scelta_migliore[0]
        self.direzione = scelta_migliore[1]

    def move_id2(self) -> None:
        self.passi += 1
        if self.passi % 30 < 20:
            self.direzione = self.get_bfs_direction(self.player.x,
                                                    self.player.y)
            self._muovi(self.direzione)
        else:
            self.move_id0()

    def move_id3(self) -> None:
        distanza: float = sqrt((self.player.x - self.x)**2 +
                               (self.player.y - self.y)**2)
        if distanza > 8:
            self.move_id2()
        else:
            self.move_id0()

    def torniamo_a_casa(self) -> None:
        if self.x != self.start_x or self.y != self.start_y:
            self.direzione = self.get_bfs_direction(self.start_x, self.start_y)
            self._muovi(self.direzione)
        else:
            if self.home_timer > 0:
                self.home_timer -= 1
            else:
                self.dead = False
                self.stupid = False
                self.home_timer = 10

    def move(self) -> None:
        if self.dead:
            self.torniamo_a_casa()
            return
        if not self.stupid:
            if self.player.direzione != "":
                if self.id == 0:
                    self.move_id0()
                elif self.id == 1:
                    self.move_id1()
                elif self.id == 2:
                    self.move_id2()
                elif self.id == 3:
                    self.move_id3()
        else:
            if self.stupid_time > 0:
                if self.id == 0:
                    self.move_id0()
                elif self.id == 1:
                    self.move_id0()
                elif self.id == 2:
                    self.move_id0()
                elif self.id == 3:
                    self.move_id0()
            self.stupid_time -= 1
            if self.stupid_time <= 0:
                self.stupid = False
