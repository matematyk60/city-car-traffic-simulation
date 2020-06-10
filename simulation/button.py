import pygame

class Button:
    def __init__(self, x, y, width, height, text, clickable, action = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.clickable = clickable
        self.action = action

    def draw(self, surface):
        pygame.draw.rect(surface, (0,0,255), (self.x, self.y, self.width, self.height))
        font3 = pygame.font.SysFont('dejavusans', 20, True)
        buttonText = font3.render(self.text, 1, (255, 255, 255))
        textRect = buttonText.get_rect()
        textRect.center = ((self.x+(self.width/2)), (self.y+(self.height/2)))
        surface.blit(buttonText, textRect)

    def check_collision(self, position):
        (x, y) = position
        if self.x + self.width > x > self.x and self.y + self.height > y > self.y:
            return True
        else:
            return False

    def update_text(self, text):
        self.text = text