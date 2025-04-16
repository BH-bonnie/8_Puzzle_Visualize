import tkinter as tk
from constants import SIZE, GRID_SIZE, PINK, WHITE  

class PuzzleGrid(tk.Canvas):
    def __init__(self, master):
        super().__init__(master, width=SIZE*GRID_SIZE, height=SIZE*GRID_SIZE, bg=WHITE)
        self.grid_size = GRID_SIZE
        self.size = SIZE

    def draw(self, state):
        self.delete("all")
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x, y = j * self.size, i * self.size
                self.create_rectangle(x, y, x + self.size, y + self.size, fill=PINK, outline=WHITE)
                if state[i][j] != 0:
                    self.create_text(x + self.size/2, y + self.size/2, text=str(state[i][j]), font=("Arial", 24), fill=WHITE)