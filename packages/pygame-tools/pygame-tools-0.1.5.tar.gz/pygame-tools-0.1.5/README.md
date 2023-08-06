# PyGame Tools

This is a package designed to make development in pygame easier my creating some classes that handle alot of the loop

## installation

`pip install pygame-tools`

The most important class `GameScreen` is a class that represents a 'screen' in the game and is meant to be inherited to be used.

```python
import pygame
from pygame_tools import GameScreen, Point

class Example(GameScreen):
    def __init__(self):
        pygame.init()
        real_size = Point(600, 600) # size of window itself
        size = real_size / 40 # 1 pixel for every 40
        super().__init__(pygame.display.set_mode(real_size), real_size, size)

    def update(self):
        pygame.draw.line(self.screen, (255, 255, 255), (0, self.window_size.y / 2), (self.window_size.x, self.window_size.y / 2))

example = Example()
example.run()
# This example shows a black screen with a white line through the center
```
