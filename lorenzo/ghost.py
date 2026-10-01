from lorenzo.models import Maze


class Ghost():
    def __init__(self, maze: Maze, start_position: tuple[int, int]):
        self.x: int = start_position[0]
        self.y: int = start_position[1]
