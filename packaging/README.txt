PAC-MAN - Ghosts! More ghosts!
==============================

Run the game
------------
Linux:  ./pac-man   (from this folder, or double click / itch.io app "Launch")
The game opens fullscreen. Use "Exit" in the main menu to close it.

Do not move the executable out of this folder: it needs the "_internal"
folder and config.json next to it.


Controls
--------
Main menu          UP / DOWN to select, ENTER or SPACE to confirm
In game            Arrow keys or W A S D to move
                   ESC to pause (resume, or return to the main menu)
Name entry         type the name (max 10 letters/digits/spaces),
                   BACKSPACE to delete, ENTER to save the score
Other screens      ESC, ENTER or SPACE to go back

Rules
-----
- Eat all the pacgums to clear the level; super-pacgums (big dots) make
  the ghosts edible for a short time.
- A ghost touching you costs one life; with no lives left the game is over.
- Clear the level before the timer reaches 0.
- There are 10 levels; speed increases at every level.
- At the end of the game (win or lose) you can save your name in the
  top 10 highscores.

Cheat mode (for evaluation)
---------------------------
Main menu > "Cheat" entry (4th) toggles it (highlighted in red when on).
In game:  N = skip to next level,  M = walk through walls on/off
          (ghosts do not hurt you while walls are ignored).


Options / configuration
-----------------------
Edit config.json (next to the executable). Lines starting with # are
comments. Invalid values are ignored and replaced by the default.

  highscore_filename        file where the top 10 is saved   (highscores.json)
  width, height             maze size, 5-200                 (14, 14)
  lives                     starting lives, 1-99             (3)
  points_per_pacgum         score of a pacgum                (10)
  points_per_super_pacgum   score of a super-pacgum          (50)
  points_per_ghost          score for eating a ghost         (200)
  seed                      seed of the first level          (42)
  level_max_time            seconds available per level      (90)

You can also pass another config file:  ./pac-man other_config.json

highscores.json is created next to the executable the first time a score
is saved. Delete it to reset the highscores.
