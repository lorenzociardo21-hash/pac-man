import pygame
from pathlib import Path
from mazegenerator import MazeGenerator

griglia = MazeGenerator(size=(20, 21), perfect=False, seed=42).maze
numero = griglia[0][0]
# numero = 15
print(numero)

pygame.init()
schermo = pygame.display.set_mode((400, 400))

cartella = Path(__file__).parent / "assets"
tile = pygame.image.load(str(cartella / f"{numero}.png")).convert_alpha()
tile = pygame.transform.scale(tile, (200, 200))

running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
    schermo.fill((0, 0, 0))
    schermo.blit(tile, (100, 100))
    pygame.display.flip()

pygame.quit()

"""griglio 0 0 e' la cella top left quindi sopra e
 sinistra e' chiuso"""