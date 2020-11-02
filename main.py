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

import pygame
import random
from pumpkinpy.pygameutils.elements import ButtonText, Slider

SCREEN = (1600, 900)
FPS = 60

pygame.init()
pygame.display.set_caption("Sorting Visualizer")
WINDOW = pygame.display.set_mode(SCREEN)

BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
FONT_SMALL = pygame.font.SysFont("comicsans", 18)
FONT_MEDIUM = pygame.font.SysFont("comicsans", 24)


class Blocks:
    sizeRange = (50, 600)
    bigPadding = 50
    smallPadding = 1

    def __init__(self):
        self.elements = []

    def Generate(self, size):
        self.elements = []
        for _ in range(size):
            self.elements.append(random.randint(*self.sizeRange))

    def Draw(self, window):
        width = (SCREEN[0] - self.bigPadding*2) / len(self.elements)
        for i, e in enumerate(self.elements):
            pygame.draw.rect(window, WHITE, ((width*i+self.bigPadding+1)//1, SCREEN[1]-e, width-2, e))


class Buttons:
    sliderSize = Slider((20, 20), (200, 10), valRange=(20, 350), initialVal=100, font=FONT_SMALL, text="Set Size", textCol=WHITE)
    buttonGenSet = ButtonText((250, 20), (150, 35), WHITE, GRAY, BLACK, FONT_MEDIUM.render("Generate", 1, BLACK), border=3, borderCol=WHITE)

    def Draw(self, window, events):
        self.sliderSize.Draw(window)
        self.buttonGenSet.Draw(window, events)
            

def Main():
    clock = pygame.time.Clock()
    blocks = Blocks()
    buttons = Buttons()
    blocks.Generate(350)
    while True:
        clock.tick(FPS)
        pygame.display.update()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        WINDOW.fill(BLACK)
        blocks.Draw(WINDOW)
        buttons.Draw(WINDOW, events)

        if buttons.buttonGenSet.clicked:
            blocks.Generate(buttons.sliderSize.value)


Main()