import numpy as np
from slime.food import FoodCell
from collections import deque
from slime.cell import Cell
import random


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


def step_direction(index: int):
    """
    * 1 = up
    * 2 = upper-right diagonal
    * 3 = right
    * 4 = lower-right diagonal
    * 5 = down
    * 6 = lower-left diagonal
    * 7 = left
    * 8 = upper-left diagonal
    """
    next_step = {
        1: (-1, 0),
        2: (-1, 1),
        3: (0, 1),
        4: (1, 1),
        5: (1, 0),
        6: (1, -1),
        7: (0, -1),
        8: (-1, -1)
    }
    return next_step[index]


def get_lookouts(sensor_offset):
    """
    Returns a dictionary containing lookout points offset
    values for the given sensor offset
    """
    s = sensor_offset
    d = int(s / np.sqrt(2))
    lookouts = {
        1: [(-s, 0), (-d, -d)],
        2: [(-d, d), (-s, 0)],
        3: [(0, s), (-d, d)],
        4: [(d, d), (0, s)],
        5: [(s, 0), (d, d)],
        6: [(d, -d), (s, 0)],
        7: [(0, -s), (d, -d)],
        8: [(-d, -d), (0, -s)]
    }
    return lookouts


class SlimeCell(Cell):

    def __init__(self, idx: tuple, pheromone: float, direction: int, mould, city):
        super().__init__(pheromone=pheromone, cell_type=1)

        self.idx = idx
        self.pheromone = pheromone
        self.direction = direction
        self.food_id = None
        # self.goals = city.get_foods()
        self.stalling_time = 0
        self.mould = mould
        self.city = city

    @staticmethod
    def check_boundary(idx, lattice_shape):
        if idx[0] > lattice_shape[0] or idx[0] < 0 or idx[1] > lattice_shape[1] or idx[1] < 0:
            return False
        return True

    # diffusion
    def diffusion(self, lattice, decay):
        neighbour_count = 1
        for neigh in neighbours(self.idx):
            # continue if the neighbor is out of boundary
            if not self.check_boundary(neigh, lattice.shape):
                continue

            # generate a slime cell on an cell neighbor,
            # decay itself
            if lattice[neigh].get_cell_type() == 0:
                self.mould.slime_cell_generator(idx=neigh, decay=decay)
                self.pheromone *= (1 - (2 * decay))

            # neighbor is a slime
            elif lattice[neigh].get_cell_type() == 1:
                neighbour_count += 1
                if self.pheromone < 4.5:
                    self.pheromone += (lattice[neigh].pheromone / 10)

            # add pheromone if current cell find food nearby
            elif lattice[neigh].get_cell_type() == 2:
                self.pheromone = 6

        if self.pheromone < 2:
            return self.mould.remove_slime_cell(self.idx)

        self.pheromone *= (1 - (decay / neighbour_count))

        self.mould.update_slime_cell(self.idx, self)
        return True

    def move(self, lattice, decay):
        new_step = step_direction(self.direction)
        new_idx = (self.idx[0] + new_step[0], self.idx[1] + new_step[1])
        new_slime = None
        if self.check_boundary(new_idx, lattice.shape):
            if lattice[new_idx].cell_type == 0:
                self.mould.remove_slime_cell(self.idx)
                new_slime = self.mould.slime_cell_generator(new_idx, decay=0.5 * decay)
            elif lattice[new_idx].cell_type == 1:
                # self.direction = random.randint(1, 8)
                self.pheromone *= (1 - decay)
                self.stalling_time += 1
                new_slime = self.mould.update_slime_cell(self.idx, self)
            elif lattice[new_idx].cell_type == 2:
                # self.direction = random.randint(1, 8)
                self.pheromone *= (1 - decay)
                self.stalling_time += 1
                new_slime = self.mould.update_slime_cell(self.idx, self)
        return new_slime

    def sensory(self, sensor_offset):
        sensors = []
        for i in get_lookouts(sensor_offset)[self.direction]:
            ph_idx = (self.idx[0] + i[0], self.idx[1] + i[1])
            if self.city.lattice[ph_idx] is None:
                sensors.append(0)
            else:
                sensors.append(self.city.lattice[ph_idx].pheromone)
        best = np.argmax(sensors)

        if best == 1:
            self.direction -= 1
            if self.direction <= 0:
                self.direction = 8
        elif best == 2:
            self.direction += 1
            if self.direction >= 9:
                self.direction = 1
        self.mould.update_slime_cell(self.idx, self)

    def step(self, lattice, decay, sensor_offset):
        # alive after diffusion
        if not self.diffusion(lattice, decay):
            return
        else:
            new_slime = self.move(lattice, decay)
            if new_slime is not None:
                if new_slime.stalling_time > 5:
                    self.mould.remove_slime_cell(new_slime.idx)
                self.sensory(sensor_offset)
