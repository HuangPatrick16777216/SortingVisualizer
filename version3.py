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

import os
import math
import time
import threading
import colorsys
import random
import pygame
from tkinter import Tk
from tkinter.filedialog import askopenfilename
pygame.init()
Tk().withdraw()

SCREEN = (1600, 900)
FPS = 60

FONT_SMALL = pygame.font.SysFont("arial", 12)
FONT_MED = pygame.font.SysFont("arial", 16)

BLACK = (0, 0, 0)
GRAY_DARK = (64, 64, 64)
GRAY = (128, 128, 128)
GRAY_LIGHT = (192, 192, 192)
WHITE = (255, 255, 255)

RED = (255, 150, 150)
GREEN = (150, 255, 150)
BLUE = (150, 150, 255)

CHOICE_LIGHT = (255, 220, 150)
CHOICE_DARK = (200, 170, 120)
CHOICE_SELECT = (190, 230, 180)


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
    slider_num_objs = Slider((1350, 50), (225, 10), 7, FONT_SMALL, "Amount", 50, (10, 500))
    button_gen_objs = Button((1400, 100), (125, 40), FONT_MED.render("Generate", 1, BLACK))
    button_random = Button((1400, 150), (125, 40), FONT_MED.render("Randomize", 1, BLACK))
    slider_speed = Slider((1350, 210), (225, 10), 7, FONT_SMALL, "Speed", 30, (10, 240))

    def __init__(self, num_objs):
        self.reset_stats()
        self.gen_objs(num_objs)

    def gen_objs(self, num_objs):
        self.objs = []
        self.colors = []
        for i in range(num_objs):
            self.objs.append(i / num_objs)
            self.colors.append(WHITE)

    def set_objs(self, objs):
        self.objs = objs[:]

    def shuffle(self):
        random.shuffle(self.objs)

    def reset_stats(self):
        self.stats_comp = 0
        self.stats_read = 0
        self.stats_write = 0

    def draw(self, window, events, mode, sorter, image):
        self.slider_num_objs.draw(window, events)
        self.button_gen_objs.draw(window, events)
        self.button_random.draw(window, events)
        self.slider_speed.draw(window, events)
        window.blit(FONT_MED.render(f"Accesses: {self.stats_read}", 1, WHITE), (1100, 50))
        window.blit(FONT_MED.render(f"Comparisons: {self.stats_comp}", 1, WHITE), (1100, 75))
        window.blit(FONT_MED.render(f"Writes: {self.stats_write}", 1, WHITE), (1100, 100))
        window.blit(FONT_MED.render(
            f"Est. Time: {int(0.0167*self.stats_write + 0.0145*self.stats_read + 0.0225*self.stats_comp) / 1000} ms",
            1, WHITE), (1100, 125))

        num_objs = len(self.objs)
        if mode == "BARS":
            border = 1 if num_objs < 200 else 0
            x_size = 1500 / num_objs - border
            for i, obj in enumerate(self.objs):
                x_loc = 1500 * i / num_objs + 50
                y_size = 500 * obj + 50
                y_loc = 900 - y_size
                pygame.draw.rect(window, self.colors[i], (x_loc, y_loc, x_size, y_size+5))

        elif mode == "SCATTERPLOT":
            x_size = 1500 / num_objs
            for i, obj in enumerate(self.objs):
                x_loc = 1500 * i / num_objs + 50
                y_size = 500 * obj + 50
                y_loc = 900 - y_size
                pygame.draw.rect(window, self.colors[i], (x_loc, y_loc, x_size, 5))

        elif mode == "BW":
            border = 1 if num_objs < 200 else 0
            x_size = 1500 / num_objs
            for i, obj in enumerate(self.objs):
                x_loc = 1500 * i / num_objs + 50
                pygame.draw.rect(window, (255*obj,)*3, (x_loc, 350, x_size, 550))
                if self.colors[i] != WHITE:
                    pygame.draw.rect(window, self.colors[i], (x_loc, 350, x_size, 550), border+1)

        elif mode == "COLOR":
            border = 1 if num_objs < 200 else 0
            x_size = 1500 / num_objs
            for i, obj in enumerate(self.objs):
                x_loc = 1500 * i / num_objs + 50
                color = [255*x for x in colorsys.hsv_to_rgb(obj, 0.8, 0.8)]
                pygame.draw.rect(window, color, (x_loc, 350, x_size, 550))
                if self.colors[i] != WHITE:
                    pygame.draw.rect(window, self.colors[i], (x_loc, 350, x_size, 550), border+1)

        elif mode == "PIE":
            thickness = 2 if num_objs < 200 else 1
            for i, obj in enumerate(self.objs):
                angle = math.pi * 2 / num_objs * i
                length = obj * 250 + 50
                x_loc, y_loc = math.cos(angle) * length, math.sin(angle) * length
                pygame.draw.line(window, self.colors[i], (800, 600), (800+x_loc, 600+y_loc), thickness)

        elif mode == "PIESCATTER":
            thickness = 2 if num_objs < 200 else 1
            for i, obj in enumerate(self.objs):
                angle = math.pi * 2 / num_objs * i
                length = obj * 250 + 50
                x_loc, y_loc = math.cos(angle) * (length-5), math.sin(angle) * (length-5)
                x_loc2, y_loc2 = math.cos(angle) * length, math.sin(angle) * length
                pygame.draw.line(window, self.colors[i], (800+x_loc, 600+y_loc), (800+x_loc2, 600+y_loc2), thickness)

        elif mode == "PIEBW":
            thickness = 2 if num_objs < 200 else 1
            length = 300
            for i, obj in enumerate(self.objs):
                angle = math.pi * 2 / num_objs * i
                x_loc, y_loc = math.cos(angle) * length, math.sin(angle) * length
                color = (255*obj,)*3 if self.colors[i] == WHITE else self.colors[i]
                pygame.draw.line(window, color, (800, 600), (800+x_loc, 600+y_loc), thickness)

        elif mode == "PIECOLOR":
            thickness = 2 if num_objs < 200 else 1
            length = 300
            for i, obj in enumerate(self.objs):
                angle = math.pi * 2 / num_objs * i
                x_loc, y_loc = math.cos(angle) * length, math.sin(angle) * length
                color = [255*x for x in colorsys.hsv_to_rgb(obj, 0.8, 0.8)] if self.colors[i] == WHITE else self.colors[i]
                pygame.draw.line(window, color, (800, 600), (800+x_loc, 600+y_loc), thickness)

        elif mode == "IMAGE":
            if image is not None:
                total_x_size = int(image.get_width() / image.get_height() * 550)
                x_size = total_x_size / num_objs + 1
                scl_img = pygame.transform.scale(image, (total_x_size, 550))
                for i, obj in enumerate(self.objs):
                    x_loc = total_x_size * i / num_objs + 250
                    try:
                        img_x_pos = total_x_size * sorted(self.objs).index(obj) / num_objs
                    except:
                        continue

                    cropped = scl_img.subsurface((img_x_pos, 0, x_size, 550))
                    window.blit(cropped, (x_loc, 350))

                    if self.colors[i] != WHITE:
                        pygame.draw.rect(window, self.colors[i], (x_loc, 350, x_size, 550), 1)

        if not sorter.active:
            if self.button_gen_objs.clicked(events):
                self.gen_objs(self.slider_num_objs.value)
            if self.button_random.clicked(events):
                self.gen_objs(self.slider_num_objs.value)
                self.shuffle()


