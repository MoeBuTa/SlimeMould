import random

import numpy as np

from slime.slime import SlimeCell
from slime.cell import Cell
import math

TARGET_SWITCH_THRESHOLD = 5


def get_corner_slime_cells(slime_cells, current_direction, direction_list=None):
    """
    get the slime cell in the corner of the mould for deciding the next target food
    :return: the slime cell in the selected corner
    """
    slime_idx = slime_cells.keys()
    curr_capital_slime = None
    if current_direction == 0:
        curr_capital_slime = slime_cells[min(slime_idx)]
    elif current_direction == 1:
        max_x = max([x for x, y in slime_idx])
        for x, y in slime_idx:
            if x == max_x:
                curr_capital_slime = slime_cells[(x, y)]
                break
    elif current_direction == 2:
        min_y = min([y for x, y in slime_idx])
        for x, y in slime_idx:
            if y == min_y:
                curr_capital_slime = slime_cells[(x, y)]
                break
    elif current_direction == 3:
        curr_capital_slime = slime_cells[max(slime_idx)]
    if curr_capital_slime.get_reached_food_id() is not None:
        if direction_list is not None:
            direction_list.remove(current_direction)
        else:
            direction_list = [0, 1, 2, 3]
        get_corner_slime_cells(slime_cells, random.choice(direction_list))
    return curr_capital_slime


