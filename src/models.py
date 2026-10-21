"""Maze data model: items, cells and the maze built from the grid."""


class Gum:
    """Normal pacgum (small dot)."""

    def __init__(self, points: int) -> None:
        """Create a pacgum.

        Args:
            points: Score given when eaten.
        """
        self.points: int = points
        self.is_super: bool = False


class Bubblegum:
    """Super-pacgum (power pellet) that makes ghosts edible."""

    def __init__(self, points: int) -> None:
        """Create a super-pacgum.

        Args:
            points: Score given when eaten.
        """
        self.points: int = points
        self.is_super: bool = True


class Cell:
    """One maze cell: its open sides and the item it holds."""

    def __init__(self, cell_value: int,
                 item: Gum | Bubblegum | None = None) -> None:
        """Decode the walls of the cell.

        Args:
            cell_value: Wall bits (1=north, 2=east, 4=south, 8=west).
            item: Item placed on the cell, if any.
        """
        self.item = item
        (
            self.opennord,
            self.openest,
            self.opensud,
            self.openwest
        ) = self._get_open_directions(cell_value)

    def _get_open_directions(self, cell_value: int) -> tuple[bool,
                                                             bool, bool, bool]:

        """Return the open sides as (north, east, south, west).

        A bit set to 1 in cell_value means a wall on that side.
        """
        nord = (cell_value & 1) == 0
        est = (cell_value & 2) == 0
        sud = (cell_value & 4) == 0
        west = (cell_value & 8) == 0
        return nord, est, sud, west

    def is_walkable(self) -> bool:
        """Return True if at least one side is open."""
        return self.opennord or self.openest or self.opensud or self.openwest

    def what_dir_is_walkable(self) -> list[str]:
        """Return the open directions: 'up', 'right', 'down', 'left'."""
        list_direzioni: list[str] = []
        if self.opennord:
            list_direzioni.append("up")
        if self.openest:
            list_direzioni.append("right")
        if self.opensud:
            list_direzioni.append("down")
        if self.openwest:
            list_direzioni.append("left")
        return list_direzioni


class Maze:
    """The whole maze: cells, item counter and spawn positions."""

    def __init__(
        self,
        raw_grid: list[list[int]],
        gum_points: int,
        bubblegum_points: int
    ) -> None:
        """Build the maze and place player, ghosts and super-pacgums.

        Args:
            raw_grid: Grid of wall bits from the maze generator.
            gum_points: Score of a pacgum.
            bubblegum_points: Score of a super-pacgum.
        """
        self.gum_points: int = gum_points
        self.bubblegum_points: int = bubblegum_points
        self.mappa: dict[tuple[int, int], Cell] = {}
        self.total_gums: int = 0
        self.player_start: tuple[int, int] = (0, 0)
        self.ghost_spawns: list[tuple[int, int]] = []
        self.max_x: int = 0
        self.max_y: int = 0
        self.build_maze(raw_grid)
        self.place_entities(raw_grid)

    def build_maze(self, raw_grid: list[list[int]]) -> None:

        """Create the cells and put a pacgum on each walkable one."""
        for y, riga in enumerate(raw_grid):
            for x, valore_cella in enumerate(riga):
                cella: Cell = Cell(valore_cella)
                if cella.is_walkable():
                    cella.item = Gum(self.gum_points)
                    self.total_gums += 1
                self.mappa[(x, y)] = cella

    def place_entities(self, raw_grid: list[list[int]]) -> None:
        """Set the player start (center) and the ghost corners."""
        max_y: int = len(raw_grid) - 1
        max_x: int = len(raw_grid[0]) - 1
        self.max_x = max_x
        self.max_y = max_y

        centro_x: int = max_x // 2
        centro_y: int = max_y // 2

        sicuro_centro_x, sicuro_centro_y = self.find_closest_walkable_bfs(
            centro_x, centro_y, max_x, max_y
        )
        self.player_start = (sicuro_centro_x, sicuro_centro_y)
        if self.mappa[self.player_start].item is not None:
            self.mappa[self.player_start].item = None
            self.total_gums -= 1

        # posizionamento di fantasmi e pucgum ai 4 angoli

        angoli_ideali: list[tuple[int, int]] = [
            (0, 0),
            (max_x, 0),
            (0, max_y),
            (max_x, max_y)
        ]

        for angolo_x, angolo_y in angoli_ideali:
            sicuro_angolo_x, sicuro_angolo_y = self.find_closest_walkable_bfs(
                angolo_x, angolo_y, max_x, max_y
            )
            tupla_sicura: tuple[int, int] = (sicuro_angolo_x, sicuro_angolo_y)
            self.ghost_spawns.append(tupla_sicura)
            self.mappa[tupla_sicura].item = Bubblegum(self.bubblegum_points)

    def find_closest_walkable_bfs(self,
                                  start_x: int,
                                  start_y: int,
                                  max_x: int,
                                  max_y: int) -> tuple[int, int]:

        """Find the walkable cell nearest to a point with a BFS.

        Args:
            start_x: Starting column.
            start_y: Starting row.
            max_x: Last valid column.
            max_y: Last valid row.

        Returns:
            The (x, y) of the closest walkable cell.
        """
        da_controllare: list[tuple[int, int]] = [(start_x, start_y)]
        visitati: set[tuple[int, int]] = {(start_x, start_y)}
        direzioni: list[tuple[int, int]] = [(0, -1), (1, 0), (0, 1), (-1, 0)]

        while da_controllare:
            corrente_x, corrente_y = da_controllare.pop(0)
            if self.mappa[(corrente_x, corrente_y)].is_walkable():
                return (corrente_x, corrente_y)
            for dx, dy in direzioni:
                vicino_x = corrente_x + dx
                vicino_y = corrente_y + dy
                if 0 <= vicino_x <= max_x and 0 <= vicino_y <= max_y:
                    if (vicino_x, vicino_y) not in visitati:
                        visitati.add((vicino_x, vicino_y))
                        da_controllare.append((vicino_x, vicino_y))
        return (start_x, start_y)
