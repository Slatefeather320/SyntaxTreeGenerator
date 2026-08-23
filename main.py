import pygame, math

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
font = pygame.font.SysFont("Arial", 20)

#############################################

#Globals
text_being_edited = False 
text_buffer = ""
num_new_children = 3
#############################################

class Tree:
    handle_radius = 10
    child_line_offset = 35
    line_width = 2
    text_offset = 15
    interact_zone = 12**2 #needs to be squared to make distance calc easier 
    child_spawn_dist = 70

    def __init__(self):
        self.pos = (0,0)
        self.label = "Add Text"
        self.children = []
        self.shown = False
        self.grabbed = False
        self.parent = None
        self.index_from_parent = 0
        self.text_highlighted = False
        self.text_edit_mode = False
        self.relation_to_moving_parent = (0,0)

    def moveChildRec(self):
        self.pos = (mouse_x + self.relation_to_moving_parent[0], mouse_y + self.relation_to_moving_parent[1])
        for child in self.children:
            child.moveChildRec()

    def render(self):
        global text_buffer
        #render and move using handle 
        self.shown = (mouse_x - self.pos[0])**2 + (mouse_y - self.pos[1])**2 <= self.interact_zone
        if self.grabbed:
                    self.pos = (mouse_x, mouse_y)
                    for child in self.children:
                        child.moveChildRec()
                    if not left_click_down:
                        self.grabbed = False
        elif self.shown:
            pygame.draw.circle(screen, (255,0,0), self.pos, self.handle_radius)

        #render label text
        if self.text_edit_mode:
            self.label = text_buffer + "|"

        if not self.text_highlighted:
            text_surface = font.render(self.label, True, (0,0,0))
        else:
            text_surface = font.render(self.label, True, (0,0,255))
        text_rect = text_surface.get_rect()
        text_rect.centerx = self.pos[0]
        text_rect.y = self.pos[1] + self.text_offset
        screen.blit(text_surface, text_rect)

        self.text_highlighted = mouse_x >= text_rect.topleft[0] and mouse_x <= text_rect.topright[0] and mouse_y >= text_rect.topleft[1] and mouse_y <= text_rect.bottomleft[1]

        #render lines to child and child 
        for child in self.children:
            pygame.draw.line(screen, (0,0,0), (self.pos[0], self.pos[1] + self.child_line_offset), child.pos, width= self.line_width)
            child.render()

    def addChild(self):
        global num_new_children
        if self.shown:
            if num_new_children > 1:
                angle_increment = (math.pi/2)/(num_new_children - 1)
            else:
                angle_increment = math.pi/4
            for i in range(0,num_new_children):
                angle = math.pi/4 + i*angle_increment
                child = Tree()
                child_x = self.pos[0] + self.child_spawn_dist * math.cos(angle)
                child_y = self.pos[1] + self.child_spawn_dist * math.sin(angle)
                child.pos = (child_x, child_y)
                self.children.append(child)
                child.parent = self
                child.index_from_parent = len(self.children) - 1
        else:
            for child in self.children:
                child.addChild()

    def removeSelf(self):
        if self.shown and self != root:
            self.parent.children.pop(self.index_from_parent)
            self.parent.decrementSiblingIndecies()
        else:
            for child in self.children:
                child.removeSelf()

    def decrementSiblingIndecies(self):
        for child in self.children:
            child.index_from_parent -= 1

    def editText(self):
        global text_being_edited, text_buffer

        if self.text_edit_mode:
            self.text_edit_mode = False
            text_being_edited = False
            self.label = text_buffer
            if text_buffer == "":
                self.label = "---"
            text_buffer = ""
        else:
            if self.text_highlighted:
                self.text_edit_mode = True
                text_being_edited = True
            else:
                for child in self.children:
                    child.editText()

    def setChildOffsetsRec(self, moving_parent):
        self.relation_to_moving_parent = (self.pos[0] - moving_parent.pos[0], self.pos[1] - moving_parent.pos[1])
        for child in self.children:
            child.setChildOffsetsRec(moving_parent)

    def setChildOffsets(self):
        for child in self.children:
            child.setChildOffsetsRec(self)

    def grab(self):
        if self.shown:
            self.grabbed = True
            self.setChildOffsets()
        else:
            for child in self.children:
                child.grab()

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
            if text_being_edited:
                if event.key == pygame.K_BACKSPACE:
                    text_buffer = text_buffer[:-1]
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER or event.key == pygame.K_ESCAPE:
                    root.editText()
                else:
                    text_buffer += event.unicode 
            if event.key == pygame.K_q:
                root.addChild()
            if event.key == pygame.K_w:
                root.removeSelf()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                root.grab()
                root.editText()
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