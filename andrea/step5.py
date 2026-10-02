import pygame
from pathlib import Path
from mazegenerator import MazeGenerator

TILE = 32

griglia = MazeGenerator(size=(20, 21), perfect=False, seed=42).maze

pygame.init()
schermo = pygame.display.set_mode((20 * TILE, 21 * TILE))

cartella = Path(__file__).parent / "assets"
tiles = []
for n in range(16):
    img = pygame.image.load(str(cartella / f"{n}.png")).convert_alpha()
    img = pygame.transform.scale(img, (TILE, TILE))
    tiles.append(img)


running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
    schermo.fill((0, 0, 0))
    for y, riga in enumerate(griglia):
        for x, numero in enumerate(riga):
            schermo.blit(tiles[numero], (x * TILE, y * TILE))
    pygame.display.flip()

pygame.quit()

"""come step 4 ma sostituisco il loop x, numero in enumerate
 con un doppio loop che prende la griglia e le righe"""