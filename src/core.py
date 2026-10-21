import random
import pygame
from pathlib import Path
from mazegenerator import MazeGenerator
from src.models import Maze, Gum, Bubblegum
from src.player import Player
from src.controllore import Controll
from src.ghost import Ghost
from src.highscore import Highscores
from src.config import Config


class Scena:
    """Base class for every scene (menu, game, pause, ...).

    Each scene has three hooks: events, update and draw. The default
    hooks do nothing, so the main loop never crashes if one is missing.
    """

    def __init__(self, app: 'App') -> None:
        self.app: 'App' = app

    def eventi(self, ev: pygame.event.Event) -> None:
        """Handle one pygame event."""
        pass

    def aggiorna(self, adesso: int) -> None:
        """Update the scene state.

        Args:
            adesso: Current time in milliseconds (pygame ticks).
        """
        pass

    def disegna(self, finestra: pygame.Surface) -> None:
        """Draw the scene on the given surface."""
        pass


class App:
    """Main engine: window setup, shared assets and the current scene."""

    def __init__(self, config: Config) -> None:
        """Initialise pygame, build the levels and load the shared assets.

        Args:
            config: Validated game configuration.
        """
        self.config = config
        pygame.init()
        l_desktop, a_desktop = pygame.display.get_desktop_sizes()[0]
        self.finestra = pygame.display.set_mode((l_desktop, a_desktop),
                                                pygame.FULLSCREEN
                                                | pygame.SCALED)
        self.running: bool = True
        self.font = pygame.font.Font(None, 48)
        self.cheat_attiva: bool = False
        self.partita_salvata: "Partita | None" = None
        self.tempo_menu: int = 0
        self.change_level: bool = False

        self.livello_corrente: int = 0
        self.livelli: list[dict[str, int]] = [
            {"seed": config.seed, "move_delay": 350, "ghost_delay": 500}
        ]
        for i in range(1, 10):
            self.livelli.append({
                "seed": random.randint(1, 1000000),
                "move_delay": max(150, 350 - (i * 20)),
                "ghost_delay": max(220, 500 - (i * 30))
            })

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

        # Caricamento delle 10 cifre (0-9)
        self.img_numeri: list[pygame.Surface] = []
        for n in range(10):
            img_num_raw = pygame.image.load(
                str(cartella / f"tempo_{n}.png")).convert_alpha()
            rap_num = img_num_raw.get_width() / img_num_raw.get_height()
            img_num = pygame.transform.smoothscale(
                img_num_raw, (
                    int(self.altezza_hud * rap_num), self.altezza_hud)
            )
            self.img_numeri.append(img_num)

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

        self.highscores = Highscores(config.highscore_filename)
        self.scena: Scena = Menu(self)

        raw_lore: list[pygame.Surface] = []
        for n in range(3):
            img_path = str(cartella / f"lore_{n}.png")
            img = pygame.image.load(img_path).convert_alpha()
            raw_lore.append(img)

        # Dizionario con le liste di frame per ciascuna direzione
        self.pacman_sprites_lore: dict[str, list[pygame.Surface]] = {
            "left": raw_lore,
            "right": [
                pygame.transform.flip(img, True, False) for img in raw_lore],
            "up": [pygame.transform.rotate(img, 270) for img in raw_lore],
            "down": [pygame.transform.rotate(img, 90) for img in raw_lore],
            "": raw_lore
        }

        raw_andrea: list[pygame.Surface] = []
        for n in range(3):
            img_path = str(cartella / f"andrea_{n}.png")
            img = pygame.image.load(img_path).convert_alpha()
            raw_andrea.append(img)

        self.pacman_sprites_andrea: dict[str, list[pygame.Surface]] = {
            "left": raw_andrea,
            "right": [
                pygame.transform.flip(img, True, False) for img in raw_andrea],
            "up": [pygame.transform.rotate(img, 270) for img in raw_andrea],
            "down": [pygame.transform.rotate(img, 90) for img in raw_andrea],
            "": raw_andrea
        }

        self.raw_ghost: list[pygame.Surface] = []
        for n in range(4):
            img_path = str(cartella / f"ghost{n}.png")
            img = pygame.image.load(img_path).convert_alpha()
            self.raw_ghost.append(img)

        self.player_img: bool = False
        self.img_selezione_lciaro = pygame.image.load(
            str(cartella / "lciardo.png")).convert_alpha()
        self.img_selezione_acentron = pygame.image.load(
            str(cartella / "acentron.png")).convert_alpha()


