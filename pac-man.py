import pygame
from src.core import App


"""
allora questo e' il main praticamente funziona con app che ha sempre una scena
che puo essere menu partita impostazioni ecc,
per ougni scena che una parte piglia gli eventi, una che aggiorna,
e una che disegna,
cosi lo rendiamo modulare e non e una merda
"""
app = App()
timer = pygame.time.Clock()


while app.running:

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            app.running = False
        else:
            app.scena.eventi(ev)

    app.scena.aggiorna(pygame.time.get_ticks())

    app.scena.disegna(app.finestra)

    pygame.display.flip()
    timer.tick(60)

pygame.quit()
