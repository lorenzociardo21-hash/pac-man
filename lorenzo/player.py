from lorenzo.models import Maze


class Player():
    def __init__(self, maze: Maze, lives: int):
        self.x: int = maze.player_start[0]
        self.y: int = maze.player_start[1]
        self.maze: Maze = maze
        self.lives: int = lives
        self.direzione: str = ""
        self.seconda_direzione: str = ""
        self.points: int = 0

    def move(self) -> None:
        cella_corrente = self.maze.mappa[(self.x, self.y)]

        if cella_corrente.item is not None:
            self.points += cella_corrente.item.points
            cella_corrente.item = None
            self.maze.total_gums -= 1

        if self.seconda_direzione != "":
            if self.seconda_direzione == 'up' and cella_corrente.opennord:
                self.direzione = self.seconda_direzione
                self.seconda_direzione = ""
            elif self.seconda_direzione == 'down' and cella_corrente.opensud:
                self.direzione = self.seconda_direzione
                self.seconda_direzione = ""
            elif self.seconda_direzione == 'left' and cella_corrente.openwest:
                self.direzione = self.seconda_direzione
                self.seconda_direzione = ""
            elif self.seconda_direzione == 'right' and cella_corrente.openest:
                self.direzione = self.seconda_direzione
                self.seconda_direzione = ""

        if self.direzione == 'up' and cella_corrente.opennord:
            self.y -= 1
        elif self.direzione == 'down' and cella_corrente.opensud:
            self.y += 1
        elif self.direzione == 'left' and cella_corrente.openwest:
            self.x -= 1
        elif self.direzione == 'right' and cella_corrente.openest:
            self.x += 1
