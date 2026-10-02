from lorenzo.models import Maze
from lorenzo.ghost import Ghost
from lorenzo.player import Player


class Controll():
    def __init__(self, maze: Maze, ghosts: list[Ghost], player: Player):
        self.maze: Maze = maze
        self.ghosts: list[Ghost] = ghosts
        self.player: Player = player
        self.show_must_go_on: bool = True
        self.you_win: bool = False

    def controlliamo(self) -> None:
        flag: bool = False
        for ghost in self.ghosts:
            if (ghost.x, ghost.y) == (self.player.x, self.player.y):
                self.player.lives -= 1
                flag = True
                self.player.direzione = ""
                break
        if flag:
            if self.player.lives == 0:
                self.show_must_go_on = False
                return
            self.player.x = self.maze.player_start[0]
            self.player.y = self.maze.player_start[1]
            for i, ghost in enumerate(self.ghosts):
                ghost.x = self.maze.ghost_spawns[i][0]
                ghost.y = self.maze.ghost_spawns[i][1]
                ghost.direzione = ""
            return
        if self.maze.total_gums == 0:
            self.you_win = True
