import tkinter as tk
import time
from tkinter import messagebox
from .control_panel import ControlPanel
from .puzzle_frame import PuzzleFrame
from constants import START_STATE, GOAL_STATE, WIDTH, HEIGHT
from algorithms.uninformed import bfs, dfs, ucs, ids
from algorithms.informed import greedy, astar, ida_star
from algorithms.local import simple_hill_climbing, stochastic_hill_climbing, simulated_annealing, beam_search, genetic_algorithm, steepest_ascent_hill_climbing
from algorithms.constraint import solve as backtracking_solve, solve_with_ac3
from algorithms.complex import and_or_graph_search, no_observation_belief_state_search, partially_observable_search
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
            "And-Or Graph Search": and_or_graph_search,
            "No-Observation Belief State Search": self.no_observable_search_adapter,
            "Partially Observable Search": self.partially_observable_search_adapter,
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
    
   
    def partially_observable_search_adapter(self, initial_state, goal_state):
    
        # Lấy phần nhìn thấy từ goal_matrix_entries (chỉ các ô bị khóa)
        visible_state = []
        for i in range(3):
            row = []
            for j in range(3):
                value = self.goal_matrix_entries[i][j].get().strip()
                if value and self.goal_matrix_entries[i][j].cget('state') == 'disabled':
                    try:
                        row.append(int(value))
                    except ValueError:
                        row.append(None)
                else:
                    row.append(None)
            visible_state.append(tuple(row))

        # Lấy tập trạng thái niềm tin và trạng thái mục tiêu từ listbox
        initial_states = self.get_states_from_listbox(self.belief_listbox)
        goal_states = self.get_states_from_listbox(self.goal_listbox)

        # Kiểm tra đầu vào
        if not initial_states or not goal_states:
            messagebox.showerror("Lỗi", "Vui lòng nhập ít nhất một trạng thái niềm tin và một mục tiêu niềm tin!")
            return None, None, []
        selected_belief = initial_states[0]  # Có thể thay bằng logic chọn từ belief_listbox
        self.start_state = selected_belief  # Cập nhật start_state để hiển thị trên puzzle_frame
        self.puzzle_frame.draw_state(self.start_state)  # Hiển thị trạng thái niềm tin trên puzzle_frame
        # Gọi hàm partially_observable_search
        path, costs, all_paths = partially_observable_search(visible_state, initial_states, goal_states)
        
        # Animate the resulting path for clarity
        if path:
            for idx, state in enumerate(path):
                prev = path[idx-1] if idx > 0 else state
                # draw current step
                self.puzzle_frame.draw_state(state)
                # highlight the move from prev→state
                self.puzzle_frame.show_move(prev, state)
                # force immediate repaint
                self.update_idletasks()
                self.update()
                # pause so you can actually see it
                time.sleep(0.4)
        
        return path, costs, all_paths

    def no_observable_search_adapter(self, initial_state, goal_state):

        initial_states = self.get_states_from_listbox(self.belief_listbox)
        goal_states = self.get_states_from_listbox(self.goal_listbox)

        # Kiểm tra đầu vào
        if not initial_states or not goal_states:
            messagebox.showerror("Lỗi", "Vui lòng nhập ít nhất một trạng thái niềm tin và một mục tiêu niềm tin!")
            return None, None, []
        selected_belief = initial_states[0]  # Có thể thay bằng logic chọn từ belief_listbox
        self.start_state = selected_belief  # Cập nhật start_state để hiển thị trên puzzle_frame
        self.puzzle_frame.draw_state(self.start_state)  # Hiển thị trạng thái niềm tin trên puzzle_frame
        # Gọi hàm partially_observable_search
        path, costs, all_paths = no_observation_belief_state_search(initial_states, goal_states)
        
        # Animate the resulting path for clarity
        if path:
            for idx, state in enumerate(path):
                prev = path[idx-1] if idx > 0 else state
                # draw current step
                self.puzzle_frame.draw_state(state)
                # highlight the move from prev→state
                self.puzzle_frame.show_move(prev, state)
                # force immediate repaint
                self.update_idletasks()
                self.update()
                # pause so you can actually see it
                time.sleep(0.4)
        
        return path, costs, all_paths
    
    def create_widgets(self):
        left_panel = tk.Frame(self, bg=COLORS["surface"])
        left_panel.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Frame cho 2 ma trận nhỏ nhập trạng thái niềm tin và mục tiêu niềm tin
        self.belief_matrices_frame = tk.Frame(left_panel, bg=COLORS["surface"])
        self.belief_matrices_frame.pack(fill="x", pady=5)
        # Ma trận nhỏ bên trái: trạng thái niềm tin
        belief_matrix_label = tk.Label(self.belief_matrices_frame, text="Trạng thái niềm tin:", bg=COLORS["surface"])
        apply_style(belief_matrix_label, "label")
        belief_matrix_label.grid(row=0, column=0, pady=2)
        self.belief_matrix_entries = []
        belief_matrix_frame = tk.Frame(self.belief_matrices_frame, bg=COLORS["surface"])
        belief_matrix_frame.grid(row=1, column=0, padx=5)
        for i in range(3):
            row_entries = []
            for j in range(3):
                entry = tk.Entry(belief_matrix_frame, width=5, font=('Arial', 12))  # Tăng kích thước ô nhập
                entry.grid(row=i, column=j, padx=2, pady=2)  # Tăng padding
                # Bind keyboard events
                entry.bind('<Return>', lambda e, row=i, col=j: self.handle_matrix_keypress(e, row, col, 'belief'))
                entry.bind('<Up>', lambda e, row=i, col=j: self.handle_matrix_keypress(e, row, col, 'belief'))
                entry.bind('<Down>', lambda e, row=i, col=j: self.handle_matrix_keypress(e, row, col, 'belief'))
                entry.bind('<Left>', lambda e, row=i, col=j: self.handle_matrix_keypress(e, row, col, 'belief'))
                entry.bind('<Right>', lambda e, row=i, col=j: self.handle_matrix_keypress(e, row, col, 'belief'))
                row_entries.append(entry)
            self.belief_matrix_entries.append(row_entries)
        # Nút lưu trạng thái niềm tin
        self.save_belief_btn = tk.Button(self.belief_matrices_frame, text="Thêm", command=self.save_belief_state, width=10, font=('Arial', 10))
        apply_style(self.save_belief_btn, "button")
        self.save_belief_btn.grid(row=2, column=0, pady=5)
        # Listbox lưu các trạng thái niềm tin đã nhập
        self.belief_listbox = tk.Listbox(self.belief_matrices_frame, height=8, width=35, font=('Arial', 10))  # Tăng width để hiển thị đầy đủ dãy số
        self.belief_listbox.grid(row=3, column=0, pady=5)
        # Thêm nút xóa trạng thái đã chọn
        self.delete_belief_btn = tk.Button(self.belief_matrices_frame, text="Xóa", command=self.delete_belief_state, width=10, font=('Arial', 10))
        apply_style(self.delete_belief_btn, "button")
        self.delete_belief_btn.grid(row=4, column=0, pady=5)

        # Ma trận nhỏ bên phải: mục tiêu niềm tin (kiêm phần nhìn thấy)
        goal_matrix_label = tk.Label(self.belief_matrices_frame, text="Mục tiêu niềm tin (kiêm phần nhìn thấy):", bg=COLORS["surface"])
        apply_style(goal_matrix_label, "label")
        goal_matrix_label.grid(row=0, column=1, pady=2)
        self.goal_matrix_entries = []
        goal_matrix_frame = tk.Frame(self.belief_matrices_frame, bg=COLORS["surface"])
        goal_matrix_frame.grid(row=1, column=1, padx=5)
        for i in range(3):
            row_entries = []
            for j in range(3):
                entry = tk.Entry(goal_matrix_frame, width=5, font=('Arial', 12))
                entry.grid(row=i, column=j, padx=2, pady=2)
                # Bind keyboard events
                entry.bind('<Return>', lambda e, row=i, col=j: self.handle_matrix_keypress(e, row, col, 'goal'))
                entry.bind('<Up>', lambda e, row=i, col=j: self.handle_matrix_keypress(e, row, col, 'goal'))
                entry.bind('<Down>', lambda e, row=i, col=j: self.handle_matrix_keypress(e, row, col, 'goal'))
                entry.bind('<Left>', lambda e, row=i, col=j: self.handle_matrix_keypress(e, row, col, 'goal'))
                entry.bind('<Right>', lambda e, row=i, col=j: self.handle_matrix_keypress(e, row, col, 'goal'))
                row_entries.append(entry)
            self.goal_matrix_entries.append(row_entries)

        # Frame chứa các nút
        button_frame = tk.Frame(self.belief_matrices_frame, bg=COLORS["surface"])
        button_frame.grid(row=2, column=1, pady=5)
        
        # Nút lưu phần nhìn thấy
        self.save_visible_btn = tk.Button(button_frame, text="Khóa", command=self.save_visible_part, width=10, font=('Arial', 10))
        apply_style(self.save_visible_btn, "button")
        self.save_visible_btn.pack(side=tk.LEFT, padx=5)
        
        # Nút lưu mục tiêu niềm tin
        self.save_goal_btn = tk.Button(button_frame, text="Thêm", command=self.save_goal_state, width=10, font=('Arial', 10))
        apply_style(self.save_goal_btn, "button")
        self.save_goal_btn.pack(side=tk.LEFT, padx=5)

        # Listbox lưu các mục tiêu niềm tin đã nhập
        self.goal_listbox = tk.Listbox(self.belief_matrices_frame, height=8, width=35, font=('Arial', 10))
        self.goal_listbox.grid(row=3, column=1, pady=5)
        # Thêm nút xóa mục tiêu đã chọn
        self.delete_goal_btn = tk.Button(self.belief_matrices_frame, text="Xóa", command=self.delete_goal_state, width=10, font=('Arial', 10))
        apply_style(self.delete_goal_btn, "button")
        self.delete_goal_btn.grid(row=4, column=1, pady=5)

        # Frame cho belief states và goal belief states (ẩn khi dùng ma trận)
        self.belief_states_frame = tk.Frame(left_panel, bg=COLORS["surface"])
        self.belief_states_frame.pack(fill="x", pady=5)
        self.belief_frame = tk.Frame(self.belief_states_frame, bg=COLORS["surface"])
        self.belief_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5)
        belief_label = tk.Label(self.belief_frame, text="Tập trạng thái niềm tin:", bg=COLORS["surface"])
        apply_style(belief_label, "label")
        belief_label.pack(pady=5)
        belief_help = tk.Label(self.belief_frame, text="Nhập nhiều trạng thái, mỗi trạng thái trên một dòng.", bg=COLORS["surface"], justify=tk.LEFT)
        apply_style(belief_help, "label")
        belief_help.pack(pady=5)
        self.belief_text = tk.Text(self.belief_frame, height=5, width=30)
        self.belief_text.pack(pady=5)
        self.goal_belief_frame = tk.Frame(self.belief_states_frame, bg=COLORS["surface"])
        self.goal_belief_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5)
        goal_belief_label = tk.Label(self.goal_belief_frame, text="Tập mục tiêu niềm tin:", bg=COLORS["surface"])
        apply_style(goal_belief_label, "label")
        goal_belief_label.pack(pady=5)
        goal_belief_help = tk.Label(self.goal_belief_frame, text="Nhập nhiều trạng thái mục tiêu, mỗi trạng thái trên một dòng.", bg=COLORS["surface"], justify=tk.LEFT)
        apply_style(goal_belief_help, "label")
        goal_belief_help.pack(pady=5)
        self.goal_belief_text = tk.Text(self.goal_belief_frame, height=5, width=30)
        self.goal_belief_text.pack(pady=5)
        # Ẩn các frame ban đầu
        self.belief_states_frame.pack_forget()
        self.belief_matrices_frame.pack_forget()
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
        self.puzzle_frame = PuzzleFrame(left_panel)
        self.puzzle_frame.pack(pady=10)
        self.puzzle_frame.draw_state(self.start_state)
        self.control_panel = ControlPanel(self, self.solve, self.navigate, self.play_pause)
        self.control_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.control_panel.selected_algorithm.trace_add("write", self.on_algorithm_change)
    
    def save_belief_state(self):
        # Kiểm tra ma trận có đủ số từ 0-8 không
        numbers = set()
        for i in range(3):
            for j in range(3):
                value = self.belief_matrix_entries[i][j].get().strip()
                if value and value.isdigit():
                    num = int(value)
                    if 0 <= num <= 8:
                        numbers.add(num)
        
        if len(numbers) != 9:
            messagebox.showerror("Lỗi", "Ma trận phải chứa đủ các số từ 0 đến 8!")
            return
            
        # Lưu trạng thái niềm tin từ ma trận vào listbox
        state = []
        for i in range(3):
            for j in range(3):
                value = self.belief_matrix_entries[i][j].get().strip()
                if value:
                    state.append(value)
                else:
                    state.append('None')
        # Thêm trạng thái mới vào listbox
        self.belief_listbox.insert('end', ','.join(state))
        # Xóa nội dung trong ma trận để nhập trạng thái mới
        self.clear_belief_matrix()

    def save_goal_state(self):
        # Kiểm tra ma trận có đủ số từ 0-8 không
        numbers = set()
        for i in range(3):
            for j in range(3):
                value = self.goal_matrix_entries[i][j].get().strip()
                if value and value.isdigit():
                    num = int(value)
                    if 0 <= num <= 8:
                        numbers.add(num)
        
        if len(numbers) != 9:
            messagebox.showerror("Lỗi", "Ma trận phải chứa đủ các số từ 0 đến 8!")
            return
            
        # Lưu mục tiêu niềm tin từ ma trận vào listbox
        state = []
        for i in range(3):
            for j in range(3):
                value = self.goal_matrix_entries[i][j].get().strip()
                if value:
                    state.append(value)
                else:
                    state.append('None')
        # Thêm trạng thái mới vào listbox
        self.goal_listbox.insert('end', ','.join(state))
        
        # Xóa nội dung trong ma trận nhưng giữ lại các ô đã bị khóa
        for i in range(3):
            for j in range(3):
                if self.goal_matrix_entries[i][j].cget('state') != 'disabled':
                    self.goal_matrix_entries[i][j].delete(0, tk.END)
                    self.goal_matrix_entries[i][j].config(state='normal')
        
        # Focus vào ô đầu tiên có thể nhập được
        for i in range(3):
            for j in range(3):
                if self.goal_matrix_entries[i][j].cget('state') == 'normal':
                    self.goal_matrix_entries[i][j].focus_set()
                    return

    def clear_belief_matrix(self):
        # Xóa nội dung trong ma trận belief
        for i in range(3):
            for j in range(3):
                self.belief_matrix_entries[i][j].delete(0, tk.END)
        # Focus vào ô đầu tiên
        self.belief_matrix_entries[0][0].focus_set()

    def clear_goal_matrix(self):
        """Xóa nội dung trong ma trận goal và mở khóa tất cả các ô"""
        for i in range(3):
            for j in range(3):
                self.goal_matrix_entries[i][j].config(state='normal')  # Mở khóa tất cả các ô
                self.goal_matrix_entries[i][j].delete(0, tk.END)
        # Enable lại nút Khóa khi reset ma trận
        self.save_visible_btn.config(state='normal')
        # Focus vào ô đầu tiên
        self.goal_matrix_entries[0][0].focus_set()

    def delete_belief_state(self):
        # Xóa trạng thái đã chọn trong listbox
        selected = self.belief_listbox.curselection()
        if selected:
            self.belief_listbox.delete(selected)

    def delete_goal_state(self):
        # Xóa mục tiêu đã chọn trong listbox
        selected = self.goal_listbox.curselection()
        if selected:
            self.goal_listbox.delete(selected)

    def on_algorithm_change(self, *args):
        algorithm_name = self.control_panel.selected_algorithm.get()
        complex_algorithms = [ "No Observation Belief State Search", "Partially Observable Search"]
        self.belief_states_frame.pack_forget()
        if algorithm_name in complex_algorithms:
            self.belief_matrices_frame.pack(fill="x", pady=5)
            self.input_frame.pack_forget()
        else:
            self.belief_matrices_frame.pack_forget()
            self.input_frame.pack(fill="x", pady=5)
    
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
    
    def solve(self, algorithm_name):
        # Nếu có trạng thái niềm tin, tự động hiển thị trạng thái đầu tiên lên ma trận phần nhìn thấy
        initial_text = self.belief_text.get("1.0", tk.END).strip()
        if initial_text:
            first_line = initial_text.split('\n')[0]
            if first_line.strip():
                values = [int(x.strip()) for x in first_line.split(',')]
                if len(values) == 9:
                    for i in range(3):
                        for j in range(3):
                            self.goal_matrix_entries[i][j].delete(0, tk.END)
                            self.goal_matrix_entries[i][j].insert(0, str(values[i*3+j]))
     
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

    def handle_matrix_keypress(self, event, row, col, matrix_type):
        """Handle keyboard navigation in matrix entries"""
        entries = self.belief_matrix_entries if matrix_type == 'belief' else self.goal_matrix_entries
        
        if event.keysym == 'Return':
            # Move to next cell or save state if at last cell
            if col < 2:
                next_col = col + 1
                while next_col < 3 and entries[row][next_col].cget('state') == 'disabled':
                    next_col += 1
                if next_col < 3:
                    entries[row][next_col].focus_set()
            elif row < 2:
                next_row = row + 1
                next_col = 0
                while next_row < 3:
                    while next_col < 3 and entries[next_row][next_col].cget('state') == 'disabled':
                        next_col += 1
                    if next_col < 3:
                        entries[next_row][next_col].focus_set()
                        break
                    next_row += 1
                    next_col = 0
            else:
                # At last cell, save the state
                if matrix_type == 'belief':
                    self.save_belief_state()
                else:
                    self.save_goal_state()
                # Focus back to first cell
                entries[0][0].focus_set()
                
        elif event.keysym == 'Up':
            if row > 0:
                prev_row = row - 1
                while prev_row >= 0 and entries[prev_row][col].cget('state') == 'disabled':
                    prev_row -= 1
                if prev_row >= 0:
                    entries[prev_row][col].focus_set()
                
        elif event.keysym == 'Down':
            if row < 2:
                next_row = row + 1
                while next_row < 3 and entries[next_row][col].cget('state') == 'disabled':
                    next_row += 1
                if next_row < 3:
                    entries[next_row][col].focus_set()
                
        elif event.keysym == 'Left':
            if col > 0:
                prev_col = col - 1
                while prev_col >= 0 and entries[row][prev_col].cget('state') == 'disabled':
                    prev_col -= 1
                if prev_col >= 0:
                    entries[row][prev_col].focus_set()
                
        elif event.keysym == 'Right':
            if col < 2:
                next_col = col + 1
                while next_col < 3 and entries[row][next_col].cget('state') == 'disabled':
                    next_col += 1
                if next_col < 3:
                    entries[row][next_col].focus_set()

    def save_visible_part(self):
        """Lưu phần nhìn thấy và khóa các ô đã nhập số từ 0-8"""
        # Kiểm tra và lưu các ô đã nhập số từ 0-8
        for i in range(3):
            for j in range(3):
                value = self.goal_matrix_entries[i][j].get().strip()
                if value and value.isdigit() and 0 <= int(value) <= 8:
                    # Khóa ô này
                    self.goal_matrix_entries[i][j].config(state='disabled')
                else:
                    # Mở khóa các ô khác
                    self.goal_matrix_entries[i][j].config(state='normal')
                    self.goal_matrix_entries[i][j].delete(0, tk.END)
        # Disable nút Khóa sau khi nhấn
        self.save_visible_btn.config(state='disabled')

    def get_states_from_listbox(self, listbox):
        """
        Chuyển mỗi dòng trong listbox thành một state 3×3 tuple.
        Ví dụ dòng "1,2,3,4,5,6,7,8,0" -> ((1,2,3),(4,5,6),(7,8,0))
        """
        states = []
        for line in listbox.get(0, tk.END):
            parts = [None if s.strip() == 'None' else int(s) for s in line.split(',')]
            # chia thành 3 hàng
            state = tuple(
                tuple(parts[i*3:(i+1)*3]) 
                for i in range(3)
            )
            states.append(state)
        return states

