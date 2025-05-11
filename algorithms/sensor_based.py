import random
from collections import deque
from .utils import get_neighbors, get_move_direction, calculate_costs
from .informed import heuristic
from constants import MOVE_COSTS
import tkinter as tk
from tkinter import messagebox

def sensor_search(start, goal_state, max_steps=500):
    current_state = start
    path = [current_state]
    costs = [0]
    visited = {current_state}
    all_paths = [(path[:], 0)]
    
    recent_memory = deque(maxlen=10)
    recent_memory.append(current_state)
    
    steps_since_improvement = 0
    best_h_so_far = heuristic(current_state, goal_state)
    
    for _ in range(max_steps):
        if current_state == goal_state:
            return path, calculate_costs(path), all_paths
            
        neighbors = get_neighbors(current_state)
        unvisited = [n for n in neighbors if n not in visited]
        
        if not unvisited:
            unvisited = [n for n in neighbors if n not in recent_memory]
            
        if not unvisited:
            random_neighbors = [n for n in neighbors if n not in path[-5:]]  
            if random_neighbors:
                next_state = random.choice(random_neighbors)
            else:
                next_state = random.choice(neighbors)
        else:
            neighbor_scores = [(heuristic(n, goal_state), n) for n in unvisited]
            neighbor_scores.sort()  
            
            if steps_since_improvement < 5:
                next_state = neighbor_scores[0][1]
            else:
                candidates = [n for _, n in neighbor_scores[:min(3, len(neighbor_scores))]]
                next_state = random.choice(candidates)
                
        direction = get_move_direction(current_state, next_state)
        step_cost = MOVE_COSTS[direction] if direction else 0
        new_cost = costs[-1] + step_cost
        
        current_state = next_state
        path.append(current_state)
        costs.append(new_cost)
        visited.add(current_state)
        recent_memory.append(current_state)
        all_paths.append((path[:], new_cost))
        
        current_h = heuristic(current_state, goal_state)
        if current_h < best_h_so_far:
            best_h_so_far = current_h
            steps_since_improvement = 0
        else:
            steps_since_improvement += 1
            
        if steps_since_improvement > 15:
            backtrack_point = max(5, len(path) // 3)
            position_to_restart = len(path) - backtrack_point
            if position_to_restart > 0:
                current_state = path[position_to_restart]
                path = path[:position_to_restart + 1]
                costs = costs[:position_to_restart + 1]
                steps_since_improvement = 0
            
    return path, calculate_costs(path), all_paths

def sensor_search_belief_states(initial_belief_state, goal, max_steps=500):
   
    current_belief_state = initial_belief_state
    path = [current_belief_state]
    costs = [0]
    visited = {current_belief_state}
    all_paths = [(path[:], 0)]
    
    for step in range(max_steps):
        if goal_test(current_belief_state, goal):
            return path, costs, all_paths
        
        actions = get_possible_actions(current_belief_state)
        
        best_action = None
        best_cost = float('inf')
        best_belief_state = None
        
        for action in actions:
            new_belief_state = result(current_belief_state, action)
            action_cost = calculate_action_cost(current_belief_state, action)
            
            if action_cost < best_cost:
                best_action = action
                best_cost = action_cost
                best_belief_state = new_belief_state
        
        if best_belief_state is None:
            break
            
        current_belief_state = best_belief_state
        path.append(current_belief_state)
        
        new_cost = costs[-1] + best_cost
        costs.append(new_cost)
        
        visited.add(current_belief_state)
        all_paths.append((path[:], new_cost))
        
    return path, costs, all_paths

def belief_state_search(start, goal, max_steps=100):
   
    current_state = start
    path = [current_state]
    costs = [0]
    visited = {current_state}
    all_paths = [(path[:], 0)]
    
    for _ in range(max_steps):
        if current_state == goal:
            return path, costs, all_paths
        
        actions = get_possible_actions(current_state)
        
        best_action = None
        best_cost = float('inf')
        best_state = None
        
        for action in actions:
            next_state = result(current_state, action)
            if next_state in visited:
                continue
                
            action_cost = MOVE_COSTS.get(action, 1)
            h_cost = heuristic(next_state, goal)
            total_cost = action_cost + h_cost
            
            if total_cost < best_cost:
                best_action = action
                best_cost = total_cost
                best_state = next_state
        
        if best_state is None:
            neighbors = get_neighbors(current_state)
            unvisited = [n for n in neighbors if n not in visited]
            if not unvisited:
                if len(path) > 1:
                    current_state = path[-2]
                    path.append(current_state)
                    costs.append(costs[-1] + 1)  
                    all_paths.append((path[:], costs[-1]))
                    continue
                else:
                    break
            else:
                best_state = random.choice(unvisited)
                best_action = get_move_direction(current_state, best_state)
                best_cost = MOVE_COSTS.get(best_action, 1)
        
        current_state = best_state
        path.append(current_state)
        costs.append(costs[-1] + best_cost)
        visited.add(current_state)
        all_paths.append((path[:], costs[-1]))
        
    return path, costs, all_paths

def goal_test(belief_state, goal):
    return belief_state == goal

def get_possible_actions(state):
    """Get possible actions for a given state."""
    zero_i, zero_j = None, None
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                zero_i, zero_j = i, j
                break
    
    actions = []
    if zero_i > 0:
        actions.append("up")
    if zero_i < 2:
        actions.append("down")
    if zero_j > 0:
        actions.append("left")
    if zero_j < 2:
        actions.append("right")
    
    return actions

def result(belief_state, action):
    zero_i, zero_j = None, None
    for i in range(3):
        for j in range(3):
            if belief_state[i][j] == 0:
                zero_i, zero_j = i, j
                break
    
    state_list = [list(row) for row in belief_state]
    
    if action == "up" and zero_i > 0:
        state_list[zero_i][zero_j], state_list[zero_i-1][zero_j] = state_list[zero_i-1][zero_j], state_list[zero_i][zero_j]
    elif action == "down" and zero_i < 2:
        state_list[zero_i][zero_j], state_list[zero_i+1][zero_j] = state_list[zero_i+1][zero_j], state_list[zero_i][zero_j]
    elif action == "left" and zero_j > 0:
        state_list[zero_i][zero_j], state_list[zero_i][zero_j-1] = state_list[zero_i][zero_j-1], state_list[zero_i][zero_j]
    elif action == "right" and zero_j < 2:
        state_list[zero_i][zero_j], state_list[zero_i][zero_j+1] = state_list[zero_i][zero_j+1], state_list[zero_i][zero_j]
    
    return tuple(tuple(row) for row in state_list)

def calculate_action_cost(belief_state, action):
    return MOVE_COSTS.get(action, 1)

def no_observation_belief_state_search(initial_beliefs, goal_beliefs, max_steps=500):
    """
    Implements the no-observation belief state search algorithm.
    
    Args:
        initial_beliefs: List of belief states (each belief state is a set of states)
        goal_beliefs: List of goal belief states (each goal belief state is a set of states)
        max_steps: Maximum number of steps to search
        
    Returns:
        path: List of states representing the solution path
        costs: List of costs for each step
        all_paths: List of all paths explored
    """
    # Initialize queue with initial belief states and empty paths
    queue = [(belief, [], 0) for belief in initial_beliefs]  # (belief_state, path, cost)
    visited = set()
    all_paths = []
    
    while queue and len(all_paths) < max_steps:
        current_belief, path, current_cost = queue.pop(0)
        
        # Check if current belief state is a subset of any goal belief
        for goal_belief in goal_beliefs:
            if current_belief.issubset(goal_belief):
                # Convert path of actions to path of states
                state_path = []
                current_state = list(current_belief)[0]  # Take any state from current belief
                state_path.append(current_state)
                
                for action in path:
                    current_state = result(current_state, action)
                    state_path.append(current_state)
                
                return state_path, calculate_costs(state_path), all_paths
        
        # Get common actions for all states in current belief
        common_actions = set.intersection(*[set(get_possible_actions(state)) for state in current_belief])
        
        for action in common_actions:
            # Calculate new belief state by applying action to all states
            new_belief = set()
            for state in current_belief:
                new_state = result(state, action)
                new_belief.add(new_state)
            
            # Convert to tuple for hashing
            new_belief_tuple = tuple(sorted(new_belief))
            
            if new_belief_tuple not in visited:
                visited.add(new_belief_tuple)
                new_path = path + [action]
                action_cost = MOVE_COSTS.get(action, 1)
                new_cost = current_cost + action_cost
                queue.append((new_belief, new_path, new_cost))
                
                # Convert path of actions to path of states for display
                state_path = []
                current_state = list(current_belief)[0]  # Take any state from current belief
                state_path.append(current_state)
                
                for a in new_path:
                    current_state = result(current_state, a)
                    state_path.append(current_state)
                
                all_paths.append((state_path, new_cost))
    
    return None, None, all_paths

def partially_observable_search(initial_state, goal_state, sensor_pos, sensor_value, max_steps=500):
    """
    Implements the partially observable search algorithm for 8-puzzle.
    
    Args:
        initial_state: Initial state of the puzzle
        goal_state: Goal state of the puzzle
        sensor_pos: Tuple of (row, col) for sensor position
        sensor_value: Value observed at sensor position
        max_steps: Maximum number of steps to search
        
    Returns:
        path: List of states representing the solution path
        costs: List of costs for each step
        all_paths: List of all paths explored
    """
    # Initialize belief state with all possible states that match sensor value
    belief_state = set()
    
    # If initial_state is a list of states (from listbox), use all of them
    if isinstance(initial_state, list):
        for state in initial_state:
            if isinstance(state, list):
                state = tuple(tuple(row) for row in state)
            if state[sensor_pos[0]][sensor_pos[1]] == sensor_value:
                belief_state.add(state)
    else:
        # Single initial state case
        if isinstance(initial_state, list):
            initial_state = tuple(tuple(row) for row in initial_state)
        if initial_state[sensor_pos[0]][sensor_pos[1]] == sensor_value:
            belief_state.add(initial_state)
    
    if not belief_state:
        return None, None, []
    
    # Start with the first state in belief state as the current state
    current_state = next(iter(belief_state))
    path = [current_state]
    costs = [0]
    visited = {current_state}
    all_paths = [(path[:], 0)]
    
    for _ in range(max_steps):
        # Check if any state in belief state matches goal
        if any(state == goal_state for state in belief_state):
            return path, costs, all_paths
            
        # Get common actions for all states in current belief
        common_actions = set.intersection(*[set(get_possible_actions(state)) for state in belief_state])
        
        if not common_actions:
            break
            
        # Choose best action based on heuristic
        best_action = None
        best_cost = float('inf')
        best_new_belief = None
        
        for action in common_actions:
            new_belief = set()
            for state in belief_state:
                new_state = result(state, action)
                # Only keep states that match sensor value
                if new_state[sensor_pos[0]][sensor_pos[1]] == sensor_value:
                    new_belief.add(new_state)
            
            if new_belief:
                # Calculate average heuristic value for new belief state
                avg_h = sum(heuristic(state, goal_state) for state in new_belief) / len(new_belief)
                action_cost = MOVE_COSTS.get(action, 1)
                total_cost = avg_h + action_cost
                
                if total_cost < best_cost:
                    best_action = action
                    best_cost = total_cost
                    best_new_belief = new_belief
        
        if best_new_belief is None:
            break
            
        # Apply best action
        belief_state = best_new_belief
        next_state = result(path[-1], best_action)
        path.append(next_state)
        
        new_cost = costs[-1] + MOVE_COSTS.get(best_action, 1)
        costs.append(new_cost)
        visited.add(next_state)
        all_paths.append((path[:], new_cost))
        
    return path, costs, all_paths

def get_states_from_listbox(self, listbox):
    states = []
    for idx in range(listbox.size()):
        line = listbox.get(idx)
        values = [int(x) for x in line.split(',')]
        state = (
            tuple(values[0:3]),
            tuple(values[3:6]),
            tuple(values[6:9])
        )
        states.append(state)
    return states

def no_observation_belief_state_search_adapter(self, initial_state, goal_state):
    # Lấy belief states và goal states từ listbox
    initial_beliefs = self.get_states_from_listbox(self.belief_listbox)
    goal_beliefs = self.get_states_from_listbox(self.goal_listbox)

    if not initial_beliefs or not goal_beliefs:
        messagebox.showerror("Lỗi", "Vui lòng nhập đủ trạng thái niềm tin và mục tiêu!")
        return None, None, []

    # Định dạng lại cho thuật toán
    initial_beliefs = [set([state]) for state in initial_beliefs]
    goal_beliefs = [set(goal_beliefs)]

    # Gọi thuật toán
    from algorithms.sensor_based import no_observation_belief_state_search
    path, costs, all_paths = no_observation_belief_state_search(initial_beliefs, goal_beliefs)
    return path, costs, all_paths

def partially_observable_search_adapter(self, initial_state, goal_state):
    try:
        # Lấy visible part từ ma trận mục tiêu (goal_matrix_entries)
        visible_state = []
        for i in range(3):
            row = []
            for j in range(3):
                value = self.goal_matrix_entries[i][j].get().strip()
                if value:
                    try:
                        row.append(int(value))
                    except ValueError:
                        row.append(None)
                else:
                    row.append(None)
            visible_state.append(tuple(row))

        # Lấy belief states và goal states từ listbox
        initial_states = self.get_states_from_listbox(self.belief_listbox)
        goal_states = self.get_states_from_listbox(self.goal_listbox)

        # Tìm vị trí số 0 trong visible_state
        sensor_pos = None
        for i in range(3):
            for j in range(3):
                if visible_state[i][j] == 0:
                    sensor_pos = (i, j)
                    break
            if sensor_pos:
                break

        if not sensor_pos:
            messagebox.showerror("Lỗi", "Không tìm thấy số 0 trong phần nhìn thấy!")
            return None, None, []

        from algorithms.sensor_based import partially_observable_search
        return partially_observable_search(
            visible_state,
            goal_states,
            sensor_pos,
            0
        )
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi nhập liệu: {str(e)}")
        return None, None, []
