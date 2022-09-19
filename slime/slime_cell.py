import numpy as np
from slime.food import FoodCell


class SlimeCell:

    def __init__(self, idx: tuple, direction: int, pheromone: float, mould, city):
        """
        Initializes the Slime Cell
        :param self.idx: index of current slime cell
        :param direction:
                direction of SlimeCell; integer number between 0 and 8 inclusive
                where:
                    * 0 = no direction, i.e., no slime is present
                    * 1 = up
                    * 2 = upper-right diagonal
                    * 3 = right
                    * 4 = lower-right diagonal
                    * 5 = down
                    * 6 = lower-left diagonal
                    * 7 = left
                    * 8 = upper-left diagonal
        :param pheromone: pheromone level of SlimeCell, >0 <5
        """
        self.idx = idx
        self.direction = direction
        self.pheromone = pheromone
        self.mould = mould
        self.city = city
        self.food_id = None
        self.lookouts = self.get_lookouts
        self.step_direction = {
            1: (-1, 0),
            2: (-1, 1),
            3: (0, 1),
            4: (1, 1),
            5: (1, 0),
            6: (1, -1),
            7: (0, -1),
            8: (-1, -1)
        }

    def get_lookouts(self, sensor_offset):
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

    def neighbours(self):
        return [
            (self.idx[0] - 1, self.idx[1] - 1),  # up   1, left  1
            (self.idx[0] - 1, self.idx[1]),  # up   1,
            (self.idx[0] - 1, self.idx[1] + 1),  # up   1, right 1
            (self.idx[0], self.idx[1] - 1),  # , left  1
            (self.idx[0], self.idx[1] + 1),  # , right 1
            (self.idx[0] + 1, self.idx[1] - 1),  # down 1, left  1
            (self.idx[0] + 1, self.idx[1]),  # down 1,
            (self.idx[0] + 1, self.idx[1] + 1),  # down 1, right 1
        ]

    def diffusion(self, coverage, decay):
        """Diffusion Cellular Automaton."""
        neighbour_count = 0
        for neigh in self.neighbours():

            # continue if the neighbor is out of boundary
            if neigh[0] > self.city.lattice.shape[0] or neigh[0] < 0 \
                    or neigh[0] > self.city.lattice.shape[1] or neigh[1] < 0:
                continue

            # generate a slime cell on an empty neighbor,
            # if the generation is success: decay itself
            if self.city.lattice[neigh] is None:
                self.mould.slime_cell_generator(idx=neigh, coverage=1, decay=decay)
                ph = self.pheromone * decay
                if ph < 0.7:
                    return self.mould.remove_slime_cell(self.idx)
                self.pheromone = ph

            # neighbor is a slime cell
            elif isinstance(self.city.lattice[neigh], SlimeCell):
                neighbour_count += 1
                if self.pheromone < 4:
                    self.pheromone += 1

            # add pheromone if current cell find food nearby
            elif isinstance(self.city.lattice[neigh], FoodCell):
                self.pheromone = 8

        if neighbour_count <= 3 or neighbour_count >= 7:
            return self.mould.remove_slime_cell(self.idx)
        self.city.lattice[self.idx] = self
        return True

    def motor(self):
        slime_cell = None
        step = self.step_direction[self.direction]
        new_idx = (self.idx[0] + step[0], self.idx[1] + step[1])

        # if the new idx is out of boundary
        # return current cell with a new random direction
        if new_idx[0] > self.city.lattice.shape[0] or new_idx[0] < 0 \
                or new_idx[0] > self.city.lattice.shape[1] or new_idx[1] < 0:
            self.direction = np.random.choice(8) + 1
            self.city.lattice[self.idx] = self
            return self

        # move to a new place if it is none
        if self.city.lattice[new_idx] is None:
            self.mould.remove_slime_cell(self.idx)
            slime_cell = self.mould.slime_cell_generator(idx=new_idx, coverage=1)
            self.city.lattice[new_idx] = slime_cell

        # new place is a slime cell
        elif isinstance(self.city.lattice[new_idx], SlimeCell):
            if self.pheromone < 4:
                self.pheromone += 1
                # self.city.lattice[self.idx] = self

        # next location is food
        elif isinstance(self.city.lattice[new_idx], FoodCell):
            food = self.city.lattice[new_idx]
            # new food reached for mould
            if len(food.slime_cells) == 0:
                self.mould.reached_foods[food.food_id] = new_idx

            # new cell reached food
            if self.food_id is None or self.food_id != food.food_id:

                self.food_id = food.food_id

                if self.pheromone < 7:
                    self.pheromone += 1
                slime_cell = self.city.lattice[new_idx].append_slime_cell(self)
                self.mould.remove_slime_cell(self.idx)

        self.direction = np.random.choice(8) + 1
        return slime_cell

    def sensory(self, sensor_offset):
        if self.food_id is not None:
            sensors = []
            for i in self.lookouts(sensor_offset)[self.direction]:

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
        else:
            self.direction = np.random.choice(8) + 1

        self.city.lattice[self.idx] = self
        pass
