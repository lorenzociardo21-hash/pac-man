import pygame
from pathlib import Path

pygame.init()
schermo = pygame.display.set_mode((400, 400))

cartella = Path(__file__).parent / "assets"
tile = pygame.image.load(str(cartella / "3.png")).convert_alpha()
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

"""creo finestra con schermo = ... e creo tile = ... che carica
il png 3 con convert alpha per avere lo sfondo trasparente.
poi creo loop e con blit mi appare l'immagine"""