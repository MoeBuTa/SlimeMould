from slime.food import FoodCell
from slime.mould import Mould
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import pandas as pd
from slime.cell import Cell


class City:
    def __init__(self, city_shape: tuple, foods: pd.DataFrame, mould_shape: tuple,
                 coverage: float, decay: float, sensor_offset: int):
        self.lattice = self.initialise_city(city_shape)
        self.all_foods = {}
        self.initialise_food(foods)
        self.mould = self.initialise_slime_mould(self, mould_shape, coverage, decay, sensor_offset)

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
        for i, food in foods.iterrows():
            idx = (food['x'], food['y'])
            value = food['value']
            for x in range(value):
                for y in range(value):
                    food_idx = (idx[0] + y, idx[1] + x)
                    food = FoodCell(food_id=i, food_idx=food_idx, capacity=10*value)
                    self.lattice[food_idx] = food
                    if i not in self.all_foods:
                        self.all_foods[i] = [food_idx]
                    else:
                        self.all_foods[i].append(food_idx)

    def get_foods(self, food_id):
        return self.all_foods.get(food_id)

    @staticmethod
    def initialise_slime_mould(city, mould_shape, coverage, decay, sensor_offset):
        return Mould(city, mould_shape, coverage, decay, sensor_offset)

    @staticmethod
    def pheromones(lattice):
        """
        Returns a lattice of just the pheromones
        """
        pheromones = np.zeros_like(lattice, dtype=float)
        for i in np.ndindex(lattice.shape):
            if lattice[i] is None:
                pheromones[i] = 0.
            else:
                pheromones[i] = lattice[i].pheromone
        return pheromones

    def draw(self, cmap='YlOrRd'):
        """Draws the cells."""

        return plt.imshow(self.pheromones(self.lattice),
                          cmap=cmap,
                          alpha=0.7,
                          vmin=0, vmax=9,
                          interpolation='none',
                          origin='lower')

    def animate(self, frames=10, interval=200, filename=None):
        """
        Returns an animation
        """
        fig = plt.figure(figsize=(20, 10))

        im = self.draw()
        plt.axis("tight")
        plt.axis("image")
        ax = plt.gca()
        ax.set_xticks(np.arange(-.5, len(self.lattice), 1))
        ax.set_yticks(np.arange(-.5, len(self.lattice), 1))
        plt.tick_params(which='both',
                        bottom=False,
                        top=False,
                        left=False,
                        right=False,
                        labelbottom=False,
                        labelleft=False)

        def func(frame):
            self.mould.evolve()
            im.set_data(self.pheromones(self.lattice))
            return [im]

        ani = FuncAnimation(fig, func, frames=frames, blit=True, interval=interval)
        fps = 1 / (interval / 1000)
        filename is not None and ani.save(filename, dpi=150, writer=PillowWriter(fps=fps))
        return ani
