import pygame
from pathlib import Path
from mazegenerator import MazeGenerator

TILE = 32

mappa = MazeGenerator(size=(20, 21), perfect=False, seed=42).maze

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
    for y, riga in enumerate(mappa):
        for x, numero in enumerate(riga):
            schermo.blit(tiles[numero], (x * TILE, y * TILE))
            if numero != 15:
                centro = (x * TILE + TILE//2, y * TILE + TILE//2)
                pygame.draw.circle(schermo, (255, 255, 0), centro, 3)
    pygame.display.flip()

pygame.quit()

"""dentro il doppio for loop del step 5, aggiungo i gum con
pygame.drawcircle e le coordinate del centro di ogni cella
della mappa tranne i png 15 cioe dove c'e il 42.
Dopo devo sostituire drawcircle con sprite
(((l'ultimo valore in drawcircle e' raggio del pallino)))"""