class ObjAppearance:
    scroll_speed = 10
    choice_width = 30
    choices = (
        ("Bars", "BARS"),
        ("Scatterplot", "SCATTERPLOT"),
        ("Black & White", "BW"),
        ("Color Gradient", "COLOR"),
        ("Pie", "PIE"),
        ("Pie Scatter", "PIESCATTER"),
        ("Pie BW", "PIEBW"),
        ("Pie Color", "PIECOLOR"),
        ("Image", "IMAGE"),
    )

    def __init__(self, loc, size, font):
        self.loc = loc
        self.size = size
        self.font = font
        self.offset = 0
        self.sel_ind = 0
        self.image = None
        self.button_load_img = Button((loc[0]+size[0]+30, loc[1]), (100, 35), FONT_MED.render("Load Image", 1, BLACK))

    def draw(self, window, events):
        loc = self.loc
        size = self.size
        surface = pygame.Surface(self.size)

        for i, choice in enumerate(self.choices):
            y_loc = self.choice_width*i + self.offset
            color = CHOICE_LIGHT if i%2 == 0 else CHOICE_DARK
            if i == self.sel_ind:
                color = CHOICE_SELECT

            pygame.draw.rect(surface, color, (0, y_loc, size[0], self.choice_width))
            text = self.font.render(choice[0], 1, BLACK)
            text_loc = ((size[0]-text.get_width()) // 2, y_loc + (self.choice_width-text.get_height())//2)
            surface.blit(text, text_loc)

        window.blit(surface, self.loc)
        pygame.draw.rect(window, WHITE, self.loc+self.size, 2)
        if self.sel_ind == 8:
            self.button_load_img.draw(window, events)
            if self.image is not None:
                window.blit(pygame.transform.scale(self.image, (150, 80)), (loc[0]+size[0]+30, loc[1]+50))
            if self.button_load_img.clicked(events):
                path = askopenfilename()
                if os.path.isfile(path):
                    self.image = pygame.image.load()

        mouse_pos = pygame.mouse.get_pos()
        if loc[0] <= mouse_pos[0] <= loc[0]+size[0] and loc[1] <= mouse_pos[1] <= loc[1]+size[1]:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        index = (mouse_pos[1]-loc[1]-self.offset) // self.choice_width
                        if 0 <= index < len(self.choices):
                            self.sel_ind = index

                    elif event.button == 4:
                        self.offset += self.scroll_speed
                    elif event.button == 5:
                        self.offset -= self.scroll_speed

        self.offset = min(self.offset, 0)
        self.offset = max(self.offset, size[1] - len(self.choices)*self.choice_width)


class Sorter:
    scroll_speed = 10
    choice_width = 30
    choices = (
        ("Bubble", "sort_bubble"),
        ("Cocktail Shaker", "sort_cocktail"),
        ("Gnome", "sort_gnome"),
        ("Insertion", "sort_insertion"),
        ("Selection", "sort_selection"),
        ("Shell", "sort_shell"),
        ("Comb", "sort_comb"),
        ("Cycle", "sort_cycle"),
    )
    
    def __init__(self, loc, size, font):
        self.loc = loc
        self.size = size
        self.font = font
        self.offset = 0
        self.sel_ind = 0
        self.button = Button((loc[0]+size[0]+20, loc[1]), (100, 35), FONT_MED.render("Sort", 1, BLACK))
        self.button_stop = Button((loc[0]+size[0]+20, loc[1]+50), (100, 35), FONT_MED.render("Stop", 1, BLACK))
        self.active = False
        self.time_start = 0

    def draw(self, window, events, objects: Objects):
        loc = self.loc
        size = self.size
        surface = pygame.Surface(self.size)

        for i, choice in enumerate(self.choices):
            y_loc = self.choice_width*i + self.offset
            color = CHOICE_LIGHT if i%2 == 0 else CHOICE_DARK
            if i == self.sel_ind:
                color = CHOICE_SELECT

            pygame.draw.rect(surface, color, (0, y_loc, size[0], self.choice_width))
            text = self.font.render(choice[0], 1, BLACK)
            text_loc = ((size[0]-text.get_width()) // 2, y_loc + (self.choice_width-text.get_height())//2)
            surface.blit(text, text_loc)

        window.blit(surface, self.loc)
        pygame.draw.rect(window, WHITE, self.loc+self.size, 2)
        self.button.draw(window, events)
        self.button_stop.draw(window, events)

        mouse_pos = pygame.mouse.get_pos()
        if loc[0] <= mouse_pos[0] <= loc[0]+size[0] and loc[1] <= mouse_pos[1] <= loc[1]+size[1]:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        index = (mouse_pos[1]-loc[1]-self.offset) // self.choice_width
                        if 0 <= index < len(self.choices):
                            self.sel_ind = index

                    elif event.button == 4:
                        self.offset += self.scroll_speed
                    elif event.button == 5:
                        self.offset -= self.scroll_speed

        self.offset = min(self.offset, 0)
        self.offset = max(self.offset, size[1] - len(self.choices)*self.choice_width)

        if self.button.clicked(events) and not self.active:
            objects.reset_stats()
            func = getattr(self, self.choices[self.sel_ind][1])
            self.active = True
            self.time_start = time.time()
            threading.Thread(target=func, args=(objects,)).start()
        if self.button_stop.clicked(events):
            self.active = False

    def sort_bubble(self, objects: Objects):
        elements = objects.objs[:]
        num_elements = len(elements)
        clock = pygame.time.Clock()

        done = False
        while not done:
            done = True
            for i in range(num_elements-1):
                clock.tick(objects.slider_speed.value)
                if not self.active:
                    return
                
                objects.stats_comp += 1
                objects.stats_read += 2
                objects.colors = [WHITE for i in range(num_elements)]
                objects.colors[i] = RED
                objects.colors[i+1] = GREEN

                if elements[i] > elements[i+1]:
                    done = False
                    elements[i], elements[i+1] = elements[i+1], elements[i]

                    objects.stats_read += 2
                    objects.stats_write += 2
                
                objects.set_objs(elements)
        
        objects.colors = [BLUE for i in range(num_elements)]
        self.active = False

    def sort_cocktail(self, objects: Objects):
        elements = objects.objs[:]
        num_elements = len(elements)
        clock = pygame.time.Clock()

        done = False
        while not done:
            done = True
            
            for i in range(num_elements-1):
                clock.tick(objects.slider_speed.value)
                if not self.active:
                    return

                objects.stats_comp += 1
                objects.stats_read += 2
                objects.colors = [WHITE for i in range(num_elements)]
                objects.colors[i] = RED
                objects.colors[i+1] = GREEN

                if elements[i] > elements[i+1]:
                    done = False
                    elements[i], elements[i+1] = elements[i+1], elements[i]

                    objects.stats_read += 2
                    objects.stats_write += 2
                
                objects.set_objs(elements)

            for i in reversed(range(1, num_elements)):
                clock.tick(objects.slider_speed.value)
                if not self.active:
                    return

                objects.stats_comp += 1
                objects.stats_read += 2
                objects.colors = [WHITE for i in range(num_elements)]
                objects.colors[i] = RED
                objects.colors[i-1] = GREEN

                if elements[i] < elements[i-1]:
                    done = False
                    elements[i], elements[i-1] = elements[i-1], elements[i]

                    objects.stats_read += 2
                    objects.stats_write += 2
                
                objects.set_objs(elements)
        
        objects.colors = [BLUE for i in range(num_elements)]
        self.active = False

    def sort_gnome(self, objects: Objects):
        elements = objects.objs[:]
        num_elements = len(elements)
        clock = pygame.time.Clock()

        i = 0
        while i < num_elements:
            clock.tick(objects.slider_speed.value)
            if not self.active:
                return

            objects.colors = [WHITE for i in range(num_elements)]
            objects.colors[i] = GREEN
            if i > 0:
                objects.colors[i-1] = RED
            objects.stats_read += 2
            objects.stats_comp += 1

            if i == 0:
                i += 1
            if elements[i] >= elements[i-1]:
                i += 1
            else:
                objects.stats_read += 2
                objects.stats_write += 2
                elements[i], elements[i-1] = elements[i-1], elements[i]
                i -= 1

            objects.set_objs(elements)
        
        objects.colors = [BLUE for i in range(num_elements)]
        self.active = False

    def sort_insertion(self, objects: Objects):
        elements = objects.objs[:]
        num_elements = len(elements)
        clock = pygame.time.Clock()

        for i in range(1, num_elements):
            clock.tick(objects.slider_speed.value)
            if not self.active:
                return

            key = elements[i]
            j = i - 1
            while j >= 0 and key < elements[j]:
                objects.stats_read += 2
                objects.stats_write += 1
                objects.stats_comp += 1
                elements[j+1] = elements[j]
                j -= 1
            elements[j+1] = key

            objects.colors = [WHITE for i in range(num_elements)]
            objects.colors[i] = GREEN
            objects.stats_read += 1
            objects.stats_write += 1
            objects.colors[j+1] = RED
            objects.set_objs(elements)
        
        objects.colors = [BLUE for i in range(num_elements)]
        self.active = False

    def sort_selection(self, objects: Objects):
        elements = objects.objs[:]
        num_elements = len(elements)
        clock = pygame.time.Clock()

        for i in range(num_elements):
            clock.tick(objects.slider_speed.value)
            if not self.active:
                return

            min_index = i
            for j in range(i+1, num_elements):
                objects.stats_read += 2
                objects.stats_comp += 1
                if elements[min_index] > elements[j]:
                    min_index = j

            elements[i], elements[min_index] = elements[min_index], elements[i]

            objects.colors = [WHITE for i in range(num_elements)]
            objects.colors[i] = GREEN
            objects.colors[min_index] = RED
            objects.stats_read += 2
            objects.stats_write += 2
            objects.set_objs(elements)
        
        objects.colors = [BLUE for i in range(num_elements)]
        self.active = False

    def sort_shell(self, objects: Objects):
        elements = objects.objs[:]
        num_elements = len(elements)
        clock = pygame.time.Clock()

        gap = num_elements // 2
        while gap > 0:
            for i in range(gap, num_elements):
                clock.tick(objects.slider_speed.value)
                if not self.active:
                    return

                objects.colors = [WHITE for i in range(num_elements)]
                objects.colors[i] = RED
                
                objects.stats_read += 1
                tmp = elements[i]
                j = i
                while j >= gap and elements[j-gap] > tmp:
                    if not self.active:
                        return

                    elements[j] = elements[j-gap]
                    j -= gap

                    objects.set_objs(elements)
                    objects.stats_write += 1
                    objects.stats_read += 2
                    objects.stats_comp += 2
                    objects.colors = [WHITE for i in range(num_elements)]
                    objects.colors[j] = RED
                    objects.colors[j-gap] = GREEN
                
                elements[j] = tmp
            gap //= 2
        
        objects.colors = [BLUE for i in range(num_elements)]
        self.active = False

    def sort_comb(self, objects: Objects):
        def next_gap(gap):
            gap = gap * 10 / 13
            if gap < 1:
                return 1
            return int(gap)

        elements = objects.objs[:]
        num_elements = len(elements)
        clock = pygame.time.Clock()

        gap = num_elements
        swapped = True
        while gap != 1 or swapped:
            gap = next_gap(gap)
            swapped = False

            for i in range(num_elements-gap):
                clock.tick(objects.slider_speed.value)
                if not self.active:
                    return

                objects.colors = [WHITE for i in range(num_elements)]
                objects.colors[i] = RED
                objects.colors[i+gap] = GREEN
                objects.stats_comp += 1
                objects.stats_read += 2
                objects.stats_write += 2

                if elements[i] > elements[i+gap]:
                    elements[i], elements[i+gap] = elements[i+gap], elements[i]
                    swapped = True

                objects.set_objs(elements)
        
        objects.colors = [BLUE for i in range(num_elements)]
        self.active = False

    def sort_cycle(self, objects: Objects):
        elements = objects.objs[:]
        num_elements = len(elements)
        clock = pygame.time.Clock()

        for start in range(0, num_elements-1):
            objects.stats_read += 3
            objects.stats_write += 2

            item = elements[start]
            pos = start

            for i in range(start+1, num_elements):
                objects.stats_read += 1
                objects.stats_comp += 1

                if elements[i] < item:
                    pos += 1
            
            if pos == start:
                continue

            while item == elements[pos]:
                objects.stats_read += 1
                objects.stats_comp += 1

                pos += 1

            objects.colors = [WHITE for i in range(num_elements)]
            objects.colors[pos] = RED
            elements[pos], item = item, elements[pos]

            while pos != start:
                clock.tick(objects.slider_speed.value)
                if not self.active:
                    return

                pos = start
                for i in range(start+1, num_elements):
                    objects.stats_comp += 1
                    objects.stats_read += 1
                    if elements[i] < item:
                        pos += 1
                
                while item == elements[pos]:
                    objects.stats_comp += 1
                    objects.stats_read += 1
                    pos += 1

                objects.stats_read += 2
                objects.stats_write += 2
                objects.colors = [WHITE for i in range(num_elements)]
                objects.colors[pos] = RED

                elements[pos], item = item, elements[pos]

                objects.set_objs(elements)
        
        objects.colors = [BLUE for i in range(num_elements)]
        self.active = False


def main():
    pygame.display.set_caption("Sorting Visualizer - Version 3")
    pygame.display.set_icon(pygame.image.load("icon.png"))
    WINDOW = pygame.display.set_mode(SCREEN)

    clock = pygame.time.Clock()
    objects = Objects(50)
    sorter = Sorter((50, 50), (150, 200), FONT_MED)
    appear = ObjAppearance((700, 50), (150, 200), FONT_MED)
    while True:
        clock.tick(FPS)
        pygame.display.update()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                sorter.active = False
                pygame.quit()
                return

        WINDOW.fill(BLACK)
        sorter.draw(WINDOW, events, objects)
        objects.draw(WINDOW, events, appear.choices[appear.sel_ind][1], sorter, appear.image)
        appear.draw(WINDOW, events)


main()