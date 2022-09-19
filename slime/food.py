from collections import deque
from slime.cell import Cell


class FoodCell(Cell):
    def __init__(self, food_id: int, food_idx: tuple, capacity=10):
        super().__init__(pheromone=10., cell_type=2)
        self.food_id = food_id
        self.food_idx = food_idx
        self.pheromone = 10.
        self.slime_cells = deque()
        self.capacity = capacity

    def append_slime_cell(self, slime_cell):
        if len(self.slime_cells) >= self.capacity:
            self.slime_cells.pop()
        self.slime_cells.append(slime_cell.idx)
        return slime_cell

    def get_all_slime_cells(self):
        return list(self.slime_cells)
