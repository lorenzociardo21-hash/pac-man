"""Visualizzatore da terminale per provare Player, Ghost e Controll.

Mettilo nella cartella che CONTIENE la cartella ``lorenzo`` (la stessa
dove sta test.py), poi lancia:

    python3 visualizza.py            # modalita' interattiva (curses)
    python3 visualizza.py --stampa   # stampa un solo frame e termina
    python3 visualizza.py --seed 7   # seed diverso dal 42

Comandi in modalita' interattiva:
    frecce / WASD  muovi il player (un passo per tasto)
    spazio         passa il turno (si muovono solo i fantasmi)
    p              modalita' automatica ON/OFF (il gioco va avanti da solo,
                   il player continua nell'ultima direzione scelta)
    r              ricomincia (stesso seed)
    n              nuovo labirinto casuale
    q              esci

Legenda:
    C player    G fantasma (4 colori)    . pacgum    O super-pacgum
    #  cella completamente chiusa        _ e |  muri
"""

import argparse
import curses
import inspect
import os
import random
import sys
import traceback
from dataclasses import dataclass
from typing import Any

from mazegenerator import MazeGenerator

from lorenzo.controllore import Controll
from lorenzo.ghost import Ghost
from lorenzo.models import Maze
from lorenzo.player import Player

SIZE: tuple[int, int] = (20, 21)
SEED: int = 42
VITE: int = 3
PUNTI_GUM: int = 10
PUNTI_BUBBLEGUM: int = 50
TICK_MS: int = 200

# (carattere, colore, sottolineato)
Tile = tuple[str, str, bool]

COLORI_CURSES: dict[str, int] = {
    "white": curses.COLOR_WHITE,
    "yellow": curses.COLOR_YELLOW,
    "red": curses.COLOR_RED,
    "green": curses.COLOR_GREEN,
    "cyan": curses.COLOR_CYAN,
    "magenta": curses.COLOR_MAGENTA,
}
INDICE_COLORI: dict[str, int] = {
    nome: i + 1 for i, nome in enumerate(COLORI_CURSES)
}
COLORI_ANSI: dict[str, str] = {
    "white": "37",
    "yellow": "33",
    "red": "31",
    "green": "32",
    "cyan": "36",
    "magenta": "35",
}
COLORI_FANTASMI: list[str] = ["red", "green", "cyan", "magenta"]

DIREZIONI_TASTI: dict[int, str] = {
    curses.KEY_UP: "up",
    curses.KEY_DOWN: "down",
    curses.KEY_LEFT: "left",
    curses.KEY_RIGHT: "right",
    ord("w"): "up",
    ord("W"): "up",
    ord("s"): "down",
    ord("S"): "down",
    ord("a"): "left",
    ord("A"): "left",
    ord("d"): "right",
    ord("D"): "right",
}


@dataclass
class Gioco:
    """Raccoglie tutti gli oggetti di una partita."""

    maze: Maze
    player: Player
    ghosts: list[Ghost]
    controllore: Controll
    messaggio: str = ""


def descrivi_errore(exc: BaseException) -> str:
    """Riassume un'eccezione indicando file e riga dove e' avvenuta."""
    frames = traceback.extract_tb(exc.__traceback__)
    dove = ""
    if frames:
        ultimo = frames[-1]
        dove = f" ({os.path.basename(ultimo.filename)}:{ultimo.lineno})"
    return f"{type(exc).__name__}: {exc}{dove}"


def nuovo_gioco(seed: int) -> Gioco:
    """Crea labirinto, player, fantasmi e controllore con le tue classi."""
    generatore = MazeGenerator(size=SIZE, perfect=False, seed=seed)
    maze = Maze(generatore.maze, PUNTI_GUM, PUNTI_BUBBLEGUM)
    player = Player(maze, VITE)
    ghosts = [Ghost(maze, pos) for pos in maze.ghost_spawns]
    return Gioco(maze, player, ghosts, Controll(maze, ghosts, player))


def dimensioni(maze: Maze) -> tuple[int, int]:
    """Ritorna (larghezza, altezza) del labirinto in celle."""
    larghezza = max(x for x, _ in maze.mappa) + 1
    altezza = max(y for _, y in maze.mappa) + 1
    return larghezza, altezza


# ---------------------------------------------------------------- disegno

