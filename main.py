import pygame

############################################
#Pygame Boilerplate Stuf
pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

clock = pygame.time.Clock()
FPS = 60
mouse_x, mouse_y = 0, 0
left_click_down = False

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Syntax Tree Generator")
font = pygame.font.SysFont("Arial", 12)
#############################################

class Tree:
    handle_radius = 10
    child_line_offset = 25
    line_width = 2
    text_offset = 10
    interact_zone = 12**2 #needs to be squared to make distance calc easier 
    child_spawn_dist = 70

    def __init__(self):
        self.pos = (0,0)
        self.label = "Not Set"
        self.children = []
        self.shown = False
        self.grabbed = False
        self.parent = None
        self.index_from_parent = 0

    def render(self):
        #render and move using handle 
        self.shown = (mouse_x - self.pos[0])**2 + (mouse_y - self.pos[1])**2 <= self.interact_zone
        if self.grabbed:
                    self.pos = (mouse_x, mouse_y)
                    if not left_click_down:
                        self.grabbed = False
        elif self.shown:
            pygame.draw.circle(screen, (255,0,0), self.pos, self.handle_radius)
            if left_click_down:
                self.grabbed = True

        #render label text
        text_surface = font.render(self.label, True, (0,0,0))
        text_rect = text_surface.get_rect()
        text_rect.centerx = self.pos[0]
        text_rect.y = self.pos[1] + self.text_offset
        screen.blit(text_surface, text_rect)

        #render lines to child and child 
        for child in self.children:
            pygame.draw.line(screen, (0,0,0), (self.pos[0], self.pos[1] + self.child_line_offset), child.pos, width= self.line_width)
            child.render()

    def addChild(self):
        if self.shown:
            child = Tree()
            child.pos = (self.pos[0], self.pos[1] + self.child_spawn_dist)
            self.children.append(child)
            child.parent = self
            child.index_from_parent = len(self.children) - 1
        else:
            for child in self.children:
                child.addChild()

    def removeSelf(self):
        if self.shown and self != root:
            self.parent.children.pop(self.index_from_parent)
        else:
            for child in self.children:
                child.removeSelf()

#Creating Initial Tree
root = Tree()
root.pos = (WINDOW_WIDTH//2, 50)

def render():
    screen.fill((255,255,255))
    root.render()
    pygame.display.flip()

#############################################
#Event Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                root.addChild()
            if event.key == pygame.K_w:
                root.removeSelf()
        if event.type == pygame.QUIT:
            running = False

    clock.tick(FPS)

    #mouse polling 
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()
    left_click_down = mouse_buttons[0]

    render()
#############################################

pygame.quit()