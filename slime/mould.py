import numpy as np
import random
from slime.slime import SlimeCell
from slime.cell import Cell
import math
from collections import deque

LOW_PH_THRESHOLD = 2
LOW_PH_MOULD_MAX_SIZE = 10000
TARGET_SWITCH_THRESHOLD = 5


def get_corner_slime_cells(slime_cells, current_direction):
    slime_idx = slime_cells.keys()
    if current_direction == 0:
        return slime_cells[min(slime_idx)]
    elif current_direction == 1:
        max_x = max([x for x, y in slime_idx])
        for x, y in slime_idx:
            if x == max_x:
                return slime_cells[(x, y)]
    elif current_direction == 2:
        min_y = min([y for x, y in slime_idx])
        for x, y in slime_idx:
            if y == min_y:
                return slime_cells[(x, y)]
    elif current_direction == 3:
        return slime_cells[max(slime_idx)]


class Mould:
    def __init__(self, city, mould_shape: tuple, init_mould_coverage: float, decay: float):
        self.city = city
        self.decay = decay
        self.slime_cells = {}
        self.mould_shape = mould_shape
        self.reached_food_ids = []
        self.current_target = 0
        self.capital_slime = None

        self.corner_foods = self.city.get_all_corner_foods()
        self.initialise(city, mould_shape, init_mould_coverage)

        self.avg_health = []
        self.total_num = []

    def remove_slime_cell(self, idx):
        self.city.set_lattice(idx, Cell())
        del self.slime_cells[idx]
        return False

    def update_slime_cell(self, idx, slime: SlimeCell):
        if idx is None or slime is None:
            return
        self.slime_cells[idx] = slime
        self.city.set_lattice(idx, slime)

    def initialise(self, city, mould_shape, init_mould_coverage):
        row = mould_shape[0] // 2
        col = mould_shape[1] // 2
        for x in range(len(city.lattice) // 2 - row, len(city.lattice) // 2 + row):
            for y in range(len(city.lattice[x]) // 2 - col, len(city.lattice[x]) // 2 + col):
                if random.random() < init_mould_coverage and (x, y) not in self.city.get_all_foods_idx():
                    self.slime_cell_generator(idx=(x, y))
        self.setup_capital_slime()
        self.update_target_food()

    def setup_capital_slime(self):
        if self.capital_slime is not None:
            previous_capital_slime = self.capital_slime
            previous_capital_slime.remove_capital()
            self.update_slime_cell(previous_capital_slime.get_idx(), previous_capital_slime)

            while self.capital_slime.get_reached_food_id() is not None:
                self.capital_slime = get_corner_slime_cells(self.slime_cells, random.choice([0, 1, 2, 3]))

        else:
            self.capital_slime = get_corner_slime_cells(self.slime_cells, random.choice([0, 1, 2, 3]))
        self.update_slime_cell(self.capital_slime.get_idx(), self.capital_slime)

    def slime_cell_generator(self, idx, pheromone=None, decay=0, is_capital=False):
        if pheromone is None:
            pheromone = 4. * (1 - decay)
        slime_cell = SlimeCell(idx=idx, pheromone=pheromone, mould=self, city=self.city, is_capital=is_capital)
        if slime_cell.is_capital:
            self.capital_slime = slime_cell
        self.update_slime_cell(slime_cell.get_idx(), slime_cell)
        return slime_cell

    def update_food_connection(self, food_id):
        min_dist = -1
        min_i = 0
        food_idx = self.city.get_food_position(food_id)
        for i in self.reached_food_ids:
            reachable_food_idx = self.city.get_food_position(i)
            dist = math.dist(food_idx, reachable_food_idx)
            if min_dist > dist or min_dist < 0:
                min_dist = dist
                min_i = i
            # self.reached_food_ids.append(food_id)
            self.city.add_food_edge(food_id, min_i)

    def update_target_food(self):
        # set a target food
        remaining_food_ids = set(self.city.get_all_foods().keys()) - set(self.reached_food_ids)
        min_i = self.capital_slime.find_nearest_food(remaining_food_ids)
        self.current_target = (min_i, self.city.get_food_position(min_i))

        # update the connection to the target food from reachable food
        if len(self.reached_food_ids) != 0:
            self.update_food_connection(min_i)
        print(min_i)

    def update_slime(self):
        if abs(len(self.slime_cells) - self.total_num[-1]) < TARGET_SWITCH_THRESHOLD or \
         self.capital_slime.get_reached_food_id() is not None:
            self.setup_capital_slime()
            self.update_target_food()
        slimes = list(self.slime_cells.values())
        for slime in slimes:
            if slime.get_pheromone() < LOW_PH_THRESHOLD and \
                    math.dist(slime.get_idx(), self.capital_slime.get_idx()) > LOW_PH_MOULD_MAX_SIZE:
                self.remove_slime_cell(slime.get_idx())

    def get_current_target(self):
        return self.current_target

    def get_reached_food_ids(self):
        return self.reached_food_ids

    def evolve(self):
        # print(len(self.slime_cells))
        self.total_num.append(len(self.slime_cells))
        slime_idx = list(self.slime_cells.keys())
        for idx in slime_idx:
            self.city.get_lattice()[idx].step(self.city.get_lattice(), self.decay)
        self.update_slime()
