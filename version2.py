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
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)


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


def main():
    pygame.init()
    pygame.display.set_caption("Sorting Visualizer - Version 2")
    pygame.display.set_icon(pygame.image.load("icon.png"))
    WINDOW = pygame.display.set_mode(SCREEN)

    clock = pygame.time.Clock()
    objects = Objects(100)
    objects.shuffle()
    while True:
        clock.tick(FPS)
        pygame.display.update()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        WINDOW.fill(BLACK)
        objects.draw(WINDOW, "BARS")


main()