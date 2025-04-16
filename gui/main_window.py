import tkinter as tk
import time
from .control_panel import ControlPanel
from .puzzle_frame import PuzzleFrame
from constants import START_STATE, GOAL_STATE, WIDTH, HEIGHT
from algorithms.uninformed import bfs, dfs, ucs, ids
from algorithms.informed import greedy, astar, ida_star
from algorithms.local import hill_climbing, stochastic_hill_climbing, simple_hill_climbing, simulated_annealing, beam_search
from algorithms.utils import generate_random_state
from .theme import COLORS, apply_style

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("8-Puzzle Solver")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.configure(bg=COLORS["background"])
        
        self.start_state = START_STATE
        self.goal_state = GOAL_STATE
        self.current_step = 0
        self.path = None
        self.costs = None
        self.all_paths = None
        self.start_time = None
        self.execution_time = None  
        self.is_playing = False
        
        self.algorithms = {
            "BFS": bfs,
            "DFS": dfs,
            "UCS": ucs,
            "IDS": ids,
            "Greedy": greedy,
            "A*": astar,
            "IDA*": ida_star,
            "Hill Climbing": hill_climbing,
            "Stochastic HC": stochastic_hill_climbing,
            "Simple HC": simple_hill_climbing,
            "Simulated Annealing": simulated_annealing,
            "Beam Search": beam_search
        }
        
        self.create_widgets()
        
    def create_widgets(self):
        left_panel = tk.Frame(self, bg=COLORS["surface"])
        left_panel.pack(side=tk.LEFT, padx=20, pady=20)
        
        random_button = tk.Button(
            left_panel,
            text="Randomize Initial State",
            command=self.randomize_state
        )
        apply_style(random_button, "secondary_button")
        random_button.pack(pady=10)
        
        self.puzzle_frame = PuzzleFrame(left_panel)
        self.puzzle_frame.pack(pady=10)
        self.puzzle_frame.draw_state(self.start_state)
        
        self.control_panel = ControlPanel(self, self.solve, self.navigate, self.play_pause)
        self.control_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def randomize_state(self):
        """Set a random initial state for the puzzle"""
        self.start_time = None
        self.execution_time = None
        self.is_playing = False
        
        self.start_state = generate_random_state()
        self.puzzle_frame.draw_state(self.start_state)
        self.path = None
        self.costs = None
        self.all_paths = None
        self.current_step = 0
        self.control_panel.enable_navigation(False)
        self.control_panel.status_msg.config(text="Initial state randomized. Ready to solve.")
        
        info = {
            "algorithm": self.control_panel.selected_algorithm.get(),
            "status": "Not Started",
            "steps": 0,
            "current_step": 0,
            "total_cost": 0,
            "current_cost": 0,
            "execution_time": "0.00s",  
            "states_explored": 0
        }
        self.control_panel.update_info(info)
        self.control_panel.update_paths([])
        
    def solve(self, algorithm_name):
        self.control_panel.status_msg.config(text=f"Solving with {algorithm_name}...")
        self.update()  
        
        self.start_time = time.time()
        
        self.path, self.costs, self.all_paths = self.algorithms[algorithm_name](self.start_state, self.goal_state)
        
        self.execution_time = time.time() - self.start_time
        
        self.current_step = 0
        self.update_display()
        self.control_panel.enable_navigation(self.path is not None)
        self.control_panel.status_msg.config(text=f"Solution found in {self.execution_time:.2f}s!" if self.path else "No solution found!")
        
    def navigate(self, direction):
        if not self.path:
            return
            
        if direction == "first":
            self.current_step = 0
        elif direction == "prev" and self.current_step > 0:
            self.current_step -= 1
        elif direction == "next" and self.current_step < len(self.path) - 1:
            self.current_step += 1
        elif direction == "last":
            self.current_step = len(self.path) - 1
            
        self.update_display()
        
    def play_pause(self, is_playing):
        self.is_playing = is_playing
        
        if is_playing and self.path:
            self.auto_step()
        
    def auto_step(self):
        if self.is_playing and self.current_step < len(self.path) - 1:
            self.current_step += 1
            self.update_display()
            delay = int(self.control_panel.animation_speed.get() * 1000)
            self.after(delay, self.auto_step)
        else:
            # When playback finishes or is stopped
            if self.current_step >= len(self.path) - 1:
                # Reached the end of solution
                self.is_playing = False
                self.control_panel.set_play_pause_state(False)
                self.control_panel.status_msg.config(text="Playback complete!")
            elif not self.is_playing:
                # User stopped playback
                self.control_panel.set_play_pause_state(False)
            
    def update_display(self):
        if self.path:
            prev_state = self.path[max(0, self.current_step - 1)] if self.current_step > 0 else self.path[0]
            self.puzzle_frame.draw_state(self.path[self.current_step])
            self.puzzle_frame.show_move(prev_state, self.path[self.current_step])
            total_steps = len(self.path) - 1
            total_cost = self.costs[-1] if self.costs else 0
            
            info = {
                "algorithm": self.control_panel.selected_algorithm.get(),
                "status": "Solved" if self.path else "No Solution",
                "steps": total_steps,
                "current_step": self.current_step,
                "total_cost": total_cost,
                "current_cost": self.costs[self.current_step],
                "execution_time": f"{self.execution_time:.2f}s",  
                "states_explored": len(self.all_paths)
            }
            self.control_panel.update_info(info)
            self.control_panel.update_paths(self.all_paths)
        else:
            self.puzzle_frame.draw_state(self.start_state)
            info = {
                "algorithm": self.control_panel.selected_algorithm.get(),
                "status": "No Solution",
                "steps": 0,
                "current_step": 0,
                "total_cost": 0,
                "current_cost": 0,
                "execution_time": "0.00s",  
                "states_explored": len(self.all_paths) if self.all_paths else 0
            }
            self.control_panel.update_info(info)
            self.control_panel.update_paths(self.all_paths if self.all_paths else [])