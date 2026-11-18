*This project has been created as part of the 42 curriculum by lciardo, acentron.*

# <span style="color:green;">DESCRIPTION</span>

A playable Pac-Man clone written in Python with Pygame.
The goal is to eat all the pacgums in each of the 10+ levels while avoiding 4 ghosts.
Super-pacgums make the ghosts edible for a short time.
Mazes come from A-Maze-ing package, and a JSON config file sets the game parameters.
Features: main menu, highscores, pause menu and a cheat mode for peer review.

# <span style="color:green;">INSTRUCTIONS</span>

Install dependencies: make install

Run the game: make run

Debug: make debug

Clean: make clean

# <span style="color:green;">RESOURCES</span>

Peer to peer, YouTube tutorials and guides.
AI was used to create this README.md and to clarify concepts and use of functions when other resources were not enough or not available.

# <span style="color:green;">CONFIGURATION</span>

The game takes one JSON file as argument. Lines starting with # are comments and are ignored.
Keys: highscore_filename, lives (3), seed (42), level_max_time (200), width and height (14).
Points: points_per_pacgum (10), points_per_super_pacgum (50), points_per_ghost (200).
Values are validated with Pydantic: invalid ones are replaced by defaults with a message, and unknown keys are ignored.

# <span style="color:green;">HIGHSCORES</span>

The top 10 scores are stored in a JSON file, loaded at start and saved after each game.
Entries are validated with Pydantic (name max 10 characters, letters, digits and spaces only; score a non-negative integer).
A missing, corrupted or invalid file never crashes the game. We chose JSON because it is simple.

# <span style="color:green;">MAZE GENERATION</span>

We use the assigned mazegenerator package as-is.
Level 1 uses the seed from the config (42), the other 9 levels use random seeds.
The wall bits of generator.maze (1=north, 2=east, 4=south, 8=west) are decoded by Maze and Cell in src/models.py.
Each walkable cell gets a pacgum, the player starts at the center, and ghosts and super-pacgums go in the 4 corners (nearest walkable cell, found with a BFS).

# <span style="color:green;">IMPLEMENTATION</span>

Pygame game with 10 levels (the first with the config seed, the others random), a timer per level, pause, and score and lives kept between levels.
Ghosts have 4 behaviors (random, greedy chase, BFS chase mixed with random moves, BFS chase when far). When edible they move randomly, and when eaten they return home with BFS and respawn.
Config and highscores are validated with Pydantic, and the code uses type hints and docstrings and passes flake8 and mypy.
Cheat mode (toggled in the main menu): "N" skips the level and "M" toggles invincibility and walking through walls.

# <span style="color:green;">GENERAL SOFTWARE ARCHITECTURE</span>

pac-man.py is the entry point: it loads the config, creates the App and runs the main loop at 60 FPS.
src/core.py has App (window, assets, shared state) and the scenes (menu, game, pause, game over, name entry, highscores, instructions), each with eventi, aggiorna and disegna.
src/models.py has Maze, Cell, Gum and Bubblegum; src/player.py and src/ghost.py have the entities.
src/controllore.py applies the rules: collisions, edible ghosts, win and lose.
src/config.py and src/highscore.py handle the validated config and the top 10 file.

# <span style="color:green;">PROJECT MANAGEMENT</span>

We split the work in two: lciardo built the backend (game logic, ghosts, config, highscores) and acentron the frontend (Pygame scenes, menus, graphics).
We then merged our work and polished the project together, deciding things jointly.
All project management documents are in the [project_management/](project_management/) folder.