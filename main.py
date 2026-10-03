import pygame
from mazegenerator import MazeGenerator
from lorenzo.models import Maze, Gum, Bubblegum, Cell
from lorenzo.player import Player
from lorenzo.ghost import Ghost
from pathlib import Path


TILE = 48
generatore = MazeGenerator(size=(20, 21), perfect=False, seed=42)
mappa = generatore.maze
maze: Maze = Maze(mappa, 10, 20)
player: Player = Player(maze, 3)
ghosts = [Ghost(maze, pos, player) for pos in maze.ghost_spawns]
finestra = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
# window: Window = Window(1980, 1200, "PACCO-MANNO")

# mappa = MazeGenerator(size=(20, 21), perfect=False, seed=42).maze

pygame.init()
# window = pygame.display.set_mode((20 * TILE, 21 * TILE))

cartella = Path(__file__).parent / "andrea/assets"
tiles = []
for n in range(16):
    img = pygame.image.load(str(cartella / f"{n}.png")).convert_alpha()
    img = pygame.transform.scale(img, (TILE, TILE))
    tiles.append(img)

lato = 20


timer = pygame.time.Clock()

running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                running = False
            elif ev.key in (pygame.K_UP, pygame.K_w):
                player.direzione = "up"
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                player.direzione = "down"
            elif ev.key in (pygame.K_LEFT, pygame.K_a):
                player.direzione = "left"
            elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                player.direzione = "right"
    player.move()
    for ghost in ghosts:
        ghost.move()

    finestra.fill((0, 0, 0))
    for y, riga in enumerate(mappa):
        for x, numero in enumerate(riga):
            finestra.blit(tiles[numero], (x * TILE, y * TILE))
            if isinstance(maze.mappa[x, y].item, Gum):
                centro = (x * TILE + TILE // 2, y * TILE + TILE // 2)
                pygame.draw.circle(finestra, (255, 255, 0), centro, 3)
            elif isinstance(maze.mappa[x, y].item, Bubblegum):
                centro = (x * TILE + TILE // 2, y * TILE + TILE // 2)
                pygame.draw.circle(finestra, (200, 155, 0), centro, 7)
    pygame.draw.rect(finestra, (200, 155, 0),
                     (player.x * TILE+15, player.y * TILE + 15, lato, lato))
    for ghost in ghosts:
        pygame.draw.rect(finestra, (1, 155, 0),
                         (ghost.x * TILE+15, ghost.y * TILE + 15, lato, lato))

    timer.tick(5)
    pygame.display.flip()

pygame.quit()
