import tkinter as tk
from tkinter import ttk
from .theme import COLORS, FONTS, apply_style, STYLES
from algorithms import ALGORITHM_CATEGORIES

class ControlPanel(tk.Frame):
    def __init__(self, parent, solve_callback, navigate_callback, play_pause_callback):
        super().__init__(parent, bg=COLORS["surface"])
        self.solve_callback = solve_callback
        self.navigate_callback = navigate_callback
        self.play_pause_callback = play_pause_callback
        
        self.selected_algorithm = tk.StringVar()
        self.animation_speed = tk.DoubleVar(value=0.5)
        self.is_running = False
        self.solution_info = {}
        
        self._create_widgets()
        
    def _create_widgets(self):
        main_frame = tk.Frame(self, bg=COLORS["surface"])
        main_frame.pack(fill="both", expand=True)
        
        left_column = tk.Frame(main_frame, bg=COLORS["surface"])
        left_column.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
        
        right_column = tk.Frame(main_frame, bg=COLORS["surface"])
        right_column.pack(side=tk.RIGHT, fill="both", expand=True, padx=5, pady=5)
        
        self.create_algorithm_section(left_column)
        
        control_group_frame = tk.Frame(left_column, bg=COLORS["surface"])
        control_group_frame.pack(fill="x", pady=5)
        self.control_group_frame = control_group_frame
        
        self.create_controls_section()
        self.create_info_section()
        self.create_navigation_section()
        
        self.create_paths_section(right_column)
        
        self.status_msg = tk.Label(left_column, text="", fg=COLORS["primary"])
        apply_style(self.status_msg, "label")
        self.status_msg.pack(fill="x", pady=5)
        
    def create_algorithm_section(self, parent):
        alg_frame = tk.Frame(parent, bg=COLORS["surface"])
        alg_frame.pack(fill="x", pady=5)
        
        heading = tk.Label(alg_frame, text="Algorithm Selection", anchor="w")
        apply_style(heading, "heading")
        heading.pack(fill="x", pady=5)
        
        notebook = ttk.Notebook(alg_frame)
        notebook.pack(fill="x", pady=5)
        
        for category, algs in ALGORITHM_CATEGORIES.items():
            tab = tk.Frame(notebook, bg=COLORS["surface"], padx=5, pady=5)
            notebook.add(tab, text=category)
            for alg in algs:
                rb = tk.Radiobutton(
                    tab, 
                    text=alg,
                    variable=self.selected_algorithm,
                    value=alg,
                    bg=COLORS["surface"],
                    fg=COLORS["on_surface"],
                    selectcolor=COLORS["primary_light"],
                    activebackground=COLORS["surface"],
                    font=FONTS["body"]
                )
                rb.pack(anchor="w", pady=2)
        
        self.selected_algorithm.set("BFS")
    
    def create_paths_section(self, parent):
        paths_frame = tk.Frame(parent, bg=COLORS["surface"])
        paths_frame.pack(fill="both", expand=True)
        
        heading = tk.Label(paths_frame, text="Explored Paths", anchor="w")
        apply_style(heading, "heading")
        heading.pack(fill="x", pady=5)
        
        text_frame = tk.Frame(paths_frame, bg=COLORS["surface"])
        text_frame.pack(fill="both", expand=True)
        
        h_scrollbar = ttk.Scrollbar(text_frame, orient="horizontal")
        h_scrollbar.pack(side=tk.BOTTOM, fill="x")
        
        v_scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
        v_scrollbar.pack(side=tk.RIGHT, fill="y")
        
        self.paths_text = tk.Text(
            text_frame, 
            height=10, 
            width=40, 
            font=FONTS["body"],
            wrap="none",
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set
        )
        self.paths_text.pack(side=tk.LEFT, fill="both", expand=True)
        
        h_scrollbar.config(command=self.paths_text.xview)
        v_scrollbar.config(command=self.paths_text.yview)
        
    def create_controls_section(self):
        control_frame = tk.Frame(self.control_group_frame, bg=COLORS["surface"])
        control_frame.pack(fill="x", pady=5)
        
        heading = tk.Label(control_frame, text="Controls", anchor="w")
        apply_style(heading, "heading")
        heading.pack(fill="x", pady=5)
        
        btn_frame = tk.Frame(control_frame, bg=COLORS["surface"])
        btn_frame.pack(fill="x", pady=2)
        
        self.solve_btn = tk.Button(
            btn_frame, 
            text="Solve",
            command=self.on_solve
        )
        apply_style(self.solve_btn, "button")
        self.solve_btn.pack(side="left", padx=2)
        
        speed_frame = tk.Frame(control_frame, bg=COLORS["surface"])
        speed_frame.pack(fill="x", pady=5)
        
        speed_label = tk.Label(speed_frame, text="Animation Speed:", anchor="w")
        apply_style(speed_label, "label")
        speed_label.pack(side="left")
        
        self.speed_scale = tk.Scale(
            speed_frame,
            from_=0.1,
            to=2.0,
            resolution=0.1,
            orient="horizontal",
            variable=self.animation_speed,
            bg=COLORS["surface"],
            highlightthickness=0,
            troughcolor=COLORS["primary_light"],
            activebackground=COLORS["primary"],
            sliderrelief="flat"
        )
        self.speed_scale.pack(side="left", fill="x", expand=True, padx=5)
        
    def create_navigation_section(self):
        nav_frame = tk.Frame(self.control_group_frame, bg=COLORS["surface"])
        nav_frame.pack(fill="x", pady=5)
        
        heading = tk.Label(nav_frame, text="Navigation", anchor="w")
        apply_style(heading, "heading")
        heading.pack(fill="x", pady=5)
        
        btn_frame = tk.Frame(nav_frame, bg=COLORS["surface"])
        btn_frame.pack(fill="x", pady=2)
        
        self.nav_buttons = {}
        self.nav_buttons["first"] = tk.Button(btn_frame, text="⏮", command=lambda: self.navigate_callback("first"), state="disabled")
        apply_style(self.nav_buttons["first"], "button")
        self.nav_buttons["first"].pack(side="left", padx=1)
        
        self.nav_buttons["prev"] = tk.Button(btn_frame, text="◀", command=lambda: self.navigate_callback("prev"), state="disabled")
        apply_style(self.nav_buttons["prev"], "button")
        self.nav_buttons["prev"].pack(side="left", padx=1)
        
        self.nav_buttons["play"] = tk.Button(btn_frame, text="▶", command=self.on_play_pause, state="disabled")
        apply_style(self.nav_buttons["play"], "secondary_button")
        self.nav_buttons["play"].pack(side="left", padx=1)
        
        self.nav_buttons["next"] = tk.Button(btn_frame, text="▶", command=lambda: self.navigate_callback("next"), state="disabled")
        apply_style(self.nav_buttons["next"], "button")
        self.nav_buttons["next"].pack(side="left", padx=1)
        
        self.nav_buttons["last"] = tk.Button(btn_frame, text="⏭", command=lambda: self.navigate_callback("last"), state="disabled")
        apply_style(self.nav_buttons["last"], "button")
        self.nav_buttons["last"].pack(side="left", padx=1)
    
    def create_info_section(self):
        info_frame = tk.Frame(self.control_group_frame, bg=COLORS["surface"])
        info_frame.pack(fill="x", padx=10, pady=5)
        
        heading = tk.Label(info_frame, text="Solution Information", anchor="w")
        apply_style(heading, "heading")
        heading.pack(fill="x", pady=5)
        
        self.info_labels = {}
        info_grid = tk.Frame(info_frame, bg=COLORS["surface"])
        info_grid.pack(fill="x", pady=2)
        
        info_fields = [
            ("Algorithm", "algorithm"), 
            ("Status", "status"),
            ("Steps", "steps"), 
            ("Current Step", "current_step"),
            ("Total Cost", "total_cost"), 
            ("Current Cost", "current_cost"),
            ("Execution Time", "execution_time"),  
            ("States Explored", "states_explored")
        ]
        
        for i, (label_text, key) in enumerate(info_fields):
            row = i // 2
            col = i % 2 * 2
            label = tk.Label(info_grid, text=f"{label_text}:", anchor="e", font=FONTS["small"])
            label.grid(row=row, column=col, sticky="e", padx=2, pady=1)
            value = tk.Label(info_grid, text="--", anchor="w", font=FONTS["small"])
            value.grid(row=row, column=col+1, sticky="w", padx=2, pady=1)
            self.info_labels[key] = value
            
        info_grid.columnconfigure(1, weight=1)
        info_grid.columnconfigure(3, weight=1)
    
    def update_paths(self, all_paths):
        self.paths_text.delete(1.0, tk.END)
        if not all_paths:
            self.paths_text.insert(tk.END, "No paths explored yet.")
            return
            
        max_display = 100
        paths_to_show = all_paths[:max_display]
        
        for i, (path, cost) in enumerate(paths_to_show):
            if i > 0:
                self.paths_text.insert(tk.END, "-" * 40 + "\n\n")
                
            self.paths_text.insert(tk.END, f"Path {i+1} (Cost: {cost}):\n\n")
            
            for state in path:
                self.paths_text.insert(tk.END, "\n")
                
                for row in state:
                    formatted_row = "  ".join(f"{num:2d}" if num != 0 else " _" for num in row)
                    self.paths_text.insert(tk.END, f"  {formatted_row}\n")
                
                self.paths_text.insert(tk.END, "\n")
            
            self.paths_text.insert(tk.END, "\n")
            
        if len(all_paths) > max_display:
            self.paths_text.insert(tk.END, f"...and {len(all_paths) - max_display} more paths (not shown).\n")
            
    def update_info(self, info_dict):
        self.solution_info.update(info_dict)
        for key, value in info_dict.items():
            if key in self.info_labels:
                self.info_labels[key].config(text=str(value))
                
    def enable_navigation(self, enable=True):
        state = "normal" if enable else "disabled"
        for button in self.nav_buttons.values():
            button.config(state=state)
        
    def lock_animation_speed(self, lock=True):
        if lock:
            self.speed_scale.config(state="disabled")
        else:
            self.speed_scale.config(state="normal")
        
    def on_solve(self):
        algorithm = self.selected_algorithm.get()
        if algorithm:
            self.status_msg.config(text=f"Solving with {algorithm}...")
            self.solve_callback(algorithm)
        else:
            self.status_msg.config(text="Please select an algorithm first!")
            
    def on_play_pause(self):
        if self.is_running:
            self.is_running = False
            self.set_play_pause_state(False)
        else:
            self.is_running = True
            self.set_play_pause_state(True)
        
        self.play_pause_callback(self.is_running)
        
    def set_play_pause_state(self, is_playing):
        self.is_running = is_playing
        if is_playing:
            self.nav_buttons["play"].config(text="⏸ Pause")
        else:
            self.nav_buttons["play"].config(text="▶ Play")