def tile_cella(gioco: Gioco, x: int, y: int) -> Tile:
    """Decide cosa disegnare dentro la cella (x, y)."""
    cella = gioco.maze.mappa[(x, y)]
    if not cella.is_walkable():
        return ("#", "white", False)
    sotto = not cella.opensud
    if (gioco.player.x, gioco.player.y) == (x, y):
        return ("C", "yellow", sotto)
    for i, ghost in enumerate(gioco.ghosts):
        if (ghost.x, ghost.y) == (x, y):
            colore = COLORI_FANTASMI[i % len(COLORI_FANTASMI)]
            return ("G", colore, sotto)
    if cella.item is None:
        return (" ", "white", sotto)
    return ("O" if cella.item.is_super else ".", "white", sotto)


def costruisci_righe(gioco: Gioco) -> list[list[Tile]]:
    """Trasforma lo stato del gioco in una griglia di tile.

    Ogni cella occupa 2 caratteri: uno per il muro ovest ('|') e uno per
    il contenuto. Il muro sud e' mostrato sottolineando la cella.
    """
    mappa = gioco.maze.mappa
    larghezza, altezza = dimensioni(gioco.maze)
    righe: list[list[Tile]] = [[(" ", "white", True)] * (larghezza * 2 + 1)]
    for y in range(altezza):
        riga: list[Tile] = []
        for x in range(larghezza):
            cella = mappa[(x, y)]
            sotto = not cella.opensud
            sotto_sx = x > 0 and not mappa[(x - 1, y)].opensud
            muro = "|" if not cella.openwest else " "
            riga.append((muro, "white", sotto and (x == 0 or sotto_sx)))
            riga.append(tile_cella(gioco, x, y))
        ultima = mappa[(larghezza - 1, y)]
        muro_fine = "|" if not ultima.openest else " "
        riga.append((muro_fine, "white", not ultima.opensud))
        righe.append(riga)
    return righe


def controlla_coerenza(maze: Maze) -> list[str]:
    """Cerca muri incoerenti tra celle vicine (utile per debug)."""
    larghezza, altezza = dimensioni(maze)
    problemi: list[str] = []
    for y in range(altezza):
        for x in range(larghezza):
            cella = maze.mappa[(x, y)]
            if x + 1 < larghezza:
                if cella.openest != maze.mappa[(x + 1, y)].openwest:
                    problemi.append(f"muro est/ovest incoerente in ({x},{y})")
            if y + 1 < altezza:
                if cella.opensud != maze.mappa[(x, y + 1)].opennord:
                    problemi.append(f"muro nord/sud incoerente in ({x},{y})")
    return problemi


def righe_info(gioco: Gioco) -> list[str]:
    """Testo di stato mostrato sotto il labirinto."""
    maze, player, ctrl = gioco.maze, gioco.player, gioco.controllore
    gum_reali = sum(1 for c in maze.mappa.values() if c.item is not None)
    if not ctrl.show_must_go_on:
        stato = "GAME OVER"
    elif ctrl.you_win:
        stato = "VITTORIA!"
    else:
        stato = "in corso"
    coincide = "OK" if gum_reali == maze.total_gums else "<-- NON COINCIDONO"
    fantasmi = "  ".join(
        f"{i}=({g.x},{g.y})" for i, g in enumerate(gioco.ghosts)
    )
    info = [
        f"Punti: {player.points}   Vite: {player.lives}   Stato: {stato}",
        f"Gum (total_gums): {maze.total_gums}   "
        f"sulla mappa: {gum_reali}   {coincide}",
        f"Player: ({player.x},{player.y})   "
        f"direzione: {player.direzione or '-'}",
        f"Fantasmi: {fantasmi}",
    ]
    if not hasattr(Ghost, "move"):
        info.append("(Ghost.move() non esiste ancora: fantasmi fermi)")
    problemi = controlla_coerenza(maze)
    if problemi:
        info.append(f"ATTENZIONE {len(problemi)} muri incoerenti, "
                    f"es. {problemi[0]}")
    if gioco.messaggio:
        info.append(gioco.messaggio)
    return info


# ------------------------------------------------------------------ logica

def muovi_fantasma(ghost: Ghost, player: Player) -> None:
    """Fa muovere un fantasma, se ha gia' un metodo ``move``.

    Funziona sia con ``move(self)`` sia con ``move(self, player)``.
    Se cambi la firma del tuo metodo, adatta questa funzione.
    """
    movimento = getattr(ghost, "move", None)
    if movimento is None:
        return
    if len(inspect.signature(movimento).parameters) == 0:
        movimento()
    else:
        movimento(player)


