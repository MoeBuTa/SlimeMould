from collections import deque
from slime.cell import Cell


class FoodCell(Cell):
    def __init__(self, food_id: int, food_idx: tuple):
        super().__init__(pheromone=10., cell_type=2)
        self.food_id = food_id
        self.food_idx = food_idx
        self.pheromone = 10.

    def get_food_idx(self):
        return self.food_idx

    def get_food_id(self):
        return self.food_id
