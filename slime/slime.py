import numpy as np
from slime.food import FoodCell
from collections import deque
from slime.cell import Cell
import random


DIFFUSION_THRESHOLD = 3.2
MOVING_THRESHOLD = 0.3
MAX_PH = 3


def neighbours(idx):
    return [
        (idx[0] - 1, idx[1] - 1),  # up   1, left  1
        (idx[0] - 1, idx[1]),  # up   1,
        (idx[0] - 1, idx[1] + 1),  # up   1, right 1
        (idx[0], idx[1] - 1),  # , left  1
        (idx[0], idx[1] + 1),  # , right 1
        (idx[0] + 1, idx[1] - 1),  # down 1, left  1
        (idx[0] + 1, idx[1]),  # down 1,
        (idx[0] + 1, idx[1] + 1),  # down 1, right 1
    ]


def step_direction(index: int, idx: tuple):
    next_step = {
        1: (-1, -1),
        2: (1, -1),
        3: (-1, 1),
        4: (1, 1),
        5: (-1, 0),
        6: (1, 0),
        7: (0, -1),
        8: (0, 1)
    }
    return next_step[index][0] + idx[0], next_step[index][1] + idx[1]


class SlimeCell(Cell):

    def __init__(self, idx: tuple, pheromone: float, mould, city, is_capital):
        super().__init__(pheromone=pheromone, cell_type=1)

        self.idx = idx
        self.pheromone = pheromone
        self.max_ph = MAX_PH
        self.direction = random.randint(1, 8)
        self.is_capital = is_capital
        self.reached_food_idx = None
        self.reached_goal = False
        self.mould = mould

        self.city = city

    @staticmethod
    def check_boundary(idx, lattice_shape):
        if idx[0] > lattice_shape[0] or idx[0] < 0 or idx[1] > lattice_shape[1] or idx[1] < 0:
            return False
        return True

    # diffusion
    def diffusion(self, lattice, decay):
        new_idx = step_direction(self.direction, self.idx)
        for neigh in neighbours(self.idx):
            # continue if the neighbor is out of boundary
            if not self.check_boundary(neigh, lattice.shape):
                continue
            neigh_cell = lattice[neigh]

            # neighbour cell is an empty cell
            if neigh_cell.get_cell_type() == 0:

                # neighbour cell is the main diffusion cell
                if neigh == new_idx and self.pheromone > MOVING_THRESHOLD:
                    self.mould.slime_cell_generator(idx=neigh, pheromone=self.pheromone, decay=decay,
                                                    is_capital=self.is_capital)
                    self.pheromone *= (1 - decay)
                    self.is_capital = False
                    continue

                # neighbour cell is a random diffusion cell
                if self.pheromone > DIFFUSION_THRESHOLD:
                    self.mould.slime_cell_generator(idx=neigh, pheromone=self.pheromone / 2, decay=decay * 5)
                    self.pheromone *= (1 - 3 * decay)

            # neighbor is a slime
            elif neigh_cell.get_cell_type() == 1:

                # neighbor bigger than self
                if neigh_cell.max_ph > self.max_ph and self.reached_food_idx is not None:
                    self.max_ph *= 1.4

                # increase self-pheromone when find neighbor nearby
                if self.max_ph > self.pheromone > 0.1:
                    self.pheromone += (neigh_cell.pheromone / 10)

                # todo: next main diffusion place is a slime cell
                # if neigh == new_idx:
                #     pass

            # add pheromone if current cell find food nearby
            elif neigh_cell.get_cell_type() == 2:

                # eat food
                self.pheromone = 8
                self.max_ph = 8

                # todo: next main diffusion place is food
                # if neigh == new_idx:
                #     pass
                food_id = neigh_cell.get_food_id()
                if food_id in self.mould.reached_food_id:
                    pass
                else:
                    self.mould.reached_food_id.append(food_id)
                    self.reached_food_idx = neigh_cell.food_idx
                    self.mould.update_slime_cell(self.idx, self)
                    return self.reached_food_idx
        self.mould.update_slime_cell(self.idx, self)
        return

    def sensory(self):
        target_food_id = self.mould.get_current_target()
        food_idx = self.city.get_all_foods()[target_food_id][0].get_food_idx()
        if self.reached_food_idx in self.city.get_all_foods()[target_food_id]:
            return
        # upper left (-1, -1)
        if food_idx[0] < self.idx[0] and food_idx[1] < self.idx[1]:
            self.direction = 1
        # upper right (1, -1)
        elif food_idx[0] > self.idx[0] and food_idx[1] < self.idx[1]:
            self.direction = 2
        # lower left (-1, 1)
        elif food_idx[0] < self.idx[0] and food_idx[1] > self.idx[1]:
            self.direction = 3
        # lower right (1, 1)
        elif food_idx[0] > self.idx[0] and food_idx[1] > self.idx[1]:
            self.direction = 4
        # left (-1, 0)
        elif food_idx[0] > self.idx[0]:
            self.direction = 5
        # right (1, 0)
        elif food_idx[0] > self.idx[0]:
            self.direction = 5
        # up (0, -1)
        elif food_idx[1] > self.idx[1]:
            self.direction = 7
        # down (0, 1)
        elif food_idx[1] < self.idx[1]:
            self.direction = 8
        self.mould.update_slime_cell(self.idx, self)

    def step(self, lattice, decay):
        if self.reached_food_idx is not None:
            return
        # alive after diffusion
        self.sensory()
        return self.diffusion(lattice, decay)

    def get_idx(self):
        return self.idx

    def get_pheromone(self):
        return self.pheromone

    def set_pheromone(self, ph):
        self.pheromone = ph

    def get_reached_food_idx(self):
        return self.reached_food_idx