class Mould:
    def __init__(self, dish, start_loc: tuple, mould_shape: tuple, init_mould_coverage: float, decay: float):
        self.dish = dish
        self.decay = decay
        self.slime_cells = {}
        self.mould_shape = mould_shape
        self.reached_food_ids = set()
        self.current_target = 0
        self.nearest_connected_target = -1
        self.capital_slime = None
        self.initialise(start_loc, mould_shape, init_mould_coverage)

        self.avg_ph = []
        self.total_num = []
        self.total_active_num = []
        self.total_inactive_num = []
        self.total_reached_foods = []
        self.coverage_ratio = []

        self.target_switch_count = 0

    def remove_slime_cell(self, idx):
        """
        remove the slime cell in the lattice
        :param idx: the tuple index of the slime cell
        """
        self.dish.set_lattice(idx, Cell())
        del self.slime_cells[idx]

    def update_slime_cell(self, idx, slime: SlimeCell):
        """
        update the lattice when changes made by a slime cell
        :param idx: the tuple index to be updated
        :param slime: the slime cell to be updated
        """
        if idx is None or slime is None:
            return
        self.slime_cells[idx] = slime
        self.dish.set_lattice(idx, slime)

    def initialise(self, start_loc, mould_shape, init_mould_coverage):
        """
        initialise the mould
        :param start_loc: the start location of the mould
        :param mould_shape: the size of the initial mould
        :param init_mould_coverage: the coverage rate of the initial mould
        """
        for x in start_loc[0] - mould_shape[0], start_loc[0] + mould_shape[0]:
            for y in start_loc[1] - mould_shape[1], start_loc[1] + mould_shape[1]:
                if random.random() < init_mould_coverage and (x, y) not in self.dish.get_all_foods_idx():
                    self.slime_cell_generator(idx=(x, y))
        self.setup_capital_slime()
        self.update_target_food()

    def setup_capital_slime(self):
        """
        set up the capital slime to decide the next target food of the mould
        """
        if self.capital_slime is not None:
            previous_capital_slime = self.capital_slime
            previous_capital_slime.remove_capital()
            self.update_slime_cell(previous_capital_slime.get_idx(), previous_capital_slime)
        self.capital_slime = get_corner_slime_cells(self.slime_cells, random.choice([0, 1, 2, 3]))
        self.update_slime_cell(self.capital_slime.get_idx(), self.capital_slime)

    def slime_cell_generator(self, idx, pheromone=None, decay=0, is_capital=False):
        """
        generate a slime cell
        :param idx: the tuple index to generate a slime cell
        :param pheromone: the pheromone value of the slime cell
        :param decay: the decay rate of the slime cell
        :param is_capital: set the next slime cell to be the capital slime if true
        :return: the generated slime cell
        """
        if pheromone is None:
            pheromone = 4. * (1 - decay)
        slime_cell = SlimeCell(idx=idx, pheromone=pheromone, mould=self, dish=self.dish, is_capital=is_capital)
        if slime_cell.is_capital:
            self.capital_slime = slime_cell
        self.update_slime_cell(slime_cell.get_idx(), slime_cell)
        return slime_cell

    def find_nearest_connected_food(self, food_id):
        """
        find the nearest connected food to the target food.
        :param food_id: the id of the target food
        :return: the nearest connected food to the target food
        """
        min_dist = -1
        min_i = -1
        food_idx = self.dish.get_food_position(food_id)
        for i in self.reached_food_ids:
            if i == food_id:
                continue
            reachable_food_idx = self.dish.get_food_position(i)
            dist = math.dist(food_idx, reachable_food_idx)
            if min_dist > dist or min_dist == -1:
                min_dist = dist
                min_i = i
        return min_i

    def update_food_connection(self, food_id):
        """
        update the connection of the food in the food graph
        :param food_id: the id of the food to be connected
        """
        if len(self.reached_food_ids) == 0:
            return
        self.nearest_connected_target = self.find_nearest_connected_food(food_id)
        if not self.dish.get_food_graph().has_edge(food_id, self.nearest_connected_target):
            self.dish.add_food_edge(food_id, self.nearest_connected_target)

    def update_target_food(self):
        """
        switch the target food
        """
        # set a target food
        remaining_food_ids = set(self.dish.get_all_foods().keys()) - self.reached_food_ids
        min_i = self.capital_slime.find_nearest_food(remaining_food_ids)[0]
        if min_i != self.current_target:
            self.current_target = (min_i, self.dish.get_food_position(min_i))
            # update the connection to the target food from reachable food
            self.nearest_connected_target = self.find_nearest_connected_food(min_i)
            # optional
            self.update_food_connection(min_i)

    def update_slime(self):
        """
        update statistics of the mould and
        update each slime after each evolution step of the mould
        """
        # update statistics after each evolution
        active_slime = [slime.pheromone for slime in list(self.slime_cells.values())
                        if slime.pheromone > 1]
        average_pheromone = np.average(active_slime)
        self.avg_ph.append(average_pheromone)
        self.total_num.append(len(self.slime_cells))
        self.total_active_num.append(len(active_slime))
        self.total_inactive_num.append(len(self.slime_cells) - len(active_slime))
        self.total_reached_foods.append(len(self.reached_food_ids))
        self.coverage_ratio.append(len(self.slime_cells)/self.dish.get_dish_size())

        if self.target_switch_count > TARGET_SWITCH_THRESHOLD or \
                self.capital_slime.get_reached_food_id() is not None or self.current_target[0] in self.reached_food_ids:
            self.target_switch_count = 0
            self.setup_capital_slime()
            self.update_target_food()

    def evolve(self):
        """
        the evolution step of the mould,
        every slime cell in the mould will take a step during each evolution step
        """
        previous_reached_foods = len(self.reached_food_ids)
        slime_idx = list(self.slime_cells.keys())
        for idx in slime_idx:
            self.dish.get_lattice()[idx].step(self.dish.get_lattice(), self.decay)
        if len(self.reached_food_ids) == previous_reached_foods:
            self.target_switch_count += 1
        self.update_slime()

    def get_current_target(self):
        return self.current_target

    def get_reached_food_ids(self):
        return self.reached_food_ids

    def get_avg_ph(self):
        return self.avg_ph

    def get_total_num(self):
        return self.total_num

    def get_total_active_num(self):
        return self.total_active_num

    def get_total_inactive_num(self):
        return self.total_inactive_num

    def get_coverage_ratio(self):
        return self.coverage_ratio

    def get_total_reached_foods(self):
        return self.total_reached_foods

    def get_nearest_connected_target(self):
        return self.nearest_connected_target

