import pygame
from pathlib import Path
from mazegenerator import MazeGenerator
from src.player import Player
from src.controllore import Controll
from src.models import Maze, Gum, Bubblegum
from src.ghost import Ghost


"""
allora sto facendo delle modifiche grosse al while running scusa,
 il concetto e che
ettore mi ha ffatto vedere come renderlo modulare, ora ci sara una classe app,
 che gestira
le scene, cosa sono le scene? sono le varie scghermate che possiamo
avere tipo menu, impostazioni, partita, ecc ,
cosi il ehile running e piu pulito e va da una scena allatra
sembra complicato ma non credo lo sia troppo credo
"""


class Scena:
    """
    allora tutte scene eraditano da scena cosi che il while tru
    non va in crash se ne manca uno come ad esempio il menu che non
    ha bisogno di aggiorna
    """
    def __init__(self, app: 'App') -> None:
        self.app: 'App' = app

    def eventi(self, ev: pygame.event.Event) -> None:
        pass

    def aggiorna(self, adesso: int) -> None:
        pass

    def disegna(self, finestra: pygame.Surface) -> None:
        pass


class App:
    """
    allora linit di app avra tutto quello che si fa primi del
    while running di pygame
    qualsiasi disegno  e cose che aggiungeremo sarrano salvate qua
    come img punte ecc, non ho ancora
    scalato il labirinto perche dipnede dalla grandezza cghe il lab,
    mentre il resto e' gia
    scalato
    """
    def __init__(self) -> None:
        pygame.init()
        l_desktop, a_desktop = pygame.display.get_desktop_sizes()[0]
        self.finestra = pygame.display.set_mode((l_desktop, a_desktop),
                                                pygame.FULLSCREEN
                                                | pygame.SCALED)
        self.running: bool = True
        self.font = pygame.font.Font(None, 48)
        # HUD
        self.altezza_hud: int = 40
        self.hud_x: int = 20
        self.hud_y: int = 20
        self.hud_spazio: int = 60
        cartella = Path(__file__).parent / "assets"

        # importiamo tutte le img e i video
        p_punti: str = str(cartella / "punti.png")
        img_punti_raw = pygame.image.load(p_punti).convert_alpha()
        rap_punti = img_punti_raw.get_width() / img_punti_raw.get_height()
        self.img_punti = pygame.transform.smoothscale(
            img_punti_raw, (int(self.altezza_hud * rap_punti),
                            self.altezza_hud)
        )
        p_file: str = str(cartella / "vite.png")
        img_vite_raw = pygame.image.load(p_file).convert_alpha()
        rap_vite = img_vite_raw.get_width() / img_vite_raw.get_height()
        self.img_vite = pygame.transform.smoothscale(
            img_vite_raw, (int(self.altezza_hud * rap_vite), self.altezza_hud)
        )

        self.raw_tiles: list[pygame.Surface] = []
        for n in range(16):
            img = pygame.image.load(str(cartella / f"{n}.png")).convert_alpha()
            self.raw_tiles.append(img)

        pygame.mixer.music.load(str(cartella / "musicsZ.mp3"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        self.scena = Partita(self)


class Partita(Scena):

    def __init__(self, app: App) -> None:
        """
        qui gestiamo la partita ettutto
        per ora lunica iterfaccia che abbiamo
        prendo le parti del whil running e le divido nelle
        varie funzioni
        da capire poi come
        incremengtare i livelli
        metto in scala anche le cose
        """
        super().__init__(app)
        generatore: MazeGenerator = MazeGenerator(size=(14, 14),
                                                  perfect=False, seed=10)
        self.mappa: list[list[int]] = generatore.maze
        self.maze: Maze = Maze(self.mappa, 10, 20)
        self.player: Player = Player(self.maze, 3)
        self.player.cheat = True
        self.ghosts = [
            Ghost(self.maze,
                  pos, self.player) for pos in self.maze.ghost_spawns
                      ]
        self.controll = Controll(self.maze, self.ghosts, self.player)
        # piu aumeti il numero piu vanno piano
        self.MOVE_DELAY = 350
        self.GHOST_DELAY = 500
        self.ultimo_move = 0
        self.ultimo_move_ghost = 0

        self.last_coord_player = (self.player.x, self.player.y)
        self.last_coord_ghost = [(g.x, g.y) for g in self.ghosts]

        # per la parte grafica
        larghezza_schermo, altezza_schermo = self.app.finestra.get_size()
        self.TILE = min(larghezza_schermo // 20, altezza_schermo // 21)
        self.margine_x = (
            larghezza_schermo - len(self.mappa[0]) * self.TILE) // 2
        self.margine_y = (altezza_schermo - len(self.mappa) * self.TILE) // 2
        self.dimensione_coso = 20
        self.offset = (self.TILE - self.dimensione_coso) // 2

        # Scaliamo le immagini dei muri
        self.tiles = []
        for img in self.app.raw_tiles:
            img_scalata = pygame.transform.scale(img, (self.TILE, self.TILE))
            self.tiles.append(img_scalata)

    def eventi(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                self.app.running = False
                # self.app.scena = Menu(self.app)
                pass
            elif ev.key in (pygame.K_UP, pygame.K_w):
                self.player.seconda_direzione = "up"
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                self.player.seconda_direzione = "down"
            elif ev.key in (pygame.K_LEFT, pygame.K_a):
                self.player.seconda_direzione = "left"
            elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                self.player.seconda_direzione = "right"

    def magia(self, a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    def aggiorna(self, adesso: int) -> None:
        """
        la funzione aggiorna probabilmente la usiamo solo
        in partita perche solo in partita il grafico
        si aggiorna senza che tu abbia toccato niente,
        e qui ce tutta la logica del movimento
        copiata e incollata dal tuo con laggiunta di self
        dio canaglia
        """
        if adesso - self.ultimo_move >= self.MOVE_DELAY:
            self.ultimo_move = adesso
            self.last_coord_player = (self.player.x, self.player.y)
            self.player.move()

        if adesso - self.ultimo_move_ghost >= self.GHOST_DELAY:
            self.ultimo_move_ghost = adesso
            self.last_coord_ghost = [(g.x, g.y) for g in self.ghosts]
            for ghost in self.ghosts:
                ghost.move()

        progresso_player = min((adesso - self.ultimo_move) /
                               self.MOVE_DELAY, 1)
        progresso_ghost = min((adesso - self.ultimo_move_ghost) /
                              self.GHOST_DELAY, 1)
        self.px = self.magia(self.last_coord_player[0],
                             self.player.x, progresso_player)
        self.py = self.magia(self.last_coord_player[1], self.player.y,
                             progresso_player)
        self.pos_ghosts = [(self.magia(p[0], g.x, progresso_ghost),
                            self.magia(p[1], g.y, progresso_ghost))
                           for g, p in zip(self.ghosts, self.last_coord_ghost)]

        self.controll.controlliamo((self.px, self.py), self.pos_ghosts)
        if self.controll.hit:
            pygame.time.wait(1000)
            self.controll.riparti()
            self.last_coord_player = (self.player.x, self.player.y)
            self.last_coord_ghost = [(g.x, g.y) for g in self.ghosts]
            self.ultimo_move = self.ultimo_move_ghost = pygame.time.get_ticks()

        if not self.controll.show_must_go_on or self.controll.you_win:
            self.app.running = False
            # self.app.scena = Menu(self.app)

    def disegna(self, finestra: pygame.Surface) -> None:

        finestra.fill((0, 0, 0))
        # Disegna i muri e i pallini
        for y, riga in enumerate(self.mappa):
            for x, numero in enumerate(riga):
                finestra.blit(self.tiles[numero],
                              (self.margine_x + x * self.TILE,
                               self.margine_y + y * self.TILE))
                item = self.maze.mappa[x, y].item
                centro = (self.margine_x + x * self.TILE + self.TILE // 2,
                          self.margine_y + y * self.TILE + self.TILE // 2)
                if isinstance(item, Gum):
                    pygame.draw.circle(finestra, (255, 255, 0), centro, 3)
                elif isinstance(item, Bubblegum):
                    pygame.draw.circle(finestra, (200, 155, 0), centro, 7)

        # Disegna il giocatore
        centro_player = (
            int(self.margine_x + self.px * self.TILE + self.TILE // 2),
            int(self.margine_y + self.py * self.TILE + self.TILE // 2))
        pygame.draw.circle(finestra, (200, 155, 0), centro_player,
                           self.dimensione_coso // 2)

        # Disegna i fantasmi
        for ghost, (gx, gy) in zip(self.ghosts, self.pos_ghosts):
            if ghost.dead:
                colore = (200, 200, 200)
            elif getattr(ghost, 'stupid', False):
                colore = (255, 0, 0)
            else:
                colore = (1, 155, 0)

            pygame.draw.rect(
                finestra, colore,
                (int(self.margine_x + gx * self.TILE + self.offset),
                 int(self.margine_y + gy * self.TILE + self.offset),
                 self.dimensione_coso, self.dimensione_coso))

        # Disegna l'HUD (pescando immagini e font da self.app)
        finestra.blit(self.app.img_punti, (self.app.hud_x, self.app.hud_y))
        testo_numero = self.app.font.render(
            str(self.player.points), True, (255, 255, 255))
        finestra.blit(testo_numero,
                      (20 + self.app.img_punti.get_width() + 10, 20))
        finestra.blit(
            self.app.img_vite, (
                self.app.hud_x, self.app.hud_y + self.app.hud_spazio))
        vite = self.app.font.render(
            str(self.player.lives), True, (255, 255, 255))
        finestra.blit(vite, (
            self.app.hud_x + self.app.img_vite.get_width() + 10,
            self.app.hud_y + self.app.hud_spazio))
