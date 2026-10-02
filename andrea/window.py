
import pygame

class Window:
    """Apre finestra di gioco e runna il loop"""

    def __init__(self, width: int, height: int, title: str) -> None:
        pygame.init()
        self.schermo = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.timer = pygame.time.Clock()
        self.running = True
        self.x = 400
        self.y = 300
        self.dx = 0
        self.dy = 0
        self.lato = 20
        self.velocita = 5

    def comandi(self) -> None:
        """Legge comandi tastiera e finestra"""

        for comando in pygame.event.get():
            if comando.type == pygame.QUIT:
                self.running = False
            elif comando.type == pygame.KEYDOWN:
                if comando.key == pygame.K_ESCAPE:
                    self.running = False
                elif comando.key in (pygame.K_UP, pygame.K_w):
                    self.dx, self.dy = 0, -1
                elif comando.key in (pygame.K_DOWN, pygame.K_s):
                    self.dx, self.dy = 0, 1
                elif comando.key in (pygame.K_LEFT, pygame.K_a):
                    self.dx, self.dy = -1, 0
                elif comando.key in (pygame.K_RIGHT, pygame.K_d):
                    self.dx, self.dy = 1, 0

    def disegna(self) -> None:
        """muovo coso, clear schermo e nuovo frame"""

        self.x += self.dx * self.velocita
        self.y += self.dy * self.velocita
        larghezza, altezza = self.schermo.get_size()
        self.x = max(0, min(self.x, larghezza - self.lato))
        self.y = max(0, min(self.y, altezza - self.lato))
        self.schermo.fill((0, 0, 0))
        pygame.draw.rect(
            self.schermo, (255, 192, 203), (self.x, self.y, self.lato, self.lato)
            )
        pygame.display.flip()

    def avvia(self) -> None:
        """Main loop, comandi, disegnini gay e speed fissa"""

        while self.running:
            self.comandi()
            self.disegna()
            self.timer.tick(60)
        pygame.quit()
