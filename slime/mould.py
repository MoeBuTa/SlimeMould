import random

import networkx as nx

from slime.slime import SlimeCell
from slime.cell import Cell
import math

from networkx.algorithms import tournament
LOW_PH_THRESHOLD = 3.5
LOW_PH_MOULD_MAX_SIZE = 10000
TARGET_SWITCH_THRESHOLD = 10


def get_corner_slime_cells(slime_cells, current_direction, capital_slime=None):
    slime_idx = slime_cells.keys()
    if current_direction == 0:
        capital_slime = slime_cells[min(slime_idx)]
    elif current_direction == 1:
        max_x = max([x for x, y in slime_idx])
        for x, y in slime_idx:
            if x == max_x:
                capital_slime = slime_cells[(x, y)]
                break
    elif current_direction == 2:
        min_y = min([y for x, y in slime_idx])
        for x, y in slime_idx:
            if y == min_y:
                capital_slime = slime_cells[(x, y)]
                break
    elif current_direction == 3:
        capital_slime = slime_cells[max(slime_idx)]
    if capital_slime.get_reached_food_id() is not None:
        get_corner_slime_cells(slime_cells, current_direction, capital_slime)
    return capital_slime


class Mould:
    def __init__(self, city, mould_shape: tuple, init_mould_coverage: float, decay: float):
        self.city = city
        self.decay = decay
        self.slime_cells = {}
        self.mould_shape = mould_shape
        self.reached_food_ids = set()
        self.current_target = 0
        self.capital_slime = None

        self.corner_foods = self.city.get_all_corner_foods()
        self.initialise(city, mould_shape, init_mould_coverage)

        self.avg_health = []
        self.total_num = []

        self.target_switch_count = 0

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
        #
        #     while self.capital_slime.get_reached_food_id() is not None:
        #         self.capital_slime = get_corner_slime_cells(self.slime_cells, random.choice([0, 1, 2, 3]))
        #
        # else:
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

        if len(self.reached_food_ids) == 0:
            return
        min_dist = -1
        min_i = 0
        food_idx = self.city.get_food_position(food_id)
        for i in self.reached_food_ids:
            reachable_food_idx = self.city.get_food_position(i)
            dist = math.dist(food_idx, reachable_food_idx)
            if min_dist > dist or min_dist < 0:
                min_dist = dist
                min_i = i

        if not self.city.get_food_graph().has_edge(food_id, min_i):
                # not nx.has_path(self.city.get_food_graph(), next(iter(self.reached_food_ids)), min_i):
            print((food_id, min_i))
            self.city.add_food_edge(food_id, min_i)

    def update_target_food(self):
        # set a target food
        remaining_food_ids = set(self.city.get_all_foods().keys()) - self.reached_food_ids
        min_i = self.capital_slime.find_nearest_food(remaining_food_ids)[0]
        if min_i != self.current_target:
            self.current_target = (min_i, self.city.get_food_position(min_i))
            # update the connection to the target food from reachable food
            self.update_food_connection(min_i)

    def update_slime(self):
        if self.target_switch_count > TARGET_SWITCH_THRESHOLD or \
         self.capital_slime.get_reached_food_id() is not None or self.current_target[0] in self.reached_food_ids:
            self.target_switch_count = 0
            self.setup_capital_slime()
            self.update_target_food()
        slimes = list(self.slime_cells.values())
        for slime in slimes:
            if slime.get_pheromone() < LOW_PH_THRESHOLD and \
                    math.dist(slime.get_idx(), self.capital_slime.get_idx()) > LOW_PH_MOULD_MAX_SIZE and \
                    not slime.is_capital:
                self.remove_slime_cell(slime.get_idx())

    def get_current_target(self):
        return self.current_target

    def get_reached_food_ids(self):
        return self.reached_food_ids

    def evolve(self):
        previous_reached_foods = len(self.reached_food_ids)
        self.total_num.append(len(self.slime_cells))
        slime_idx = list(self.slime_cells.keys())
        for idx in slime_idx:
            self.city.get_lattice()[idx].step(self.city.get_lattice(), self.decay)
        if len(self.reached_food_ids) == previous_reached_foods:
            self.target_switch_count += 1
        self.update_slime()

