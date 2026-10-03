import pygame
from mazegenerator import MazeGenerator
from lorenzo.models import Maze, Gum, Bubblegum, Cell
from lorenzo.player import Player
from lorenzo.ghost import Ghost
from lorenzo.controllore import Controll
from pathlib import Path



generatore: MazeGenerator = MazeGenerator(size=(20, 21),
                                          perfect=False,
                                          seed=42)
mappa: list[list[int]] = generatore.maze
maze: Maze = Maze(mappa, 10, 20)
player: Player = Player(maze, 3)
ghosts = [Ghost(maze, pos, player) for pos in maze.ghost_spawns]
controll = Controll(maze, ghosts, player)

pygame.init()
larghezza_desktop, altezza_desktop = pygame.display.get_desktop_sizes()[0]
finestra = pygame.display.set_mode((larghezza_desktop, altezza_desktop),
                                   pygame.FULLSCREEN | pygame.SCALED)

TILE = min(finestra.get_width() // 20, finestra.get_height() // 21)
larghezza_schermo, altezza_schermo = finestra.get_size()
margine_x = (larghezza_schermo - len(mappa[0]) * TILE) // 2
margine_y = (altezza_schermo - len(mappa) * TILE) // 2
dimensione_coso = 20
offset = (TILE - dimensione_coso) // 2


cartella = Path(__file__).parent / "andrea/assets"

altezza_hud = 40
hud_x = 20
hud_y = 20
hud_spazio = 60

immagine_punti = pygame.image.load(str(cartella / "punti.png")).convert_alpha()
rapporto = immagine_punti.get_width() / immagine_punti.get_height()
immagine_punti = pygame.transform.smoothscale(
    immagine_punti, (int(altezza_hud * rapporto), altezza_hud))
font = pygame.font.Font(None, 48)

immagine_vite = pygame.image.load(str(cartella / "vite.png")).convert_alpha()
rapporto_lives = immagine_vite.get_width() / immagine_vite.get_height()
immagine_vite = pygame.transform.smoothscale(
    immagine_vite, (int(altezza_hud * rapporto_lives), altezza_hud))


try:
    pygame.mixer.music.load(str(cartella / "musicsZ.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"[audio] no music: {e}")

"""da vedere come cazzo si usa. sicuramente con il key event come
quello per muoversi"""
# pygame.mixer.music.pause()
# pygame.mixer.music.unpause()

"""da aggiungere nel loop se si vuole soundeffects di tutto.
esempio con gum :"""
# suono_gum = pygame.mixer.Sound(str(cartella / "nomefile"))
# suono_gum.play()

tiles = []
for n in range(16):
    img = pygame.image.load(str(cartella / f"{n}.png")).convert_alpha()
    img = pygame.transform.scale(img, (TILE, TILE))
    tiles.append(img)


timer = pygame.time.Clock()
running = True
MOVE_DELAY = 200
"""piu e' alto il delay piu vanno piano"""
GHOST_DELAY = 300
ultimo_move = 0
ultimo_move_ghost = 0
last_coord_player = (player.x, player.y)
last_coord_ghost = [(g.x, g.y) for g in ghosts]

def magia(a: float, b: float, t: float) -> float:
    return a + (b- a) * t

while running:
    for ev in pygame.event.get():
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

    # keys = pygame.key.get_pressed()
    # if keys[pygame.K_UP]:
    #     player.direzione = "up"
    # if keys[pygame.K_DOWN]:
    #     player.direzione = "down"
        
    # if keys[pygame.K_LEFT]:
    #     player.direzione = "left"
        
    # if keys[pygame.K_RIGHT]:
    #     player.direzione = "right"
            
        
            

    """prendo il tempo da pygame con get_ticks in millisecondi.
    se sono passati 200ms dall'ultimo step entro nell' if.
    Se entro nell'if, resetto ultimo_move, salvo la posizione del
    player e del ghost prima di muovermi e quindi prima di player.move().
    progresso calcola la percentuale della distanza percorsa tra la cella
    in cui si trova il coso e la cella in cui sta andando."""
    adesso = pygame.time.get_ticks()
    mosso = False
    vite_prima = player.lives
    if adesso - ultimo_move >= MOVE_DELAY:
        ultimo_move = adesso
        last_coord_player = (player.x, player.y)
        player.move()
        mosso = True

    if adesso - ultimo_move_ghost >= GHOST_DELAY:
        ultimo_move_ghost = adesso
        last_coord_ghost = [(g.x, g.y) for g in ghosts]
        for ghost in ghosts:
            ghost.move()
        mosso = True

    if mosso:
        controll.controlliamo()
        if player.lives < vite_prima:
            last_coord_player = (player.x, player.y)
            last_coord_ghost = [(g.x, g.y) for g in ghosts]
        if not controll.show_must_go_on or controll.you_win:
            running = False

    progresso_player = min((adesso - ultimo_move) / MOVE_DELAY, 1)
    progresso_ghost = min((adesso - ultimo_move_ghost) / GHOST_DELAY, 1)


    finestra.fill((0, 0, 0))


    for y, riga in enumerate(mappa):
        for x, numero in enumerate(riga):
            finestra.blit(tiles[numero], (margine_x + x * TILE, margine_y + y * TILE))
            item = maze.mappa[x, y].item
            centro = (margine_x + x * TILE + TILE // 2,
                      margine_y + y * TILE + TILE // 2)
            if isinstance(item, Gum):            
                pygame.draw.circle(finestra, (255, 255, 0), centro, 3)
            elif isinstance(item, Bubblegum):
                pygame.draw.circle(finestra, (200, 155, 0), centro, 7)

    """Ora uso px e py invece di player.x e player.y. px e py possono essere
    decimali e quindi il movimento appare piu fluido."""
    px = magia(last_coord_player[0], player.x, progresso_player)
    py = magia(last_coord_player[1], player.y, progresso_player)
    centro_player = (int(margine_x + px * TILE + TILE // 2),
                     int(margine_y + py * TILE + TILE // 2))
    pygame.draw.circle(finestra, (200, 155, 0), centro_player,
                       dimensione_coso // 2)


    """gx e gy si comportano come px e py di prima. Aggiungendo prima e zip,
    ogni ghost adesso continene anche le info della cella precedente."""
    for ghost, prima in zip(ghosts, last_coord_ghost):
        gx = magia(prima[0], ghost.x, progresso_ghost)
        gy = magia(prima[1], ghost.y, progresso_ghost)
        pygame.draw.rect(finestra, (1, 155, 0),
                         (int(margine_x + gx * TILE + offset),
                          int(margine_y + gy * TILE + offset),
                          dimensione_coso, dimensione_coso))

    finestra.blit(immagine_punti, (hud_x, hud_y))
    numero = font.render(str(player.points), True, (255, 255, 255))
    finestra.blit(numero, (20 + immagine_punti.get_width() + 10, 20))

    finestra.blit(immagine_vite, (hud_x, hud_y + hud_spazio))
    vite = font.render(str(player.lives), True, (255, 255, 255))
    finestra.blit(vite, (hud_x + immagine_vite.get_width() + 10,
                         hud_y + hud_spazio))

    timer.tick(60)
    pygame.display.flip()

pygame.mixer.music.stop()
pygame.quit()
