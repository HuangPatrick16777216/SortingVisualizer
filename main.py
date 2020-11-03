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
import pygame
import random
import threading
from pumpkinpy.pygameutils.elements import ButtonText, Slider

SCREEN = (1600, 900)
FPS = 24
processing = None
elements = []

pygame.init()
pygame.display.set_caption("Sorting Visualizer")
WINDOW = pygame.display.set_mode(SCREEN)

BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
FONT_SMALL = pygame.font.SysFont("comicsans", 18)
FONT_MEDIUM = pygame.font.SysFont("comicsans", 24)


class Blocks:
    sizeRange = (50, 600)
    bigPadding = 50
    smallPadding = 1

    def Generate(self, size):
        global elements
        elements = []
        for _ in range(size):
            elements.append([random.randint(*self.sizeRange), WHITE])

    def Draw(self, window):
        width = (SCREEN[0] - self.bigPadding*2) / len(elements)
        for i, e in enumerate(elements):
            size, col = e
            pygame.draw.rect(window, col, ((width*i+self.bigPadding+1)//1, SCREEN[1]-size, width-2, size))


class Buttons:
    sliderSize = Slider((20, 20), (200, 10), valRange=(20, 350), initialVal=100, font=FONT_SMALL, text="Set Size", textCol=WHITE)
    sliderSpeed = Slider((20, 100), (200, 10), valRange=(10, 120), initialVal=30, font=FONT_SMALL, text="Speed", textCol=WHITE)
    buttonGenSet = ButtonText((250, 20), (150, 35), WHITE, GRAY, BLACK, FONT_MEDIUM.render("Generate", 1, BLACK), border=3, borderCol=WHITE)

    buttonInsertion =  ButtonText((450, 20), (150, 35), WHITE, GRAY, BLACK, FONT_MEDIUM.render("Insertion", 1, BLACK), border=3, borderCol=WHITE)

    def Draw(self, window, events):
        self.sliderSize.Draw(window)
        self.sliderSpeed.Draw(window)
        self.buttonGenSet.Draw(window, events)

        self.buttonInsertion.Draw(window, events)
            

class InsertionSort:
    def __init__(self):
        global elements
        self.go = False
        threading.Thread(target=self.Start, args=()).start()

    def Start(self):
        global processing, elements
        for i in range(1, len(elements)):
            while not self.go:
                continue

            for e in elements:
                e[1] = WHITE

            elements[i][1] = GREEN
            currNum = elements[i][0]
            j = i - 1
            while j >= 0 and currNum < elements[j][0]:
                elements[j+1][0] = elements[j][0]
                j -= 1
            elements[j+1][0] = currNum
            elements[j+1][1] = RED
            self.go = False

        for e in elements:
            e[1] = GREEN

        processing = None
        self.go = False
        self.Start()


def Main():
    global processing
    clock = pygame.time.Clock()
    blocks = Blocks()
    buttons = Buttons()
    blocks.Generate(100)

    sortInsertion = InsertionSort()
    fps = FPS
    while True:
        clock.tick(fps)
        pygame.display.update()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        WINDOW.fill(BLACK)
        blocks.Draw(WINDOW)
        buttons.Draw(WINDOW, events)

        fps = buttons.sliderSpeed.value
        if buttons.buttonGenSet.clicked:
            blocks.Generate(buttons.sliderSize.value)
        
        if processing is None:
            if buttons.buttonInsertion.clicked:
                processing = "INSERTION"

        if processing == "INSERTION":
            sortInsertion.go = True


Main()