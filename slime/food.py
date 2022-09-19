from collections import deque


class FoodCell:
    def __init__(self, food_id: int, food_idx: tuple, capacity=10):
        self.food_id = food_id
        self.food_idx = food_idx
        self.pheromone = 10.
        self.direction = 9
        self.slime_cells = deque()
        self.capacity = capacity

    def append_slime_cell(self, slime_cell):
        if len(self.slime_cells) >= self.capacity:
            self.slime_cells.pop()
        self.slime_cells.append(slime_cell.idx)
        return slime_cell

    def get_all_slime_cells(self):
        return list(self.slime_cells)
