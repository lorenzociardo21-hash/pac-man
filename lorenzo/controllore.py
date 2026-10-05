from lorenzo.models import Maze, Bubblegum
from lorenzo.ghost import Ghost
from lorenzo.player import Player
import pygame


class Controll():
    def __init__(self, maze: Maze, ghosts: list[Ghost], player: Player):
        self.maze: Maze = maze
        self.ghosts: list[Ghost] = ghosts
        self.player: Player = player
        self.show_must_go_on: bool = True
        self.you_win: bool = False

    def bublegummiamo(self) -> None:
        cord_player: tuple[int, int] = (self.player.x, self.player.y)
        if isinstance(self.maze.mappa[cord_player].item, Bubblegum):
            for ghost in self.ghosts:
                if not ghost.dead:
                    ghost.stupid = True
                    ghost.stupid_time = 30

    def controlliamo(self) -> None:
        self.bublegummiamo()    
        flag: bool = False
        for ghost in self.ghosts:
            if ghost.dead:
                continue
            if (ghost.x, ghost.y) == (self.player.x, self.player.y):
                if not ghost.stupid:
                    self.player.lives -= 1
                    flag = True
                    self.player.direzione = ""
                    break
                else:
                    ghost.dead = True
                    ghost.stupid = False
                    self.player.points += 200

        if flag:
            pygame.time.wait(1000)
            if self.player.lives == 0:
                self.show_must_go_on = False
                return
            self.player.x = self.maze.player_start[0]
            self.player.y = self.maze.player_start[1]
            for i, ghost in enumerate(self.ghosts):
                ghost.x = self.maze.ghost_spawns[i][0]
                ghost.y = self.maze.ghost_spawns[i][1]
                ghost.direzione = ""
                ghost.dead = False
                ghost.stupid = False
            return

        if self.maze.total_gums == 0:
            self.you_win = True
