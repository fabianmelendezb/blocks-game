from typing import List, Tuple
from enum import Enum
import pygame
from dataclasses import dataclass
from random import randint
from copy import deepcopy

ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
VERTICAL_PADDING = 50
HORIZONTAL_PADDING = 120
BLOCK_SIZE = 50
BORDER_WIDTH = 3

class Color(Enum):
    NULL = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    ORANGE = (255, 0, 255)
    CYAN = (0, 255, 255)

    # BORDERS
    YELLOW = (255, 255, 0)
    GRAY = (50, 50, 50)

    @classmethod
    def list(cls):
        return list(map(lambda c: c, cls))

    @classmethod
    def get_color(cls, i: int):
        return cls.list()[i]

class IlegalMove(Exception):
    pass

@dataclass
class Container:
    blocks: Tuple[Color, Color, Color, Color]
    position: Tuple[int, int]
    selected: bool=False

    def clicked(self, click: Tuple[int, int]):
        return bool((click[0] >= self.position[0] and click[0] <= self.position[0] + BLOCK_SIZE)
                and (click[1] >= self.position[1] and click[1] <= self.position[1] + 4*BLOCK_SIZE))

    def entropy(self):
        last = self.blocks[0]
        entropy = 0
        for i in range(1,4):
            if self.blocks[i] != last:
                last = self.blocks[i]
                entropy += 1
        return entropy

    def __str__(self):
        return str([self.blocks[i].name for i in range(4)]) + ("*" if self.selected else "")

    def empty(self):
        return all([block == Color.NULL for block in self.blocks])

    def free(self):
        """Returns count of free blocks in this container"""

        free = 0
        for i in range(4):
            if self.blocks[i] == Color.NULL:
                free += 1
            else:
                break
        return free

    def first(self):
        """Returns the first empty slot"""
        first = None
        for i in range(4):
            if self.blocks[i] == Color.NULL:
                continue
            else:
                first = i-1
                break
        if first is None:
            first = 4-1
        return first

    def top(self) -> Tuple[Color, int]:
        """Returns the color and count of the top blocks in this container"""
        first = None
        count = 0

        for i in range(4):
            if self.blocks[i] == Color.NULL:
                continue
            elif first is None:
                first = self.blocks[i]
                count += 1
                continue
            elif self.blocks[i] == first:
                count += 1
            else:
                break
        return first, count


    def fill(self, color: Color, count: int):
        first = self.first()
        for i in range(first, first - count, -1):
            self.blocks[i] = color


    def remove(self, count: int):
        first = self.first()
        for i in range(first+1, first+1+count):
            self.blocks[i] = Color.NULL

    def transfer_from(self, container: "Container"):
        if self.free() == 0:
            raise IlegalMove(f"No free spaces in container: {self.blocks}")

        # What the other container wants to transfer
        transfer = container.top()
        if self.empty() or (self.top()[0] == transfer[0]):
            # We can transfer (now it depends how much)
            transfer_count = min([self.free(), transfer[1]])
            self.fill(color=transfer[0], count=transfer_count)
            container.remove(count=transfer_count)
        else:
            raise IlegalMove("Can't transfer from this container")


class State:
    IDLE = 1
    SELECTED = 2

class GameEngine:
    @classmethod
    def _swap_colors(cls, colors: List[List[Color]]):
        num_colors = len(colors)
        col_i = randint(0, num_colors-1)
        col_j = randint(0, num_colors-1)

        row_i = randint(0, 3)
        row_j = randint(0, 3)

        val_i = colors[col_i][row_i]
        val_j = deepcopy(colors[col_j][row_j])

        colors[col_j][row_j] = val_i
        colors[col_i][row_i] = val_j

    @classmethod
    def _color_init(cls, iter: int=15) -> List[List[Color]]:
        NUM_COLORS = 6
        colors = [[Color.get_color(i)]*4 for i in range(1, NUM_COLORS+1)]

        for i in range(iter):
            cls._swap_colors(colors=colors)

        # Add to empty rows
        colors.append([Color.NULL]*4)
        colors.append([Color.NULL] * 4)

        return colors

    def __init__(self, screen):
        self.screen = screen
        self.selected = None

        self.containers: List[Container] = []
        positions = [
            [120, 290, 460, 630] * 2,
            [50] * 4 + [350] * 4
        ]
        colors = GameEngine._color_init()
        for i in range(8):
            container = Container(
                blocks=colors[i],
                position=(positions[0][i], positions[1][i])
            )
            self.containers.append(
                container
            )
            self.paint(container)
        self.state: State = State.IDLE

    def paint(self, container: Container):
        for i in range(4):
            pygame.draw.rect(self.screen, container.blocks[i].value, (container.position[0], container.position[1] + i * VERTICAL_PADDING, BLOCK_SIZE, BLOCK_SIZE))
        # Draw border
        border = Color.YELLOW if container.selected else Color.GRAY
        pygame.draw.rect(self.screen, border.value, (container.position[0], container.position[1], BLOCK_SIZE, BLOCK_SIZE*4), BORDER_WIDTH)

    def find(self, click: Tuple[int, int]) -> Tuple[int,Container]:
        for index, container in enumerate(self.containers):
            if container.clicked((click)):
                print(f"Container {index} clicked")
                return index, container

    def handle(self, click: Tuple[int,int]):
        print(f"Click {click}")

        result = self.find(click=click)

        if result is None:
            if self.selected is not None:
                self.containers[self.selected].selected = False
                self.paint(self.containers[self.selected])
            self.selected = None
            self.state = State.IDLE
            return False

        index = result[0]
        clicked = result[1]

        if self.state == State.IDLE:
            clicked.selected = True
            self.paint(clicked)
            self.state = State.SELECTED
            self.selected = index

            return False
        elif self.state == State.SELECTED:
            container_from = self.containers[self.selected]

            try:
                clicked.transfer_from(container=container_from)
            except IlegalMove as e:
                print(e)

            container_from.selected = False

            self.paint(container_from)
            self.paint(clicked)

            # Cleanup
            self.selected = None
            self.state = State.IDLE

            return True

    def entropy(self) -> int:
        return sum([container.entropy() for container in self.containers])





