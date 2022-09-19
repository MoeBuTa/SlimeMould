import numpy as np
import random
from slime.slime import SlimeCell
from slime.cell import Cell


class Mould:
    def __init__(self, city, mould_shape: tuple, init_mould_coverage: float, decay: float, sensor_offset: int):
        self.city = city
        self.decay = decay
        self.sensor_offset = sensor_offset
        self.slime_cells = {}
        self.mould_shape = mould_shape
        self.initialise(city, mould_shape, init_mould_coverage)

    def remove_slime_cell(self, idx):
        self.city.set_lattice(idx, Cell())
        del self.slime_cells[idx]
        return False

    def update_slime_cell(self, idx, slime: SlimeCell):
        self.slime_cells[idx] = slime
        self.city.set_lattice(idx, slime)

    def slime_cell_generator(self, idx, decay=0):
        pheromone = 2. * (1 - decay)
        direction = random.randint(1, 8)
        slime_cell = SlimeCell(idx=idx, pheromone=pheromone, direction=direction, mould=self, city=self.city)
        self.slime_cells[slime_cell.idx] = slime_cell
        return slime_cell

    def initialise(self, city, mould_shape, init_mould_coverage):
        row = mould_shape[0] // 2
        col = mould_shape[1] // 2
        for x in range(len(city.lattice) // 2 - row, len(city.lattice) // 2 + row):
            for y in range(len(city.lattice[x]) // 2 - col, len(city.lattice[x]) // 2 + col):
                if random.random() < init_mould_coverage and (x, y) not in self.city.get_foods_idx():
                    slime_cell = self.slime_cell_generator(idx=(x, y))
                    city.lattice[x][y] = slime_cell

    def evolve(self):
        """
        * The diffusion stage: all pheromones undergo diffusion
        * The motor stage: all slime cells determine if they can move forward or not
        * The sensory stage: all slime cells adjust their direction based on the pheromones
        :return:
        """
        print(len(self.slime_cells))
        slimes = list(self.slime_cells.values())
        for cell in slimes:
            cell.step(self.city.get_lattice(), self.decay, self.sensor_offset)
