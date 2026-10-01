from lorenzo.models import Maze


class Player():
    def __init__(self, maze: Maze, lives: int):
        self.x: int = maze.player_start[0]
        self.y: int = maze.player_start[1]
        self.maze: Maze = maze
        self.lives: int = lives
        self.direzione: str = ""
        self.points: int = 0

    def move(self) -> None:
        cella_corrente = self.maze.mappa[(self.x, self.y)]
        if self.direzione == 'up' and cella_corrente.opennord:
            self.y -= 1
        elif self.direzione == 'down' and cella_corrente.opensud:
            self.y += 1
        elif self.direzione == 'left' and cella_corrente.openwest:
            self.x -= 1
        elif self.direzione == 'right' and cella_corrente.openeast:
            self.x += 1
        else:
            return
        nuova_cella = self.maze.mappa[(self.x, self.y)]
        if nuova_cella.item is not None:
            self.points += nuova_cella.item.points
            nuova_cella.item = None
            self.maze.total_gums -= 1
