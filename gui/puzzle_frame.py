import tkinter as tk
from .theme import COLORS, FONTS, apply_style

class PuzzleFrame(tk.Frame):
    def __init__(self, parent, size=90, grid_size=3):  
        super().__init__(parent, bg=COLORS["surface"])
        self.size = size
        self.grid_size = grid_size
        self.tiles = {}
        self.current_state = None
        
        self.canvas = tk.Canvas(
            self, 
            width=self.size * self.grid_size,
            height=self.size * self.grid_size,
            bg=COLORS["background"],
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)  
        
        self.direction_label = tk.Label(self, text="", bg=COLORS["surface"])
        apply_style(self.direction_label, "label")
        self.direction_label.pack(pady=5)

    def draw_state(self, state):
        self.current_state = state
        self.canvas.delete("all")
        
        self.canvas.create_rectangle(
            0, 0, 
            self.size * self.grid_size, 
            self.size * self.grid_size,
            width=2, 
            outline=COLORS["primary"]
        )
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                value = state[i][j]
                if value != 0:
                    x0, y0 = j * self.size, i * self.size
                    x1, y1 = x0 + self.size, y0 + self.size
                    
                    tile = self.canvas.create_rectangle(
                        x0 + 2, y0 + 2, 
                        x1 - 2, y1 - 2,
                        fill=COLORS["tile"],
                        outline=COLORS["primary_dark"],
                        width=2
                    )
                    
                    text = self.canvas.create_text(
                        (x0 + x1) // 2,
                        (y0 + y1) // 2,
                        text=str(value),
                        fill=COLORS["on_primary"],
                        font=FONTS["tile"]
                    )
                    
                    self.tiles[value] = (tile, text)
                else:
                    x0, y0 = j * self.size, i * self.size
                    x1, y1 = x0 + self.size, y0 + self.size
                    
                    self.canvas.create_rectangle(
                        x0 + 2, y0 + 2, 
                        x1 - 2, y1 - 2,
                        fill=COLORS["empty_tile"],
                        outline=COLORS["primary_light"],
                        width=1,
                        dash=(4, 4)
                    )
                    
    def show_move(self, prev_state, curr_state):
        from algorithms.utils import get_move_direction
        direction = get_move_direction(prev_state, curr_state)
        if direction:
            self.direction_label.config(text=f"Move: {direction.upper()}")
        else:
            self.direction_label.config(text="")