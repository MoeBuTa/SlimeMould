import random

import numpy as np
from slime.slime_cell import SlimeCell


class Mould:
    def __init__(self, city, mould_shape: tuple, coverage: float, decay: float, sensor_offset: int):
        # super().__init__(shape=mould_shape)
        self.city = city
        self.coverage = coverage
        self.decay = decay
        self.sensor_offset = sensor_offset
        self.slime_cells = {}
        self.reached_foods = {}
        self.mould_shape = mould_shape
        self.initialise(city, mould_shape, coverage)

    def remove_slime_cell(self, idx):
        self.city.lattice[idx] = None
        del self.slime_cells[idx]
        return False

    def slime_cell_generator(self, idx, coverage=0.6, decay=1):
        """
        "coverage" chance of successfully generate a slime cell
        """
        slime_cell = None
        direction = np.random.choice(a=9, p=[1 - coverage] + [coverage / 8] * 8)
        if direction > 0:
            pheromone = 2. * decay if direction > 0 else 0.
            slime_cell = SlimeCell(idx=idx, direction=direction, pheromone=pheromone, mould=self, city=self.city)
            self.slime_cells[slime_cell.idx] = slime_cell
        return slime_cell

    def initialise(self, city, mould_shape, coverage):
        row = mould_shape[0] // 2
        col = mould_shape[1] // 2
        for x in range(len(city.lattice) // 2 - row, len(city.lattice) // 2 + row):
            for y in range(len(city.lattice[x]) // 2 - col, len(city.lattice[x]) // 2 + col):
                slime_cell = self.slime_cell_generator(idx=(x, y), coverage=coverage)
                city.lattice[x][y] = slime_cell

    def evolve(self):
        """
        * The diffusion stage: all pheromones undergo diffusion
        * The motor stage: all slime cells determine if they can move forward or not
        * The sensory stage: all slime cells adjust their direction based on the pheromones
        :return:
        """
        print(len(self.slime_cells))
        keys = list(self.slime_cells.keys())
        for k in keys:
            cell = self.slime_cells.get(k)
            if cell.diffusion(coverage=self.coverage, decay=self.decay):
                new_cell = cell.motor()
                if new_cell is None:
                    continue
                else:
                    cell.sensory(self.sensor_offset)
            else:
                continue

        # foods = list(self.city.all_foods.keys())
        # for food_id in foods:
        #     food = self.city.all_foods.get(food_id)
        #     for cell in food.get_all_slime_cells():
        #         if cell.diffusion(decay=self.decay):
        #             new_cell = cell.motor()
        #             if new_cell is None:
        #                 continue
        #             else:
        #                 cell.sensory(self.sensor_offset)
        #         else:
        #             continue
