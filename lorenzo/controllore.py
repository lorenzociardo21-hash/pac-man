from lorenzo.models import Maze, Bubblegum
from lorenzo.ghost import Ghost
from lorenzo.player import Player


class Controll():
    def __init__(self, maze: Maze, ghosts: list[Ghost], player: Player):
        self.maze: Maze = maze
        self.ghosts: list[Ghost] = ghosts
        self.player: Player = player
        self.show_must_go_on: bool = True
        self.you_win: bool = False
        self.hit: bool = False

    def bublegummiamo(self) -> None:
        cord_player: tuple[int, int] = (self.player.x, self.player.y)
        if isinstance(self.maze.mappa[cord_player].item, Bubblegum):
            for ghost in self.ghosts:
                if not ghost.dead:
                    ghost.stupid = True
                    ghost.stupid_time = 30

    def controlliamo(self, pos_player: tuple[float, float],
                     pos_ghosts: list[tuple[float, float]]) -> None:
        self.bublegummiamo()
        for ghost, (gx, gy) in zip(self.ghosts, pos_ghosts):
            if ghost.dead:
                continue
            dist2 = (pos_player[0] - gx) ** 2 + (pos_player[1] - gy) ** 2
            if dist2 < 0.5 ** 2:
                if not ghost.stupid:
                    self.player.lives -= 1
                    self.player.direzione = ""
                    self.hit = True
                    return
                ghost.dead = True
                ghost.stupid = False
                self.player.points += 200

        if self.maze.total_gums == 0:
            self.you_win = True

    def riparti(self) -> None:
        self.hit = False
        if self.player.lives == 0:
            self.show_must_go_on = False
            return
        self.player.x, self.player.y = self.maze.player_start
        for i, ghost in enumerate(self.ghosts):
            ghost.x, ghost.y = self.maze.ghost_spawns[i]
            ghost.direzione = ""
            ghost.dead = False
            ghost.stupid = False
