from slime.food import FoodCell
from slime.mould import Mould
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import pandas as pd
from slime.cell import Cell


class City:
    def __init__(self, city_shape: tuple, foods: pd.DataFrame, mould_shape: tuple, init_mould_coverage: float,
                 decay: float):
        self.lattice = self.initialise_city(city_shape)
        self.all_foods = {}
        self.all_foods_idx = []
        self.all_corner_foods = {}
        self.initialise_food(foods)
        self.mould = self.initialise_slime_mould(self, mould_shape, init_mould_coverage, decay)

    @staticmethod
    def initialise_city(city_shape):
        lattice = np.empty(city_shape, object)
        for i in np.ndindex(city_shape):
            lattice[i] = Cell()
        return lattice

    def initialise_food(self, foods):
        """
        Adds food cells in a square with length size
        """
        for i, station in foods.iterrows():
            idx = (station['x'], station['y'])
            value = station['value']
            # add corner foods
            if station['type'] is not 'False':
                self.all_corner_foods[station['type']] = i

            for x in range(value//2):
                for y in range(value//2):
                    food_idx = (idx[0] - x, idx[1] - y)
                    food = FoodCell(food_id=i, food_idx=food_idx, food_type=station['type'])
                    self.lattice[food_idx] = food

                    # add food idx
                    self.all_foods_idx.append(food_idx)

                    # add all foods
                    if i not in self.all_foods:
                        self.all_foods[i] = [food]
                    else:
                        self.all_foods[i].append(food)

    @staticmethod
    def initialise_slime_mould(city, mould_shape, init_mould_coverage, decay):
        return Mould(city, mould_shape, init_mould_coverage, decay)

    @staticmethod
    def foods(lattice):
        food_list = []
        foods = np.zeros_like(lattice, dtype=float)
        for i in np.ndindex(lattice.shape):
            if lattice[i].get_cell_type() == 2 and lattice[i].get_food_id() not in food_list:
                foods[i] = lattice[i].get_food_id()
                food_list.append(lattice[i].get_food_id())
        return foods

    def draw_foods(self):
        fig, ax = plt.subplots(figsize=(15, 10))
        data = self.foods(self.lattice)
        dataT = data.T

        for (i, j), z in np.ndenumerate(data):
            if data[i][j] != 0:
                ax.text(i, j, '{}'.format(int(z)), ha='center', va='center', size=5)
        ax.imshow(dataT, cmap='YlOrRd', interpolation='none',
                  origin='lower', extent=[0, dataT.shape[1], 0, dataT.shape[0]])
        plt.savefig("output/test.png")
        plt.show()

    @staticmethod
    def pheromones(lattice):
        """
        Returns a lattice of just the pheromones
        """
        pheromones = np.zeros_like(lattice, dtype=float)
        for i in np.ndindex(lattice.shape):
            pheromones[i] = lattice[i].pheromone
        return pheromones

    def draw_pheromones(self, cmap='YlOrRd'):
        """Draws the cells."""
        data = self.pheromones(self.lattice)
        data = data.T

        return plt.imshow(self.pheromones(self.lattice),
                              cmap=cmap,
                              vmin=0, vmax=10,
                              interpolation='none',
                              origin='lower', extent=[0, data.shape[1], 0, data.shape[0]])

    def animate(self, frames=10, interval=200, filename=None):
        """
        Returns an animation
        """
        fig = plt.figure(figsize=(10, 15))

        im = self.draw_pheromones()
        # plt.axis("tight")
        # plt.axis("image")
        # plt.tick_params(which='both',
        #                 bottom=False,
        #                 top=False,
        #                 left=False,
        #                 right=False,
        #                 labelbottom=False,
        #                 labelleft=False)

        def func(frame):
            self.mould.evolve()
            im.set_data(self.pheromones(self.lattice).T)
            return [im]

        ani = FuncAnimation(fig, func, frames=frames, blit=True, interval=interval)
        fps = 1 / (interval / 1000)
        filename is not None and ani.save(filename, dpi=150, writer=PillowWriter(fps=fps))
        return ani

    def get_all_foods_idx(self):
        return self.all_foods_idx

    def get_all_foods(self):
        return self.all_foods

    def get_all_corner_foods(self):
        return self.all_corner_foods

    def get_lattice(self):
        return self.lattice

    def set_lattice(self, idx, obj):
        self.lattice[idx] = obj
