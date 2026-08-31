import pygame, math, asyncio, js
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
font = pygame.font.SysFont("Arial", 25)

#############################################

#Globals
text_being_edited = False 
text_buffer = ""
num_new_children = 3
grab_semaphor = True
#############################################

class Tree:
    handle_radius = 10
    child_line_offset = 40
    line_width = 2
    text_offset = 10
    interact_zone = 12**2 #needs to be squared to make distance calc easier 
    child_spawn_dist = 90

    def __init__(self):
        self.pos = (0,0)
        self.label = "Text"
        self.children = []
        self.shown = False
        self.grabbed = False
        self.parent = None
        self.index_from_parent = 0
        self.text_highlighted = False
        self.text_edit_mode = False
        self.relation_to_moving_parent = (0,0)
        self.buttons_shown = False
        self.isRoot = False

        self.button_vert_offset = 50
        self.button_horz_offset = 12

        self.add_button = Button()
        self.add_button.color = (0,255,0)
        self.add_button.label = "+"
        self.add_button.pos = (self.pos[0] - self.button_horz_offset, self.pos[1] + self.button_vert_offset)

        self.del_button = Button()
        self.del_button.color = (255,0,0)
        self.del_button.label = "x"
        self.del_button.pos = (self.pos[0] + self.button_horz_offset, self.pos[1] + self.button_vert_offset)


    def moveChildRec(self):
        self.pos = (mouse_x + self.relation_to_moving_parent[0], mouse_y + self.relation_to_moving_parent[1])
        for child in self.children:
            child.moveChildRec()

    def render(self):
        global text_buffer, grab_semaphor
        #render and move using handle 
        self.shown = (mouse_x - self.pos[0])**2 + (mouse_y - self.pos[1])**2 <= self.interact_zone
        if self.grabbed:
                    self.pos = (mouse_x, mouse_y)
                    for child in self.children:
                        child.moveChildRec()
                    if not left_click_down:
                        self.grabbed = False
                        grab_semaphor = True
        elif self.shown:
            pygame.draw.circle(screen, (255,0,0), self.pos, self.handle_radius)

        #render label text
        if self.text_edit_mode:
            self.label = text_buffer + "|"

        if not self.text_highlighted:
            text_surface = ui.font.render(self.label, True, (0,0,0))
        else:
            text_surface = ui.font.render(self.label, True, (0,0,255))
        text_rect = text_surface.get_rect()
        text_rect.centerx = self.pos[0]
        text_rect.y = self.pos[1] + self.text_offset
        screen.blit(text_surface, text_rect)

        self.text_highlighted = mouse_x >= text_rect.topleft[0] and mouse_x <= text_rect.topright[0] and mouse_y >= text_rect.topleft[1] and mouse_y <= text_rect.bottomleft[1]

        #render lines to child and child 
        for child in self.children:
            pygame.draw.line(screen, (0,0,0), (self.pos[0], self.pos[1] + self.child_line_offset), child.pos, width= self.line_width)
            child.render()

        #render buttons 
        midx = self.add_button.pos[0] + self.add_button.sidelength // 2 + self.button_horz_offset
        midy = self.add_button.pos[1]
        self.buttons_shown = abs(mouse_x - midx) <= 30 and abs(mouse_y - midy) <= 20
        self.add_button.pos = (self.pos[0] - self.button_horz_offset, self.pos[1] + self.button_vert_offset)
        self.del_button.pos = (self.pos[0] + self.button_horz_offset, self.pos[1] + self.button_vert_offset)
        if self.buttons_shown:
            self.add_button.render()
            if not self.isRoot:
                self.del_button.render()

    def addChild(self):
        global num_new_children

        #This code overrides the old "select children per click" system no one liked using but the global to do that is still there
        if num_new_children == 0:
            if len(self.children) == 0:
                num_new_children = 2
            else:
                num_new_children = 1

        spread_angle = math.pi / 2
        if num_new_children > 1:
            angle_increment = spread_angle / (num_new_children - 1)
            start_angle = math.pi/2 - (spread_angle / 2) 
        else:
            angle_increment = 0
            start_angle = math.pi/2
        for i in range(0,num_new_children):
            angle = start_angle + (i * angle_increment)
            child = Tree()
            child_x = self.pos[0] + self.child_spawn_dist * math.cos(angle)
            child_y = self.pos[1] + self.child_spawn_dist * math.sin(angle)
            child.pos = (child_x, child_y)
            self.children.append(child)
            child.parent = self
            child.index_from_parent = len(self.children) - 1

        num_new_children = 0

    def treeAddChild(self):
        if self.shown:
            self.addChild()
        else:
            for child in self.children:
                child.treeAddChild()

    def removeSelf(self):
        if self != root:
            self.parent.children.pop(self.index_from_parent)
            self.parent.decrementSiblingIndecies(self.index_from_parent)

    def treeRemoveSelf(self):
        if self.shown:
            self.removeSelf()
        else:
            for child in self.children:
                child.treeRemoveSelf()

    def decrementSiblingIndecies(self, deli):
        for child in self.children:
            if child.index_from_parent > deli:
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
        global grab_semaphor
        if self.shown and grab_semaphor:
            grab_semaphor = False
            self.grabbed = True
            self.setChildOffsets()
        else:
            for child in self.children:
                child.grab()

    def buttonInteract(self):
        if self.buttons_shown:
            if self.add_button.checkClick():
                self.addChild()
            if self.del_button.checkClick():
                self.removeSelf()
        else:
            for child in self.children:
                child.buttonInteract()

    def makeText(self):
        if self.parent != None:
            hasSibling =  not self.parent.children == [self]
        else:
            hasSibling = False
        out =  self.label.replace(" ", "-") 
        if self.children != []: #is leaf
            out += " "
            self.children.reverse()
            for child in self.children:
                out += child.makeText()
            self.children.reverse()
            return "[" + out + "]"
        else:
            if hasSibling:
                return "[" + out + "]"
            else:
                return out 

    def reset(self):
        self.label = "Text"
        self.children.clear()

    def export(self):
        text = self.makeText()
        output_el = js.document.getElementById("Output")
        if output_el:
            output_el.innerText = text
        

