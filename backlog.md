# Backlog

Each row is meant to become a **GitHub Issue** (title = "Task", body = "Done when").
Priority: P0 blocking, P1 mandatory, P2 nice to have.

## Shared

| ID | Task | Owner | Priority | Done when |
|---|---|---|---|---|
| S-01 | Repo setup: folder structure, `.gitignore`, Makefile (`install`, `run`, `debug`, `clean`, `lint`, `lint-strict`) | A + B | P0 | Every make rule runs on the empty skeleton |
| S-02 | flake8 and mypy configuration, pre-push habit | A + B | P0 | `make lint` passes |
| S-03 | Architecture and interface contract (`GameState`, main classes, module layout) | A + B | P0 | Diagram and short doc committed, both agree |
| S-04 | Study the assigned A-Maze-ing package (install, API, output format, `PERFECT=False`) | A + B | P0 | Notes written, small example script generates a maze |
| S-05 | Initial project management docs (this folder), board, labels | A + B | P0 | Board and issues created, documents committed |
| S-06 | Integration sessions at the end of each phase | A + B | P1 | Game launched together, issues found are logged |
| S-07 | Acceptance test plan and bug log (`test_plan.md`) | A | P1 | Each mandatory feature has a test case and a result |
| S-08 | README (all required sections, in English, AI usage described) | A + B | P1 | Every section from the subject is present |
| S-09 | Defense rehearsal: explain each other's modules, small recode exercises | A + B | P1 | Each person explained the other's module without help |

## Person A - Game engine

| ID | Task | Priority | Done when |
|---|---|---|---|
| A-01 | Maze adapter around the assigned A-Maze-ing package (fixed seed for level 1, random after) | P0 | Adapter returns a grid of walls/corridors for any level number |
| A-02 | Adapter error handling and post-processing (connectivity check, scaling if needed) | P1 | Generator failure shows a clean message, no traceback |
| A-03 | Level model: grid, pacgums, 4 super-pacgums in the corners, 4 ghost spawns, player start in the middle | P0 | Level object exposes all elements, remaining pacgum count is correct |
| A-04 | Player movement in 4 directions with wall collision | P0 | Player never enters a wall, moves smoothly |
| A-05 | Lives, contact with ghost, respawn in the middle, game over | P0 | 3 lives, losing all of them triggers game over |
| A-06 | Ghost base movement (autonomous, corridors only) | P0 | Ghosts move without crossing walls |
| A-07 | Ghost chase behaviour (BFS or distance based) | P1 | Non-edible ghosts follow the player |
| A-08 | Edible mode: flee, timer, eaten ghost, respawn in its corner after a delay | P1 | After a super-pacgum ghosts run away, can be eaten, come back later |
| A-09 | Scoring: pacgum (X), super-pacgum (Y), ghost (Z), score never decreases | P0 | Values come from the config |
| A-10 | Level progression: at least 10 levels, level timer, keep score and lives | P1 | Completing a level loads the next one |
| A-11 | Win/lose conditions and pause/resume logic | P1 | Level won when all pacgums are eaten, game won after last level |
| A-12 | Cheat mode logic (invincibility, skip level, freeze ghosts, extra lives, speed) | P1 | Each cheat can be toggled and works |

## Person B - Application and UI

| ID | Task | Priority | Done when |
|---|---|---|---|
| B-01 | Entry point `pac-man.py` with exactly one argument and clean error messages | P0 | Missing file or wrong arguments show a clear message |
| B-02 | JSON parser with `#` comments (optionally `//`, `/* */`) | P0 | Commented file loads correctly |
| B-03 | Config validation: defaults, clamping, unknown keys ignored, log messages | P0 | Faulty config never crashes the game |
| B-04 | Highscore storage: load at start, save at end, robust to missing/corrupted file | P0 | Deleting or breaking the file does not crash |
| B-05 | Highscore rules: name max 10 chars alphanumeric + spaces, non-negative score, top 10 | P1 | Invalid names/scores are rejected or sanitised |
| B-06 | Window and game loop with the graphics library | P0 | Window opens, loop runs at stable speed, closes cleanly |
| B-07 | Rendering of maze, pacgums, super-pacgums, player, ghosts (edible ghosts look different) | P0 | Everything from `GameState` is visible |
| B-08 | Keyboard input (arrows and WASD) | P0 | Player is controllable |
| B-09 | Main menu: Start Game, View Highscores, Instructions, Exit | P1 | All four entries work |
| B-10 | HUD: score, lives, level, remaining time | P1 | Always visible and updated |
| B-11 | Pause menu: Resume, Return to main menu | P1 | Game freezes and resumes correctly |
| B-12 | Game over and victory screens with final score and name entry | P1 | Name is saved in highscores, then back to menu |
| B-13 | Instructions screen and highscores screen | P1 | Controls, rules and top 10 are displayed |
| B-14 | Cheat mode UI: key bindings and on-screen indicator | P1 | Reviewer can see which cheats are active |
| B-15 | Packaging script (spec at repo root) | P1 | Package launches on a clean machine |
| B-16 | Publication on itch.io/Steam as unlisted build, in-package instructions | P1 | Game can be downloaded and played from the platform |

## Extras (only after all P0 and P1 are done)

| ID | Task | Owner | Priority |
|---|---|---|---|
| X-01 | Sounds and music | B | P2 |
| X-02 | Different behaviour per ghost (Blinky, Pinky, Inky, Clyde) | A | P2 |
| X-03 | Animations (mouth, ghost eyes) | B | P2 |