class Partita(Scena):
    """Game scene: one level with maze, player, ghosts and HUD."""

    def __init__(self, app: 'App', punti_iniziali: int = 0,
                 vite_iniziali: int | None = None) -> None:
        """Generate the maze and set up entities, timers and sprites.

        Args:
            app: The main application.
            punti_iniziali: Score carried over from the previous level.
            vite_iniziali: Lives carried over (config value if None).
        """
        super().__init__(app)
        cfg = self.app.config
        dati_livello = self.app.livelli[self.app.livello_corrente]
        seed_livello = dati_livello["seed"]

        generatore: MazeGenerator = MazeGenerator(size=(cfg.width, cfg.height),
                                                  perfect=False,
                                                  seed=seed_livello)
        self.mappa: list[list[int]] = generatore.maze
        self.maze: Maze = Maze(self.mappa, cfg.points_per_pacgum,
                               cfg.points_per_super_pacgum)

        vite_effettive = (
            vite_iniziali if vite_iniziali is not None else cfg.lives)
        self.player: Player = Player(self.maze, vite_effettive)
        self.player.points = punti_iniziali

        self.ghosts = [
            Ghost(self.maze, pos, self.player)
            for pos in self.maze.ghost_spawns
        ]
        self.controll = Controll(self.maze, self.ghosts, self.player,
                                 self.app.config.points_per_ghost)

        self.MOVE_DELAY = dati_livello["move_delay"]
        self.GHOST_DELAY = dati_livello["ghost_delay"]

        tick_iniziale = pygame.time.get_ticks()
        self.ultimo_move = tick_iniziale
        self.ultimo_move_ghost = tick_iniziale

        self.last_coord_player = (self.player.x, self.player.y)
        self.last_coord_ghost = [(g.x, g.y) for g in self.ghosts]

        self.px: float = float(self.player.x)
        self.py: float = float(self.player.y)
        self.pos_ghosts: list[tuple[float, float]] = [
            (float(g.x), float(g.y)) for g in self.ghosts
        ]
        larghezza_schermo, altezza_schermo = self.app.finestra.get_size()
        self.TILE = min(larghezza_schermo // 15, altezza_schermo // 16)
        self.margine_x = (
            larghezza_schermo - len(self.mappa[0]) * self.TILE) // 2
        self.margine_y = (altezza_schermo - len(self.mappa) * self.TILE) // 2

        self.dimensione_coso = 90
        self.offset = (self.TILE - self.dimensione_coso) // 2

        self.dimensione_ghost = 150
        self.offset_ghost = (self.TILE - self.dimensione_ghost) // 2

        self.tiles = []
        for img in self.app.raw_tiles:
            img_scalata = pygame.transform.scale(img, (self.TILE, self.TILE))
            self.tiles.append(img_scalata)

        self.max_time: int = cfg.level_max_time
        self.start_time: int = pygame.time.get_ticks()
        self.time_remining: int = self.max_time
        self.pausa_start: int = 0

        if self.app.player_img:
            self.pacman_frames: dict[str, list[pygame.Surface]] = {}
            for dir_key, lista_frame in self.app.pacman_sprites_lore.items():
                self.pacman_frames[dir_key] = [
                    pygame.transform.smoothscale(img, (self.dimensione_coso,
                                                       self.dimensione_coso))
                    for img in lista_frame
                ]
        else:
            self.pacman_frames = {}
            for dir_key, lista_frame in self.app.pacman_sprites_andrea.items():
                self.pacman_frames[dir_key] = [
                    pygame.transform.smoothscale(img, (self.dimensione_coso,
                                                       self.dimensione_coso))
                    for img in lista_frame
                ]

        self.ghost_images: list[pygame.Surface] = [
            pygame.transform.smoothscale(img, (self.dimensione_ghost,
                                               self.dimensione_ghost))
            for img in self.app.raw_ghost
        ]
        self.cambiaghost: int = 0

    def eventi(self, ev: pygame.event.Event) -> None:
        """Handle movement keys, pause (ESC) and level skip (N)."""
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                self.pausa_start = pygame.time.get_ticks()
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
            elif ev.unicode in ("n", "N"):
                if self.app.cheat_attiva:
                    self.app.change_level = True
            elif ev.unicode in ("m", "M"):
                if self.app.cheat_attiva:
                    self.player.cheat_player = not self.player.cheat_player

    def magia(self, a: float, b: float, t: float) -> float:
        """Linear interpolation between a and b (t from 0 to 1)."""
        return a + (b - a) * t

    def aggiorna(self, adesso: int) -> None:
        """Move player and ghosts, check collisions, win/lose and the timer."""
        secondi_passati = (adesso - self.start_time) // 1000
        self.time_remining = max(0, self.max_time - secondi_passati)
        if self.time_remining <= 0:
            self.controll.show_must_go_on = False

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

        self.controll.controlliamo((self.px, self.py), self.pos_ghosts,
                                   progresso_player)
        if self.controll.hit:
            pygame.time.wait(1000)
            self.controll.riparti()
            self.last_coord_player = (self.player.x, self.player.y)
            self.last_coord_ghost = [(g.x, g.y) for g in self.ghosts]
            tick = pygame.time.get_ticks()
            self.ultimo_move = tick
            self.ultimo_move_ghost = tick

        if not self.controll.show_must_go_on:
            self.app.scena = FineGioco(self.app, self.player.points, False)
            return

        if self.controll.you_win or self.app.change_level:
            self.app.change_level = False
            if self.app.livello_corrente >= len(self.app.livelli) - 1:
                self.app.scena = FineGioco(self.app, self.player.points, True)
            else:
                self.app.livello_corrente += 1
                self.app.scena = Partita(
                    self.app,
                    punti_iniziali=self.player.points,
                    vite_iniziali=self.player.lives
                )

    def disegna(self, finestra: pygame.Surface) -> None:

        """Draw the maze, items, player, ghosts and the HUD."""
        finestra.fill((60, 60, 60))

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

        if self.player.direzione == "":
            frame_idx = 0
        else:
            frame_idx = (
                pygame.time.get_ticks() // 120) % len(
                    self.pacman_frames["left"])

        sprite_corrente = self.pacman_frames[self.player.direzione][frame_idx]

        pos_faccia_x = centro_player[0] - self.dimensione_coso // 2
        pos_faccia_y = centro_player[1] - self.dimensione_coso // 2
        finestra.blit(sprite_corrente, (pos_faccia_x, pos_faccia_y))

        for i, (ghost, (gx, gy)) in enumerate(zip(self.ghosts,
                                                  self.pos_ghosts)):
            fase = (pygame.time.get_ticks() // 150) % 3
            if fase == 0:
                angolo = -15
            elif fase == 1:
                angolo = 0
            elif fase == 2:
                angolo = 15

            img_ghost = self.ghost_images[i % len(self.ghost_images)]

            if ghost.dead:
                img_da_ruotare = img_ghost.copy()
                img_da_ruotare.fill((50, 255, 50, 200),
                                    special_flags=pygame.BLEND_RGBA_MULT)
            elif getattr(ghost, 'stupid', False):
                img_da_ruotare = img_ghost.copy()
                img_da_ruotare.fill((50, 50, 255, 200),
                                    special_flags=pygame.BLEND_RGBA_MULT)
            else:
                img_da_ruotare = img_ghost

            img_ruotata = pygame.transform.rotate(img_da_ruotare, angolo)

            centro_x = int(self.margine_x + gx * self.TILE + self.TILE // 2)
            centro_y = int(self.margine_y + gy * self.TILE + self.TILE // 2)

            rect_centrato = img_ruotata.get_rect(center=(centro_x, centro_y))

            finestra.blit(img_ruotata, rect_centrato)

        def disegna_numero(valore: int, x_pos: int, y_pos: int) -> None:
            """Draw a number using the digit images."""
            cur_x = x_pos
            for char_cifra in str(valore):
                img_cifra = self.app.img_numeri[int(char_cifra)]
                finestra.blit(img_cifra, (cur_x, y_pos))
                cur_x += img_cifra.get_width() + 4

        finestra.blit(self.app.img_punti, (self.app.hud_x, self.app.hud_y))
        pos_x_punti = self.app.hud_x + self.app.img_punti.get_width() + 10
        disegna_numero(self.player.points, pos_x_punti, self.app.hud_y)

        y_vite = self.app.hud_y + self.app.hud_spazio
        finestra.blit(self.app.img_vite, (self.app.hud_x, y_vite))
        pos_x_vite = self.app.hud_x + self.app.img_vite.get_width() + 10
        disegna_numero(self.player.lives, pos_x_vite, y_vite)

        y_tempo = self.margine_y - self.app.altezza_hud - 10
        x_tempo = self.margine_x

        disegna_numero(self.time_remining, x_tempo, y_tempo)

        livello = self.app.font.render("Livello ", True, "white")

        finestra.blit(livello, livello.get_rect(center=(80, 160)))
        disegna_numero(self.app.livello_corrente + 1, 140, 140)


class Menu(Scena):
    """Main menu scene."""

    def __init__(self, app: 'App') -> None:
        """Prepare the highlight surfaces and button positions."""
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
        self.tempo_ingresso = pygame.time.get_ticks()

    def eventi(self, ev: pygame.event.Event) -> None:
        """Move the selection and run the chosen entry."""
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_DOWN:
                self.selezione = (self.selezione + 1) % self.num_opzioni
            elif ev.key == pygame.K_UP:
                self.selezione = (self.selezione - 1) % self.num_opzioni
            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.selezione == 0:
                    self.app.scena = SelezionaGiocatore(self.app)
                elif self.selezione == 1:
                    self.app.scena = DisplayPunteggi(self.app)
                elif self.selezione == 2:
                    self.app.scena = Istruzioni(self.app)
                elif self.selezione == 3:
                    self.app.cheat_attiva = not self.app.cheat_attiva
                elif self.selezione == 4:
                    self.app.running = False

    def aggiorna(self, adesso: int) -> None:
        """Track the time spent in the menu."""
        self.app.tempo_menu = adesso - self.tempo_ingresso

    def disegna(self, finestra: pygame.Surface) -> None:
        """Draw the menu image and the selection highlights."""
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
    """Pause menu shown on top of the saved game."""

    def __init__(self, app: 'App') -> None:
        """Create the pause menu entries."""
        super().__init__(app)
        self.voci = ["RESUME THE GAME", "RETURN TO MAIN MENU"]
        self.selezione = 0

    def riprendi_gioco(self) -> None:
        """Resume the saved game, compensating its timers for the pause."""
        salvataggio = self.app.partita_salvata
        if salvataggio is not None:
            delta_pausa = pygame.time.get_ticks() - salvataggio.pausa_start
            salvataggio.start_time += delta_pausa
            salvataggio.ultimo_move += delta_pausa
            salvataggio.ultimo_move_ghost += delta_pausa
            self.app.scena = salvataggio

    def eventi(self, ev: pygame.event.Event) -> None:
        """Navigate the pause menu."""
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_DOWN:
                self.selezione = (self.selezione + 1) % 2
            elif ev.key == pygame.K_UP:
                self.selezione = (self.selezione - 1) % 2
            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.selezione == 0:
                    self.riprendi_gioco()
                elif self.selezione == 1:
                    self.app.partita_salvata = None
                    self.app.livello_corrente = 0
                    self.app.scena = Menu(self.app)
            elif ev.key == pygame.K_ESCAPE:
                self.riprendi_gioco()

    def disegna(self, finestra: pygame.Surface) -> None:
        """Draw the frozen game, dimmed, with the menu entries."""
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


class FineGioco(Scena):
    """Victory or defeat screen shown before the name entry."""

    def __init__(self, app: 'App', punti: int, vittoria: bool) -> None:
        """Store the result of the game.

        Args:
            app: The main application.
            punti: Final score.
            vittoria: True if the player won, False otherwise.
        """
        super().__init__(app)
        self.punti = punti
        self.vittoria = vittoria
        self.tempo_ingresso = pygame.time.get_ticks()

    def eventi(self, ev: pygame.event.Event) -> None:

        """Go to the name entry on ENTER or SPACE."""
        if pygame.time.get_ticks() - self.tempo_ingresso < 700:
            return
        if ev.type == pygame.KEYDOWN and ev.key in (
                pygame.K_RETURN, pygame.K_SPACE):
            self.app.scena = InserisciNome(self.app, self.punti)

    def disegna(self, finestra: pygame.Surface) -> None:
        """Draw the result message, the score and the prompt."""
        finestra.fill((0, 0, 0))
        larg, alt = finestra.get_size()

        if self.vittoria:
            titolo_testo = "HAI VINTO!"
            colore = (0, 255, 0)
        else:
            titolo_testo = "HAI PERSO!"
            colore = (255, 0, 0)

        font_grande = pygame.font.Font(None, 160)
        titolo = font_grande.render(titolo_testo, True, colore)
        finestra.blit(titolo, titolo.get_rect(center=(larg // 2, alt // 3)))

        punteggio = self.app.font.render(
            f"SCORE: {self.punti}", True, (255, 255, 0))
        finestra.blit(punteggio, punteggio.get_rect(
            center=(larg // 2, alt // 2)))

        invito = self.app.font.render(
            "PREMI INVIO PER CONTINUARE", True, (255, 255, 255))
        finestra.blit(invito, invito.get_rect(
            center=(larg // 2, alt // 2 + 120)))


class InserisciNome(Scena):
    """Scene to type the player name and save the score."""

    def __init__(self, app: 'App', punti: int) -> None:
        """Start with an empty name.

        Args:
            app: The main application.
            punti: Final score to save.
        """
        super().__init__(app)
        self.punti = punti
        self.nome = ""

    def eventi(self, ev: pygame.event.Event) -> None:
        """Edit the name (max 10 alphanumeric chars), save it on ENTER."""
        if self.app.cheat_attiva:
            return
        self.app.livello_corrente = 0
        if ev.type != pygame.KEYDOWN:
            return
        if ev.key == pygame.K_RETURN:
            """chiamo funzione .add()"""
            self.app.highscores.add(self.nome, self.punti)
            self.app.scena = Menu(self.app)
        elif ev.key == pygame.K_BACKSPACE:
            self.nome = self.nome[:-1]
        elif len(self.nome) < 10 and ev.unicode.isascii() \
                and (ev.unicode.isalnum() or ev.unicode == " "):
            self.nome += ev.unicode

    def disegna(self, finestra: pygame.Surface) -> None:
        """Draw the score and the name being typed."""
        if self.app.cheat_attiva:
            self.app.livello_corrente = 0
            self.app.scena = Menu(self.app)
        finestra.fill((0, 0, 0))
        righe = [f"SCORE: {self.punti}", "ENTER YOUR NAME:",
                 self.nome + "_"]
        for i, r in enumerate(righe):
            t = self.app.font.render(r, True, (255, 255, 0))
            finestra.blit(t, t.get_rect(
                center=(finestra.get_width() // 2, 300 + 80 * i)))


class DisplayPunteggi(Scena):
    """Scene showing the top highscores."""

    def eventi(self, ev: pygame.event.Event) -> None:
        """Go back to the menu on ESC, ENTER or SPACE."""
        if ev.type == pygame.KEYDOWN and ev.key in (
                pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
            self.app.scena = Menu(self.app)

    def disegna(self, finestra: pygame.Surface) -> None:
        """Draw the highscore list."""
        finestra.fill((0, 0, 0))
        centro = finestra.get_width() // 2
        titolo = self.app.font.render("HIGHSCORES", True, (255, 255, 0))
        finestra.blit(titolo, titolo.get_rect(center=(centro, 100)))

        top = self.app.highscores.get_top()
        if not top:
            t = self.app.font.render("Gioca per vedere la classifica", True,
                                     (255, 255, 255))
            finestra.blit(t, t.get_rect(center=(centro, 250)))
        for i, (nome, punti) in enumerate(top):
            t = self.app.font.render(
                f"{i + 1}. {nome} - {punti}", True, (255, 255, 255))
            finestra.blit(t, t.get_rect(center=(centro, 200 + 60 * i)))


class Istruzioni(Scena):
    """Scene showing the game instructions."""

    def __init__(self, app: 'App') -> None:
        """Define the lines of text to show."""
        super().__init__(app)
        self.righe = [
            "Istruzioni",
            "",
            "Muoversi",
            "Tasti freccia o WASD: muoversi",
            "ESC: pausa",
            "",
            "",
            "Mangia gum",
            "Mangia bubblegum",
            "Ghost tolgono una vita",
            "3 vite",
            "",
            "cheat mode:",
            "'n' per livello extra",
            "'m' per togliere e mettere attraversamento muri",
            "",
            "ESC per Menu principale"
        ]

    def eventi(self, ev: pygame.event.Event) -> None:
        """Go back to the menu on ESC, ENTER or SPACE."""
        if ev.type == pygame.KEYDOWN and ev.key in (
                pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
            self.app.scena = Menu(self.app)

    def disegna(self, finestra: pygame.Surface) -> None:
        """Draw the instructions directly on the background."""
        finestra.fill((0, 0, 0))  # Sfondo nero
        larg, alt = finestra.get_size()

        spazio_righe = 40
        altezza_totale = len(self.righe) * spazio_righe
        y_iniziale = (alt - altezza_totale) // 2

        for i, riga in enumerate(self.righe):
            t = self.app.font.render(riga, True, (255, 255, 255))
            finestra.blit(t, t.get_rect(
                center=(larg // 2, y_iniziale + spazio_righe * i)))


class SelezionaGiocatore(Scena):
    """Character selection scene before a new game."""

    def __init__(self, app: 'App') -> None:
        """Start with the first character selected."""
        super().__init__(app)
        # True per Lore, False per Andrea
        self.scelta_lore = True

    def eventi(self, ev: pygame.event.Event) -> None:
        """Choose with left/right, confirm with ENTER, go back with ESC."""
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_LEFT, pygame.K_a):
                self.scelta_lore = True
            elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                self.scelta_lore = False
            elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.app.player_img = self.scelta_lore
                self.app.livello_corrente = 0
                self.app.scena = Partita(self.app)
            elif ev.key == pygame.K_ESCAPE:
                self.app.scena = Menu(self.app)

    def disegna(self, finestra: pygame.Surface) -> None:
        """Draw the two characters and highlight the selected one."""
        finestra.fill((0, 0, 0))
        larg, alt = finestra.get_size()

        margine = 100
        rect_bordo = pygame.Rect(
            margine, margine, larg - margine * 2, alt - margine * 2)
        pygame.draw.rect(finestra, (255, 255, 0), rect_bordo, width=8,
                         border_radius=20)

        titolo = self.app.font.render("SELEZIONA GIOCATORE", True, (255, 255,
                                                                    255))
        finestra.blit(titolo, titolo.get_rect(center=(larg // 2,
                                                      margine + 60)))

        centro_y = alt // 2
        x_lore = larg // 3
        x_andrea = (larg // 3) * 2

        rect_lciardo = self.app.img_selezione_lciaro.get_rect(
            center=(x_lore, centro_y - 50))
        finestra.blit(self.app.img_selezione_lciaro, rect_lciardo)

        rect_acentron = self.app.img_selezione_acentron.get_rect(
            center=(x_andrea, centro_y - 50))
        finestra.blit(self.app.img_selezione_acentron, rect_acentron)

        colore_lore = (255, 255, 0) if self.scelta_lore else (100, 100, 100)
        colore_andrea = (255, 255, 0) if not self.scelta_lore else (100, 100,
                                                                    100)

        t_lore = self.app.font.render("LCIARDO", True, colore_lore)
        t_andrea = self.app.font.render("ACENTRON", True, colore_andrea)

        finestra.blit(t_lore, t_lore.get_rect(center=(x_lore, centro_y + 250)))
        finestra.blit(t_andrea, t_andrea.get_rect(center=(x_andrea,
                                                          centro_y + 250)))