class UI:
    def __init__(self):
        self.fontsize = 25
        self.font = pygame.font.SysFont("Arial", self.fontsize) 

    def render(self):    
        #num_child_counter_text_surface = self.font.render(("Children Per Click: " + str(num_new_children)), True, (0,0,0))
        #num_child_counter_text_rect =  num_child_counter_text_surface.get_rect() 
        #num_child_counter_text_rect.bottomright = (WINDOW_WIDTH - self.fontsize/2, WINDOW_HEIGHT - self.fontsize/2)
        #screen.blit(num_child_counter_text_surface, num_child_counter_text_rect) 
        pass

    def increaseChildPerClick(self, *args):
        global num_new_children
        num_new_children += 1

    def decreaseChildPerClick(self, *args):
            global num_new_children 
            if num_new_children > 1:
                num_new_children -= 1

class Button:
    font = pygame.font.SysFont("Arial", 20) 

    def __init__(self):
        self.pos = (0,0) #(centered)
        self.label = "None"
        self.color = (255,255,0)
        self.sidelength = 20
        self.label_color = (0,0,0)

    def render(self):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.pos[0] - self.sidelength //2, self.pos[1] - self.sidelength //2, self.sidelength, self.sidelength))
        label_surface = self.font.render(str(self.label), True, self.label_color)
        label_rect =  label_surface.get_rect()
        label_rect.centerx = self.pos[0]
        label_rect.centery = self.pos[1] - 3
        screen.blit(label_surface, label_rect) 

    def checkClick(self):
        hor = (mouse_x >= self.pos[0] - self.sidelength //2) and (mouse_x <= self.pos[0] + self.sidelength //2)
        ver = (mouse_y >= self.pos[1] - self.sidelength //2) and (mouse_y <= self.pos[1] + self.sidelength //2)
        return (hor and ver)


#Creating Initial Tree
root = Tree()
root.pos = (WINDOW_WIDTH//2, 50)
root.isRoot = True
ui = UI()

##making the wug sentence :)
num_new_children = 0
root.label = "S"
num_new_children = 2
root.addChild()
vp, np = root.children[0], root.children[1]
np.label = "NP"
vp.label = "VP"
vp.addChild()
np2, v = vp.children[0], vp.children[1]
v.label = "V"
np2.label = "NP"
num_new_children = 1
np.addChild()
np.children[0].label = "This"
num_new_children = 1
v.addChild()
v.children[0].label = "is"
num_new_children = 1
np2.addChild()
np2.children[0].label = "a wug"
num_new_children = 2

print(root.makeText())

def render():
    screen.fill((255,255,255))
    root.render()
    ui.render()
    pygame.display.flip()
   
############################################
#JS Globals 
js.window.increaseChildPerClick = ui.increaseChildPerClick
js.window.decreaseChildPerClick = ui.decreaseChildPerClick
js.window.reset = root.reset
js.window.export = root.export


#############################################
#Event Loop
async def main():
    global mouse_x, mouse_y, left_click_down, text_buffer, text_being_edited
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
                    root.treeAddChild()
                if event.key == pygame.K_w:
                    root.treeRemoveSelf()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    root.buttonInteract()
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
        await asyncio.sleep(0)

#############################################

asyncio.run(main())