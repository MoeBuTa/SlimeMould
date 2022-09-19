class Cell:
    def __init__(self, pheromone=0., cell_type=0):
        self.pheromone = pheromone
        self.cell_type = cell_type

    def get_cell_type(self):
        return self.cell_type