def esegui_turno(gioco: Gioco, muovi_player: bool) -> None:
    """Un turno: player, controllo, fantasmi, controllo."""
    ctrl = gioco.controllore
    if not ctrl.show_must_go_on or ctrl.you_win:
        return
    vite_prima = gioco.player.lives
    punti_prima = gioco.player.points
    try:
        if muovi_player:
            gioco.player.move()
        ctrl.controlliamo()
        if ctrl.show_must_go_on and not ctrl.you_win:
            for ghost in gioco.ghosts:
                muovi_fantasma(ghost, gioco.player)
            ctrl.controlliamo()
    except Exception as exc:
        gioco.messaggio = "ERRORE " + descrivi_errore(exc)
        return
    messaggi: list[str] = []
    if gioco.player.lives < vite_prima:
        messaggi.append("Preso da un fantasma: vita persa, respawn al centro.")
    if gioco.player.points > punti_prima:
        messaggi.append(f"+{gioco.player.points - punti_prima} punti")
    gioco.messaggio = "  ".join(messaggi)


# --------------------------------------------------------------- terminale

def stampa(gioco: Gioco) -> None:
    """Stampa un singolo frame con colori ANSI."""
    for riga in costruisci_righe(gioco):
        pezzi: list[str] = []
        for char, colore, sottolineato in riga:
            codice = COLORI_ANSI[colore] + (";4" if sottolineato else "")
            pezzi.append(f"\033[{codice}m{char}\033[0m")
        print("".join(pezzi))
    print()
    for linea in righe_info(gioco):
        print(linea)


def scrivi(stdscr: Any, riga: int, col: int,
           testo: str, attr: int = 0) -> None:
    """addstr che ignora gli errori se il terminale e' troppo piccolo."""
    try:
        stdscr.addstr(riga, col, testo, attr)
    except curses.error:
        pass


def init_colori() -> None:
    """Inizializza le coppie di colori curses."""
    curses.start_color()
    curses.use_default_colors()
    for nome, colore in COLORI_CURSES.items():
        curses.init_pair(INDICE_COLORI[nome], colore, -1)


def disegna(stdscr: Any, gioco: Gioco, auto: bool) -> None:
    """Disegna labirinto, info e comandi."""
    stdscr.erase()
    righe = costruisci_righe(gioco)
    for r, riga in enumerate(righe):
        for c, (char, colore, sottolineato) in enumerate(riga):
            attr = curses.color_pair(INDICE_COLORI[colore])
            if sottolineato:
                attr |= curses.A_UNDERLINE
            if char in ("C", "G"):
                attr |= curses.A_BOLD
            scrivi(stdscr, r, c, char, attr)
    base = len(righe) + 1
    for i, testo in enumerate(righe_info(gioco)):
        scrivi(stdscr, base + i, 0, testo)
    modo = "AUTO" if auto else "a turni"
    comandi = (f"[{modo}] frecce/WASD muovi | spazio passa | p auto | "
               "r reset | n nuovo | q esci")
    scrivi(stdscr, base + 8, 0, comandi, curses.A_DIM)
    stdscr.refresh()


def ciclo(stdscr: Any, gioco: Gioco, seed: int) -> None:
    """Ciclo principale interattivo."""
    curses.curs_set(0)
    init_colori()
    auto = False
    while True:
        disegna(stdscr, gioco, auto)
        stdscr.timeout(TICK_MS if auto else -1)
        tasto = stdscr.getch()
        if tasto in (ord("q"), ord("Q")):
            break
        if tasto == -1:
            esegui_turno(gioco, muovi_player=True)
        elif tasto in DIREZIONI_TASTI:
            gioco.player.direzione = DIREZIONI_TASTI[tasto]
            if not auto:
                esegui_turno(gioco, muovi_player=True)
        elif tasto == ord(" "):
            esegui_turno(gioco, muovi_player=False)
        elif tasto in (ord("p"), ord("P")):
            auto = not auto
        elif tasto in (ord("r"), ord("R"), ord("n"), ord("N")):
            if tasto in (ord("n"), ord("N")):
                seed = random.randint(0, 10**6)
            try:
                gioco = nuovo_gioco(seed)
            except Exception as exc:
                gioco.messaggio = "ERRORE generatore: " + descrivi_errore(exc)


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Visualizzatore da terminale per Player/Ghost/Controll"
    )
    parser.add_argument("--stampa", action="store_true",
                        help="stampa un solo frame e termina")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    try:
        gioco = nuovo_gioco(args.seed)
    except Exception as exc:
        print(f"Errore nella creazione del gioco: {descrivi_errore(exc)}")
        sys.exit(1)
    if args.stampa:
        stampa(gioco)
    else:
        curses.wrapper(ciclo, gioco, args.seed)


if __name__ == "__main__":
    main()