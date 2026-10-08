import pygame
from pathlib import Path
from mazegenerator import MazeGenerator
from src.models import Maze, Gum, Bubblegum
from src.player import Player
from src.controllore import Controll
from src.ghost import Ghost


class Scena:
    """
    Tutte scene ereditano da questa, cosi il while loop
    non va in crash se manca un metodo.
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
    Motore principale. Gestisce il while running,
    i setup base e gli asset grafici condivisi.
    """

    def __init__(self) -> None:
        pygame.init()
        l_desktop, a_desktop = pygame.display.get_desktop_sizes()[0]
        self.finestra = pygame.display.set_mode((l_desktop, a_desktop),
                                                pygame.FULLSCREEN
                                                | pygame.SCALED)
        self.running: bool = True
        self.font = pygame.font.Font(None, 48)
        self.cheat_attiva: bool = False
        self.partita_salvata: "Partita | None" = None

        # HUD
        self.altezza_hud: int = 40
        self.hud_x: int = 20
        self.hud_y: int = 20
        self.hud_spazio: int = 60
        cartella = Path(__file__).parent / "assets"

        # Importiamo tutte le img e i video
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
            img = pygame.image.load(str(cartella / f"{n}.png"))
            self.raw_tiles.append(img.convert_alpha())

        pygame.mixer.music.load(str(cartella / "musicsZ.mp3"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        # Importiamo immagine menu
        p_menu: str = str(cartella / "img_menu.png")
        img_menu_raw = pygame.image.load(p_menu).convert()
        rap_menu = img_menu_raw.get_width() / img_menu_raw.get_height()

        # Fissiamo il limite massimo all'80% della grandezza del desktop
        limite_larghezza = int(l_desktop * 0.8)
        limite_altezza = int(a_desktop * 0.8)

        # Calcolo le dimensioni mantenendo le proporzioni
        if limite_altezza * rap_menu > limite_larghezza:
            larghezza_finale = limite_larghezza
            altezza_finale = int(limite_larghezza / rap_menu)
        else:
            altezza_finale = limite_altezza
            larghezza_finale = int(limite_altezza * rap_menu)

        self.img_menu = pygame.transform.smoothscale(
            img_menu_raw, (larghezza_finale, altezza_finale)
        )

        self.scena: Scena = Menu(self)


class Partita(Scena):
    def __init__(self, app: 'App') -> None:
        super().__init__(app)
        generatore: MazeGenerator = MazeGenerator(size=(14, 14),
                                                  perfect=False, seed=10)
        self.mappa: list[list[int]] = generatore.maze
        self.maze: Maze = Maze(self.mappa, 10, 20)
        self.player: Player = Player(self.maze, 3)

        if self.app.cheat_attiva:
            self.player.cheat = True
        else:
            self.player.cheat = False

        self.ghosts = [
            Ghost(self.maze, pos, self.player)
            for pos in self.maze.ghost_spawns
        ]
        self.controll = Controll(self.maze, self.ghosts, self.player)

        self.MOVE_DELAY = 350
        self.GHOST_DELAY = 500

        tick_iniziale = pygame.time.get_ticks()
        self.ultimo_move = tick_iniziale
        self.ultimo_move_ghost = tick_iniziale

        self.last_coord_player = (self.player.x, self.player.y)
        self.last_coord_ghost = [(g.x, g.y) for g in self.ghosts]

        larghezza_schermo, altezza_schermo = self.app.finestra.get_size()
        self.TILE = min(larghezza_schermo // 20, altezza_schermo // 21)
        self.margine_x = (
            larghezza_schermo - len(self.mappa[0]) * self.TILE) // 2
        self.margine_y = (altezza_schermo - len(self.mappa) * self.TILE) // 2
        self.dimensione_coso = 20
        self.offset = (self.TILE - self.dimensione_coso) // 2

        self.tiles = []
        for img in self.app.raw_tiles:
            img_scalata = pygame.transform.scale(img, (self.TILE, self.TILE))
            self.tiles.append(img_scalata)

    def eventi(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:

                self.app.partita_salvata = self

                self.app.scena = Pausa(self.app)
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
        self.py = self.magia(self.last_coord_player[1],
                             self.player.y, progresso_player)

        self.pos_ghosts = []
        for g, p in zip(self.ghosts, self.last_coord_ghost):
            nx = self.magia(p[0], g.x, progresso_ghost)
            ny = self.magia(p[1], g.y, progresso_ghost)
            self.pos_ghosts.append((nx, ny))

        self.controll.controlliamo((self.px, self.py), self.pos_ghosts)
        if self.controll.hit:
            pygame.time.wait(1000)
            self.controll.riparti()
            self.last_coord_player = (self.player.x, self.player.y)
            self.last_coord_ghost = [(g.x, g.y) for g in self.ghosts]
            tick = pygame.time.get_ticks()
            self.ultimo_move = tick
            self.ultimo_move_ghost = tick

        if not self.controll.show_must_go_on or self.controll.you_win:
            self.app.scena = Menu(self.app)

    def disegna(self, finestra: pygame.Surface) -> None:
        finestra.fill((0, 0, 0))
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

        centro_player = (
            int(self.margine_x + self.px * self.TILE + self.TILE // 2),
            int(self.margine_y + self.py * self.TILE + self.TILE // 2))
        pygame.draw.circle(finestra, (200, 155, 0), centro_player,
                           self.dimensione_coso // 2)

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


class Menu(Scena):
    def __init__(self, app: 'App') -> None:
        super().__init__(app)

        self.num_opzioni = 5
        self.selezione = 0

        self.l_schermo, self.a_schermo = self.app.finestra.get_size()
        self.centro_x = self.l_schermo // 2

        self.larghezza_lente = 330
        self.altezza_lente = 75

        # lente gialla
        self.lente = pygame.Surface(
            (self.larghezza_lente, self.altezza_lente), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.lente,
            (255, 255, 0, 100),
            (0, 0, self.larghezza_lente, self.altezza_lente),
            border_radius=30
        )
        # lente Rossa cheatmode
        self.lente_rossa = pygame.Surface(
            (self.larghezza_lente, self.altezza_lente), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.lente_rossa, (255, 0, 0, 100),
            (0, 0, self.larghezza_lente, self.altezza_lente), border_radius=30
        )

        self.y_primo_bottone = self.a_schermo // 2 - 102
        self.distanza_bottoni = 100

    def eventi(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_DOWN:
                self.selezione = (self.selezione + 1) % self.num_opzioni
            elif ev.key == pygame.K_UP:
                self.selezione = (self.selezione - 1) % self.num_opzioni
            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.selezione == 0:
                    self.app.scena = Partita(self.app)
                elif self.selezione == 1:
                    print("TODO: Aprire Highscores")
                elif self.selezione == 2:
                    print("TODO: Aprire Istruzioni")
                elif self.selezione == 3:
                    self.app.cheat_attiva = not self.app.cheat_attiva
                elif self.selezione == 4:
                    self.app.running = False

    def aggiorna(self, adesso: int) -> None:
        pass

    def disegna(self, finestra: pygame.Surface) -> None:
        finestra.fill((0, 0, 0))

        img_w = self.app.img_menu.get_width()
        img_h = self.app.img_menu.get_height()
        x_img = (self.l_schermo - img_w) // 2
        y_img = (self.a_schermo - img_h) // 2
        finestra.blit(self.app.img_menu, (x_img, y_img))

        y_selezione = self.y_primo_bottone + (
            self.distanza_bottoni * self.selezione)
        x_lente = self.centro_x - (self.larghezza_lente // 2)

        if self.app.cheat_attiva:
            y_cheat = self.y_primo_bottone + (self.distanza_bottoni * 3)
            finestra.blit(self.lente_rossa, (x_lente, y_cheat))

        finestra.blit(self.lente, (x_lente, y_selezione))


class Pausa(Scena):
    def __init__(self, app: 'App') -> None:
        super().__init__(app)
        self.voci = ["RESUME THE GAME", "RETURN TO MAIN MENU"]
        self.selezione = 0

    def eventi(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_DOWN:
                self.selezione = (self.selezione + 1) % 2
            elif ev.key == pygame.K_UP:
                self.selezione = (self.selezione - 1) % 2
            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.selezione == 0:
                    salvataggio = self.app.partita_salvata
                    if salvataggio is not None:
                        self.app.scena = salvataggio
                elif self.selezione == 1:
                    self.app.partita_salvata = None
                    self.app.scena = Menu(self.app)
                elif ev.key == pygame.K_ESCAPE:
                    salvataggio = self.app.partita_salvata
                    if salvataggio is not None:
                        self.app.scena = salvataggio

    def disegna(self, finestra: pygame.Surface) -> None:
        if self.app.partita_salvata:
            self.app.partita_salvata.disegna(finestra)

        sfondo_scuro = pygame.Surface(finestra.get_size(), pygame.SRCALPHA)
        sfondo_scuro.fill((0, 0, 0, 150))
        finestra.blit(sfondo_scuro, (0, 0))

        for i, voce in enumerate(self.voci):
            colore = (255, 255, 0) if i == self.selezione else (150, 150, 150)
            testo = self.app.font.render(voce, True, colore)
            rect = testo.get_rect(center=(
                finestra.get_width()//2, 300 + (80 * i)))
            finestra.blit(testo, rect)
