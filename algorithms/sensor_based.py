import random
from collections import deque
from .utils import get_neighbors, get_move_direction, calculate_costs
from .informed import heuristic
from constants import MOVE_COSTS

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

def get_possible_actions(belief_state):
    zero_i, zero_j = None, None
    for i in range(3):
        for j in range(3):
            if belief_state[i][j] == 0:
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
