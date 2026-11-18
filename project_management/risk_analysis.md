# Project Management

## Risks and mitigation
| Risk | Mitigation |
|------|------------|
| Pygame is not MLX | Use only basic functions (images, shapes, text, key events) |
| Maze package is not ours and cannot be changed | The loader adapts to its interface; errors are caught |
| Crash on bad config or highscore file | Pydantic validation, defaults and clean messages |
| Bigger mazes do not fit the screen | Compute the tile size from the maze size |
| Ghost AI too hard or too easy | Four behaviors and speed that grows per level |
