import numpy as np
import random
from slime.slime import SlimeCell
from slime.cell import Cell
import math
from collections import deque


class Mould:
    def __init__(self, city, mould_shape: tuple, init_mould_coverage: float, decay: float):
        self.city = city
        self.decay = decay
        self.slime_cells = {}
        self.mould_shape = mould_shape
        self.reached_food_id = []
        self.current_target = 0
        self.corner_foods = self.city.get_all_corner_foods()
        self.corner_types = ['left', 'right', 'down', 'up']
        self.initialise(city, mould_shape, init_mould_coverage)
        self.capital_slime = None
        self.setup_capital_slime()
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
                    slime_cell = self.slime_cell_generator(idx=(x, y))

    def setup_capital_slime(self):
        self.capital_slime = self.get_corner_slime_cells(random.choice([0, 1, 2, 3]))
        self.update_slime_cell(self.capital_slime.get_idx(), self.capital_slime)

    def slime_cell_generator(self, idx, pheromone=None, decay=0, is_capital=False):
        if pheromone is None:
            pheromone = 3. * (1 - decay)
        slime_cell = SlimeCell(idx=idx, pheromone=pheromone, mould=self, city=self.city, is_capital=is_capital)
        if slime_cell.is_capital:
            self.capital_slime = slime_cell
        self.update_slime_cell(slime_cell.get_idx(), slime_cell)
        return slime_cell

    def update_target_food(self):
        remaining_food_id = set(self.city.get_all_foods().keys()) - set(self.reached_food_id)
        slime_idx = self.capital_slime.get_idx()

        # # use food type to determine the direction of the evolution
        # for food_type in self.corner_types:
        #     if self.city.get_all_corner_foods()[food_type] not in self.reached_food_id:
        #         slime_idx = self.get_corner_slime_cells(food_type)
        #         break

        min_dist = -1
        min_i = 0
        for i in remaining_food_id:
            idx = self.city.get_all_foods()[i][0].get_food_idx()
            dist = math.dist(slime_idx, idx)
            if min_dist > dist or min_dist < 0:
                min_dist = dist
                min_i = i
        self.current_target = min_i

    def evolve(self):
        """
        * The diffusion stage: all pheromones undergo diffusion
        * The motor stage: all slime cells determine if they can move forward or not
        * The sensory stage: all slime cells adjust their direction based on the pheromones
        """
        self.update_target_food()
        self.total_num.append(len(self.slime_cells))
        print(len(self.slime_cells))
        slimes = list(self.slime_cells.values())
        for cell in slimes:
            cell.step(self.city.get_lattice(), self.decay)
        self.update_slime_connection()

    def get_current_target(self):
        return self.current_target

    def update_slime_connection(self):
        if abs(len(self.slime_cells) - self.total_num[-1]) < 10 or self.capital_slime.get_reached_food_idx() is not None:
            self.setup_capital_slime()
        slimes = list(self.slime_cells.values())
        for slime in slimes:
            if slime.get_pheromone() < 5 and math.dist(slime.get_idx(), self.capital_slime.get_idx()) > 100:
                self.remove_slime_cell(slime.get_idx())
            #     continue
            # if slime.get_pheromone() < 5:
            #     slime.set_pheromone(3)
            #     self.update_slime_cell(slime.get_idx(), slime)

    def get_corner_slime_cells(self, current_direction):
        slime_idx = self.slime_cells.keys()
        if current_direction == 0:
            min_x = min([x for x, y in slime_idx])
            for x, y in slime_idx:
                if x == min_x:
                    return self.slime_cells[(x, y)]
        elif current_direction == 1:
            max_x = max([x for x, y in slime_idx])
            for x, y in slime_idx:
                if x == max_x:
                    return self.slime_cells[(x, y)]
        elif current_direction == 2:
            min_y = min([y for x, y in slime_idx])
            for x, y in slime_idx:
                if y == min_y:
                    return self.slime_cells[(x, y)]
        elif current_direction == 3:
            max_y = max([y for x, y in slime_idx])
            for x, y in slime_idx:
                if y == max_y:
                    return self.slime_cells[(x, y)]
