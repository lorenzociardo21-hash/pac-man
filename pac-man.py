import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'


import sys  # noqa: E402
from pathlib import Path  # noqa: E402
import pygame  # noqa: E402
from src.core import App  # noqa: E402
from src.config import load_config  # noqa: E402


"""
allora questo e' il main praticamente funziona con app che ha sempre una scena
che puo essere menu partita impostazioni ecc,
per ougni scena che una parte piglia gli eventi, una che aggiorna,
e una che disegna,
cosi lo rendiamo modulare e non e una merda
"""

if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        # Packaged build (PyInstaller): work next to the executable, so that
        # config.json and highscores.json are found whatever the launch
        # directory is (double click, itch.io app, terminal...), and use
        # config.json by default when no argument is given.
        os.chdir(Path(sys.executable).resolve().parent)
        if len(sys.argv) == 1:
            sys.argv.append("config.json")

    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py config.json")
        sys.exit(1)

    try:
        config = load_config(sys.argv[1])
        app = App(config)
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
    except Exception as e:
        print(f"Errore:  {e}")
    except KeyboardInterrupt:
        pass

    pygame.quit()
