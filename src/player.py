"""Player logic: movement in the maze and eating items."""

from src.models import Maze


class Player():
    """The Pac-Man controlled by the user."""

    def __init__(self, maze: Maze, lives: int):
        """Place the player at the maze start.

        Args:
            maze: The maze the player moves in.
            lives: Initial number of lives.
        """
        self.x: int = maze.player_start[0]
        self.y: int = maze.player_start[1]
        self.maze: Maze = maze
        self.lives: int = lives
        self.direzione: str = ""
        self.seconda_direzione: str = ""
        self.points: int = 0
        self.cheat_player: bool = False

    def move(self) -> None:
        """Eat the item on the current cell, then move by one cell.

        The player turns to the queued direction when that side is open.
        In cheat mode walls are ignored (only the borders stop it).
        """
        cella_corrente = self.maze.mappa[(self.x, self.y)]

        if cella_corrente.item is not None:
            self.points += cella_corrente.item.points
            cella_corrente.item = None
            self.maze.total_gums -= 1

        if not self.cheat_player:
            aperte: dict[str, bool] = {
                "up": cella_corrente.opennord,
                "down": cella_corrente.opensud,
                "left": cella_corrente.openwest,
                "right": cella_corrente.openest,
            }
            if (self.seconda_direzione != ""
                    and aperte[self.seconda_direzione]):
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

        else:
            if self.seconda_direzione != "":
                self.direzione = self.seconda_direzione
                self.seconda_direzione = ""

            if self.direzione == 'up' and self.y > 0:
                self.y -= 1
            elif self.direzione == 'down' and self.y < self.maze.max_y:
                self.y += 1
            elif self.direzione == 'left' and self.x > 0:
                self.x -= 1
            elif self.direzione == 'right' and self.x < self.maze.max_x:
                self.x += 1
