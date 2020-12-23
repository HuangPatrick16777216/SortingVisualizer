#  ##### BEGIN GPL LICENSE BLOCK #####
# 
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import random
import pygame

SCREEN = (1600, 900)
FPS = 60

BLACK = (0, 0, 0)
GRAY_DARK = (64, 64, 64)
GRAY = (128, 128, 128)
GRAY_LIGHT = (192, 192, 192)
WHITE = (255, 255, 255)

CHOICE_LIGHT = (255, 220, 150)
CHOICE_DARK = (200, 170, 120)


class Button:
    def __init__(self, loc, size, text):
        self.loc = loc
        self.size = size
        self.text = text
        self.text_loc = (loc[0] + (size[0]-text.get_width())//2, loc[1] + (size[1]-text.get_height())//2)

    def draw(self, window, events):
        color = (GRAY_DARK if self.clicked(events) else GRAY_LIGHT) if self.hovered() else WHITE
        pygame.draw.rect(window, color, self.loc+self.size)
        pygame.draw.rect(window, WHITE, self.loc+self.size, 2)
        window.blit(self.text, self.text_loc)

    def hovered(self):
        loc = self.loc
        size = self.size
        mouse_pos = pygame.mouse.get_pos()
        if loc[0] <= mouse_pos[0] <= loc[0]+size[0] and loc[1] <= mouse_pos[1] <= loc[1]+size[1]:
            return True
        return False

    def clicked(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered():
                return True
        return False


class Slider:
    def __init__(self, loc, size, circle_size, font, label, default_val, val_range):
        self.loc = loc
        self.size = size
        self.circle_size = circle_size
        self.font = font
        self.label = label
        self.value = default_val
        self.range = val_range
        self.val_dist = val_range[1] - val_range[0]
        self.dragging = False

    def draw(self, window, events):
        loc = self.loc
        size = self.size

        text = self.font.render(f"{self.label}: {self.value}", 1, WHITE)
        text_loc = (loc[0] + (self.size[0]-text.get_width())//2, self.loc[1]+self.size[1]+7)
        pygame.draw.rect(window, GRAY, loc+size)
        pygame.draw.rect(window, WHITE, loc+size, 1)
        pygame.draw.circle(window, WHITE, (self.value_to_loc(), self.loc[1]+self.size[1]//2), self.circle_size)
        window.blit(text, text_loc)

        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if loc[0] <= mouse_pos[0] <= loc[0]+size[0] and loc[1] <= mouse_pos[1] <= loc[1]+size[1]:
                    self.dragging = True

        clicked = pygame.mouse.get_pressed()[0]
        if not clicked:
            self.dragging = False
        
        if clicked and self.dragging:
            self.value = self.loc_to_value(mouse_pos[0])

    def loc_to_value(self, loc):
        fac = max(min((loc-self.loc[0]) / self.size[0], 1), 0)
        return int(fac*self.val_dist + self.range[0])

    def value_to_loc(self):
        fac = (self.value-self.range[0]) / self.val_dist
        return fac * self.size[0] + self.loc[0]


class Objects:
    def __init__(self, num_objs):
        self.gen_objs(num_objs)

    def gen_objs(self, num_objs):
        self.objs = []
        for i in range(num_objs):
            self.objs.append(i / num_objs)

    def shuffle(self):
        random.shuffle(self.objs)

    def draw(self, window, mode):
        num_objs = len(self.objs)
        if mode == "BARS":
            border = 1 if num_objs < 300 else 0
            x_size = 1500 / num_objs - border
            for i, obj in enumerate(self.objs):
                x_loc = 1500 * i / num_objs + 50
                y_size = 600 * obj + 50
                y_loc = 900 - y_size
                pygame.draw.rect(window, WHITE, (x_loc, y_loc, x_size, y_size+5))

        elif mode == "SCATTERPLOT":
            x_size = 1500 / num_objs
            for i, obj in enumerate(self.objs):
                x_loc = 1500 * i / num_objs + 50
                y_size = 600 * obj + 50
                y_loc = 900 - y_size
                pygame.draw.rect(window, WHITE, (x_loc, y_loc, x_size, 5))


class SortChooser:
    scroll_speed = 10
    choice_width = 20
    choices = ("asdf", "bsdf", "csdf", "dsdf", "esdf", "fsdf", "gsdf")
    
    def __init__(self, loc, size, font):
        self.loc = loc
        self.size = size
        self.font = font
        self.offset = 0

    def draw(self, window, events):
        loc = self.loc
        size = self.size
        surface = pygame.Surface(self.size)

        for i, choice in enumerate(self.choices):
            y_loc = self.choice_width*i + self.offset
            color = CHOICE_LIGHT if i%2 == 0 else CHOICE_DARK

            pygame.draw.rect(surface, color, (0, y_loc, size[0], self.choice_width))
            text = self.font.render(choice, 1, BLACK)
            text_loc = ((size[0]-text.get_width()) // 2, y_loc + (self.choice_width-text.get_height())//2)
            surface.blit(text, text_loc)

        window.blit(surface, self.loc)
        pygame.draw.rect(window, WHITE, self.loc+self.size, 2)

        mouse_pos = pygame.mouse.get_pos()
        if loc[0] <= mouse_pos[0] <= loc[0]+size[0] and loc[1] <= mouse_pos[1] <= loc[1]+size[1]:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        self.offset += self.scroll_speed
                    elif event.button == 5:
                        self.offset -= self.scroll_speed

        self.offset = min(self.offset, 0)
        self.offset = max(self.offset, size[1] - len(self.choices)*self.choice_width)


def main():
    pygame.init()
    pygame.display.set_caption("Sorting Visualizer - Version 2")
    pygame.display.set_icon(pygame.image.load("icon.png"))
    WINDOW = pygame.display.set_mode(SCREEN)

    clock = pygame.time.Clock()
    objects = Objects(100)
    asdf = SortChooser((100, 100), (150, 110), pygame.font.SysFont("arial", 14))
    while True:
        clock.tick(FPS)
        pygame.display.update()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        WINDOW.fill(BLACK)
        objects.draw(WINDOW, "SCATTERPLOT")
        asdf.draw(WINDOW, events)


main()