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

    def __init__(self, config: Config) -> None:
        self.config = Config = config
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
        self.pacman_sprites: dict[str, list[pygame.Surface]] = {
            "left": raw_lore,
            "right": [
                pygame.transform.flip(img, True, False) for img in raw_lore],
            "up": [pygame.transform.rotate(img, 270) for img in raw_lore],
            "down": [pygame.transform.rotate(img, 90) for img in raw_lore],
            "": raw_lore
        }


class Partita(Scena):

    def __init__(self, app: 'App', punti_iniziali: int = 0,
                 vite_iniziali: int | None = None) -> None:
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

        # NOTA: Se vite_iniziali è passato (dai livelli successivi) usa quello,
        # altrimenti cfg.lives
        vite_effettive = (
            vite_iniziali if vite_iniziali is not None else cfg.lives)
        self.player: Player = Player(self.maze, vite_effettive)
        self.player.points = punti_iniziali

        if self.app.cheat_attiva:
            self.player.cheat = True
        else:
            self.player.cheat = False

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

        self.tiles = []
        for img in self.app.raw_tiles:
            img_scalata = pygame.transform.scale(img, (self.TILE, self.TILE))
            self.tiles.append(img_scalata)

        self.max_time: int = cfg.level_max_time
        self.start_time: int = pygame.time.get_ticks()
        self.time_remining: int = self.max_time
        self.pausa_start: int = 0

        self.pacman_frames: dict[str, list[pygame.Surface]] = {}
        for dir_key, lista_frame in self.app.pacman_sprites.items():
            self.pacman_frames[dir_key] = [
                pygame.transform.smoothscale(img, (self.dimensione_coso,
                                                   self.dimensione_coso))
                for img in lista_frame
            ]

    def eventi(self, ev: pygame.event.Event) -> None:
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
            elif ev.unicode == "n":
                if self.app.cheat_attiva:
                    self.app.change_level = True

    def magia(self, a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    def aggiorna(self, adesso: int) -> None:
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

        self.controll.controlliamo((self.px, self.py), self.pos_ghosts)
        if self.controll.hit:
            pygame.time.wait(1000)
            self.controll.riparti()
            self.last_coord_player = (self.player.x, self.player.y)
            self.last_coord_ghost = [(g.x, g.y) for g in self.ghosts]
            tick = pygame.time.get_ticks()
            self.ultimo_move = tick
            self.ultimo_move_ghost = tick

        if not self.controll.show_must_go_on:
            self.app.scena = InserisciNome(self.app, self.player.points)
            return

        if self.controll.you_win or self.app.change_level:
            self.app.change_level = False
            if self.app.livello_corrente >= len(self.app.livelli) - 1:
                self.app.scena = InserisciNome(self.app, self.player.points)
            else:
                self.app.livello_corrente += 1
                self.app.scena = Partita(
                    self.app,
                    punti_iniziali=self.player.points,
                    vite_iniziali=self.player.lives
                )

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

        def disegna_numero(valore: int, x_pos: int, y_pos: int) -> None:
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
        self.tempo_ingresso = pygame.time.get_ticks()

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
                    self.app.scena = DisplayPunteggi(self.app)
                elif self.selezione == 2:
                    self.app.scena = Istruzioni(self.app)
                elif self.selezione == 3:
                    self.app.cheat_attiva = not self.app.cheat_attiva
                elif self.selezione == 4:
                    self.app.running = False

    def aggiorna(self, adesso: int) -> None:
        self.app.tempo_menu = adesso - self.tempo_ingresso

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

    def riprendi_gioco(self) -> None:
        salvataggio = self.app.partita_salvata
        if salvataggio is not None:
            delta_pausa = pygame.time.get_ticks() - salvataggio.pausa_start
            salvataggio.start_time += delta_pausa
            salvataggio.ultimo_move += delta_pausa
            salvataggio.ultimo_move_ghost += delta_pausa
            self.app.scena = salvataggio

    def eventi(self, ev: pygame.event.Event) -> None:
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


class InserisciNome(Scena):

    def __init__(self, app: 'App', punti: int) -> None:
        super().__init__(app)
        self.punti = punti
        self.nome = ""

    def eventi(self, ev: pygame.event.Event) -> None:
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

    def eventi(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.KEYDOWN and ev.key in (
                pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
            self.app.scena = Menu(self.app)

    def disegna(self, finestra: pygame.Surface) -> None:
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

    def __init__(self, app: 'App') -> None:
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
            "ESC per Menu principale",
        ]

    def eventi(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.KEYDOWN and ev.key in (
                pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
            self.app.scena = Menu(self.app)

    def disegna(self, finestra: pygame.Surface) -> None:
        finestra.fill((0, 0, 0))
        larg, alt = finestra.get_size()

        # white square in the middle of the screen
        lato = 800
        quadrato = pygame.Rect(0, 0, lato, lato)
        quadrato.center = (larg // 2, alt // 2)
        pygame.draw.rect(finestra, (255, 255, 255), quadrato,
                         border_radius=20)

        # black text on top of it
        for i, riga in enumerate(self.righe):
            t = self.app.font.render(riga, True, (0, 0, 0))
            finestra.blit(t, t.get_rect(
                center=(larg // 2, quadrato.top + 60 + 50 * i)))
