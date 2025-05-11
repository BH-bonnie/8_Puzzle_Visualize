import tkinter as tk
import time
from tkinter import messagebox
from .control_panel import ControlPanel
from .puzzle_frame import PuzzleFrame
from constants import START_STATE, GOAL_STATE, WIDTH, HEIGHT
from algorithms.uninformed import bfs, dfs, ucs, ids
from algorithms.informed import greedy, astar, ida_star
from algorithms.local import simple_hill_climbing, stochastic_hill_climbing, simulated_annealing, beam_search, genetic_algorithm, steepest_ascent_hill_climbing
from algorithms.nondeterministic import and_or_graph_search
from algorithms.sensor_based import sensor_search, belief_state_search, no_observation_belief_state_search
from algorithms.constraint import solve as backtracking_solve, solve_with_ac3
from algorithms.utils import generate_random_state
from algorithms.Reforcement_learning import QLearning
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
            "Simple HC": simple_hill_climbing,
            "Stochastic HC": stochastic_hill_climbing,
            "Simulated Annealing": simulated_annealing,
            "Beam Search": beam_search,
            "Steepest Ascent HC": steepest_ascent_hill_climbing,
            "Genetic Algorithm": genetic_algorithm,
            "AND-OR Search": and_or_graph_search,
            "Sensor Search": sensor_search,
            "Belief State Search": self.belief_state_search_adapter,
            "No-Observation Belief State Search": self.no_observation_belief_state_search_adapter,
            "Backtracking": self.adapt_backtracking,
            "AC-3": self.adapt_ac3,
            "Forward Checking": self.adapt_forward_checking,
            "Q-Learning": self.q_learning_adapter
        }
        
        self.create_widgets()
    
    def adapt_backtracking(self, initial_state, goal_state):
        result = backtracking_solve(initial_state)
        
        if result['solution']:
            path = result['path']
            if path:
                from algorithms.utils import calculate_costs
                costs = calculate_costs(path)
                all_paths = [(path[:i+1], costs[i]) for i in range(len(path))]
                return path, costs, all_paths
            else:
                return None, None, []
        else:
            return None, None, []
    
    def adapt_forward_checking(self, initial_state, goal_state):
        result = backtracking_solve(initial_state)  # Using the same solver since Forward Checking is built into it
        
        if result['solution']:
            path = result['path']
            if path:
                from algorithms.utils import calculate_costs
                costs = calculate_costs(path)
                all_paths = [(path[:i+1], costs[i]) for i in range(len(path))]
                return path, costs, all_paths
            else:
                return None, None, []
        else:
            return None, None, []
    
    def adapt_ac3(self, initial_state, goal_state):        
        result = solve_with_ac3(initial_state)
        
        if result['solution'] is not None:
            path = result['path']
            
            costs = [i for i in range(len(path))]
            
            all_paths = [(path[:i+1], costs[i]) for i in range(len(path))]
            
            return path, costs, all_paths
        else:
            return [], [], []
    
    def belief_state_search_adapter(self, initial_state, goal_state):
        return belief_state_search(initial_state, goal_state)
    
    def no_observation_belief_state_search_adapter(self, initial_state, goal_state):
        # Sử dụng belief states đã nhập
        if not self.initial_beliefs or not self.goal_beliefs:
            messagebox.showerror("Error", "Vui lòng nhập belief states trước!")
            return None, None, []
            
        # Convert states to tuples for hashing
        initial_beliefs = [tuple(tuple(row) for row in state) for state in self.initial_beliefs]
        goal_beliefs = [tuple(tuple(row) for row in state) for state in self.goal_beliefs]
        
        # Mỗi trạng thái ban đầu là một belief state riêng biệt
        initial_beliefs = [set([state]) for state in initial_beliefs]
        goal_beliefs = [set(goal_beliefs)]  # Tất cả goal states trong một belief state
        
        # Run the algorithm
        path, costs, all_paths = no_observation_belief_state_search(initial_beliefs, goal_beliefs)
        
        # If no solution found, return empty results
        if path is None:
            return None, None, all_paths
            
        # Convert path back to list of states
        state_path = []
        for state in path:
            state_path.append(tuple(tuple(row) for row in state))
            
        return state_path, costs, all_paths
            
    def create_widgets(self):
        left_panel = tk.Frame(self, bg=COLORS["surface"])
        left_panel.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Frame cho belief states
        self.belief_frame = tk.Frame(left_panel, bg=COLORS["surface"])
        self.belief_frame.pack(fill="x", pady=5)
        
        # Label cho belief states
        belief_label = tk.Label(self.belief_frame, text="Trạng thái niềm tin ban đầu:", bg=COLORS["surface"])
        apply_style(belief_label, "label")
        belief_label.pack(pady=5)
        
        # Hướng dẫn nhập belief states
        belief_help = tk.Label(self.belief_frame, 
            text="Nhập nhiều trạng thái, mỗi trạng thái trên một dòng.", 
            bg=COLORS["surface"], justify=tk.LEFT)
        apply_style(belief_help, "label")
        belief_help.pack(pady=5)
        
        # Text area cho belief states
        self.belief_text = tk.Text(self.belief_frame, height=5, width=30)
        self.belief_text.pack(pady=5)
        
        # Frame cho goal belief states
        self.goal_belief_frame = tk.Frame(left_panel, bg=COLORS["surface"])
        self.goal_belief_frame.pack(fill="x", pady=5)
        
        # Label cho goal belief states
        goal_belief_label = tk.Label(self.goal_belief_frame, text="Mục tiêu niềm tin:", bg=COLORS["surface"])
        apply_style(goal_belief_label, "label")
        goal_belief_label.pack(pady=5)
        
        # Hướng dẫn nhập goal belief states
        goal_belief_help = tk.Label(self.goal_belief_frame, 
            text="Nhập nhiều trạng thái mục tiêu, mỗi trạng thái trên một dòng.", 
            bg=COLORS["surface"], justify=tk.LEFT)
        apply_style(goal_belief_help, "label")
        goal_belief_help.pack(pady=5)
        
        # Text area cho goal belief states
        self.goal_belief_text = tk.Text(self.goal_belief_frame, height=5, width=30)
        self.goal_belief_text.pack(pady=5)
        
        # Nút áp dụng belief states
        self.apply_belief_button = tk.Button(
            self.belief_frame,
            text="Áp dụng Belief States",
            command=self.apply_belief_states
        )
        apply_style(self.apply_belief_button, "button")
        self.apply_belief_button.pack(pady=5)
        
        # Ẩn belief frames ban đầu
        self.belief_frame.pack_forget()
        self.goal_belief_frame.pack_forget()
        self.apply_belief_button.pack_forget()
        
        # Frame cho input thông thường
        self.input_frame = tk.Frame(left_panel, bg=COLORS["surface"])
        self.input_frame.pack(fill="x", pady=5)
        
        input_label = tk.Label(self.input_frame, text="Enter 1D array (0-8):", bg=COLORS["surface"])
        apply_style(input_label, "label")
        input_label.pack(side=tk.LEFT, padx=5)
        
        self.array_input = tk.Entry(self.input_frame, width=15)
        self.array_input.pack(side=tk.LEFT, padx=5)
        self.array_input.insert(0, "2,6,5,0,8,7,4,3,1")  
        
        apply_button = tk.Button(
            self.input_frame,
            text="Apply Array",
            command=self.apply_array_input
        )
        apply_style(apply_button, "button")
        apply_button.pack(side=tk.LEFT, padx=5)
        
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
        
        # Khởi tạo belief states
        self.initial_beliefs = []
        self.goal_beliefs = []
        self.apply_belief_states()
        
        # Thêm callback cho việc thay đổi thuật toán
        self.control_panel.selected_algorithm.trace_add("write", self.on_algorithm_change)
    
    def on_algorithm_change(self, *args):
        algorithm_name = self.control_panel.selected_algorithm.get()
        if algorithm_name == "No-Observation Belief State Search":
            self.belief_frame.pack(fill="x", pady=5)
            self.goal_belief_frame.pack(fill="x", pady=5)
            self.apply_belief_button.pack(pady=5)
            self.input_frame.pack_forget()
        elif algorithm_name in ["Sensor Search", "Belief State Search"]:
            self.belief_frame.pack_forget()
            self.goal_belief_frame.pack_forget()
            self.apply_belief_button.pack_forget()
            self.input_frame.pack(fill="x", pady=5)
        else:
            self.belief_frame.pack_forget()
            self.goal_belief_frame.pack_forget()
            self.apply_belief_button.pack_forget()
            self.input_frame.pack(fill="x", pady=5)
    
    def apply_belief_states(self):
        try:
            # Đọc và xử lý initial belief states
            initial_text = self.belief_text.get("1.0", tk.END).strip()
            initial_states = []
            for line in initial_text.split('\n'):
                if line.strip():
                    values = [int(x.strip()) for x in line.split(',')]
                    if len(values) != 9:
                        raise ValueError("Mỗi state phải có đúng 9 số")
                    if sorted(values) != list(range(9)):
                        raise ValueError("Mỗi state phải chứa các số từ 0-8")
                    state = (
                        tuple(values[0:3]),
                        tuple(values[3:6]),
                        tuple(values[6:9])
                    )
                    initial_states.append(state)
            
            # Đọc và xử lý goal belief states
            goal_text = self.goal_belief_text.get("1.0", tk.END).strip()
            goal_states = []
            for line in goal_text.split('\n'):
                if line.strip():
                    values = [int(x.strip()) for x in line.split(',')]
                    if len(values) != 9:
                        raise ValueError("Mỗi state phải có đúng 9 số")
                    if sorted(values) != list(range(9)):
                        raise ValueError("Mỗi state phải chứa các số từ 0-8")
                    state = (
                        tuple(values[0:3]),
                        tuple(values[3:6]),
                        tuple(values[6:9])
                    )
                    goal_states.append(state)
            
            # Cập nhật belief states
            self.initial_beliefs = initial_states
            self.goal_beliefs = goal_states
            
            # Cập nhật trạng thái hiển thị
            if initial_states:
                self.start_state = initial_states[0]
                self.puzzle_frame.draw_state(self.start_state)
            
            self.reset_solution_data()
            self.control_panel.status_msg.config(text="Belief states đã được cập nhật!")
            
        except Exception as e:
            messagebox.showerror("Input Error", f"Lỗi khi nhập belief states: {str(e)}")
    
    def apply_array_input(self):
        try:
            input_text = self.array_input.get().strip()
            if ',' in input_text:
                values = [int(x.strip()) for x in input_text.split(',')]
            else:
                values = [int(x) for x in input_text.split()]
            
            # Validate input
            if len(values) != 9:
                messagebox.showerror("Input Error", "Please enter exactly 9 values (0-8)")
                return
            
            if sorted(values) != list(range(9)):
                messagebox.showerror("Input Error", "Input must contain exactly the numbers 0-8")
                return
            
            new_state = (
                tuple(values[0:3]),
                tuple(values[3:6]),
                tuple(values[6:9])
            )
            
            self.start_state = new_state
            self.puzzle_frame.draw_state(self.start_state)
            
            self.reset_solution_data()
            
            self.control_panel.status_msg.config(text="Initial state updated from 1D array.")
            
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input format: {str(e)}")
    
    def reset_solution_data(self):
        self.start_time = None
        self.execution_time = None
        self.is_playing = False
        self.path = None
        self.costs = None
        self.all_paths = None
        self.current_step = 0
        self.control_panel.enable_navigation(False)
        
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
    
    def randomize_state(self):
        self.start_state = generate_random_state()
        self.puzzle_frame.draw_state(self.start_state)
        self.reset_solution_data()
        self.control_panel.status_msg.config(text="Initial state randomized. Ready to solve.")
        
        flat_state = [num for row in self.start_state for num in row]
        self.array_input.delete(0, tk.END)
        self.array_input.insert(0, ",".join(str(num) for num in flat_state))
        
    def solve(self, algorithm_name):
        # Kiểm tra và hiển thị/ẩn belief states dựa trên thuật toán
        if algorithm_name in ["Sensor Search", "Belief State Search", "No-Observation Belief State Search"]:
            self.belief_frame.pack(fill="x", pady=5)
            self.goal_belief_frame.pack(fill="x", pady=5)
            self.apply_belief_button.pack(pady=5)
            self.input_frame.pack_forget()  # Ẩn phần input array
        else:
            self.belief_frame.pack_forget()
            self.goal_belief_frame.pack_forget()
            self.apply_belief_button.pack_forget()
            self.input_frame.pack(fill="x", pady=5)  # Hiện phần input array
            
        self.control_panel.status_msg.config(text=f"Đang giải với thuật toán {algorithm_name}...")
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
            if self.current_step >= len(self.path) - 1:
                self.is_playing = False
                self.control_panel.set_play_pause_state(False)
                self.control_panel.status_msg.config(text="Playback complete!")
            elif not self.is_playing:
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
                "execution_time": f"{self.execution_time:.2f}s" if self.execution_time else "0.00s",  
                "states_explored": len(self.all_paths) if self.all_paths else 0
            }
            self.control_panel.update_info(info)
            self.control_panel.update_paths(self.all_paths if self.all_paths else [])
    
    def q_learning_adapter(self, initial_state, goal_state):
        # Tạo instance của QLearning
        agent = QLearning()
        
        # Tạo môi trường giả lập
        class PuzzleEnvironment:
            def __init__(self, initial_state, goal_state):
                self.state = initial_state
                self.goal_state = goal_state
                
            def reset(self):
                self.state = initial_state
                return self.state
                
            def get_possible_actions(self):
                from algorithms.utils import get_neighbors
                return get_neighbors(self.state)
                
            def step(self, action):
                self.state = action
                reward = -1 if self.state != self.goal_state else 100
                done = self.state == self.goal_state
                return self.state, reward, done
        
        env = PuzzleEnvironment(initial_state, goal_state)
        
        # Huấn luyện agent
        agent.train(env, num_episodes=1000)
        
        # Tìm đường đi tốt nhất
        path = [initial_state]
        costs = [0]
        all_paths = [(path[:], 0)]
        current_state = initial_state
        
        while current_state != goal_state:
            possible_actions = env.get_possible_actions()
            if not possible_actions:
                return None, None, all_paths
                
            action = agent.get_best_action(current_state, possible_actions)
            current_state = action
            path.append(current_state)
            
            # Tính toán chi phí
            from algorithms.utils import get_move_direction
            from constants import MOVE_COSTS
            direction = get_move_direction(path[-2], current_state)
            new_cost = costs[-1] + (MOVE_COSTS[direction] if direction else 0)
            costs.append(new_cost)
            all_paths.append((path[:], new_cost))
            
            # Kiểm tra vòng lặp vô hạn
            if len(path) > 100:
                return None, None, all_paths
        
        return path, costs, all_paths

