import random
import math
import heapq
from .utils import get_neighbors, get_move_direction, calculate_costs
from .informed import heuristic
from constants import MOVE_COSTS

def hill_climbing(start, goal):
    current = start
    path = [current]
    costs = [0]
    visited = {current}
    all_paths = [(path, 0)]
    
    while current != goal:
        neighbors = get_neighbors(current)
        best_neighbor = None
        best_heuristic = float('inf')
        
        for neighbor in neighbors:
            if neighbor not in visited:
                h = heuristic(neighbor, goal)
                if h < best_heuristic:
                    best_heuristic = h
                    best_neighbor = neighbor
        
        if best_neighbor is None or best_heuristic >= heuristic(current, goal):
            return None, None, all_paths
        
        direction = get_move_direction(current, best_neighbor)
        new_cost = costs[-1] + (MOVE_COSTS[direction] if direction else 0)
        costs.append(new_cost)
        current = best_neighbor
        path.append(current)
        visited.add(current)
        all_paths.append((path[:], new_cost))
    
    return path, costs, all_paths

def stochastic_hill_climbing(start, goal):
    current = start
    path = [current]
    costs = [0]
    visited = {current}
    all_paths = [(path, 0)]
    max_iterations = 100
    
    for _ in range(max_iterations):
        if current == goal:
            return path, costs, all_paths
        neighbors = [n for n in get_neighbors(current) if n not in visited]
        if not neighbors:
            return None, None, all_paths
        current_h = heuristic(current, goal)
        improving_neighbors = [(n, heuristic(n, goal)) for n in neighbors if heuristic(n, goal) < current_h]
        if not improving_neighbors:
            return None, None, all_paths
        next_state = random.choice(improving_neighbors)[0]
        direction = get_move_direction(current, next_state)
        new_cost = costs[-1] + (MOVE_COSTS[direction] if direction else 0)
        costs.append(new_cost)
        current = next_state
        path.append(current)
        visited.add(current)
        all_paths.append((path[:], new_cost))
    return None, None, all_paths

def simple_hill_climbing(start, goal):
    current = start
    path = [current]
    costs = [0]
    visited = {current}
    all_paths = [(path, 0)]
    
    while current != goal:
        neighbors = get_neighbors(current)
        current_h = heuristic(current, goal)
        found_better = False
        
        for neighbor in neighbors:
            if neighbor not in visited:
                h = heuristic(neighbor, goal)
                if h < current_h:
                    direction = get_move_direction(current, neighbor)
                    new_cost = costs[-1] + (MOVE_COSTS[direction] if direction else 0)
                    costs.append(new_cost)
                    current = neighbor
                    path.append(current)
                    visited.add(current)
                    all_paths.append((path[:], new_cost))
                    found_better = True
                    break
        if not found_better:
            return None, None, all_paths
    return path, costs, all_paths

def simulated_annealing(start, goal, initial_temperature=1000, cooling_rate=0.995, max_iterations=10000):
    current = start
    path = [current]
    costs = [0]
    visited = {current}
    all_paths = [(path, 0)]
    temperature = initial_temperature
    
    for _ in range(max_iterations):
        if current == goal:
            return path, costs, all_paths
        neighbors = [n for n in get_neighbors(current) if n not in visited]
        if not neighbors:
            return None, None, all_paths
        next_state = random.choice(neighbors)
        current_h = heuristic(current, goal)
        next_h = heuristic(next_state, goal)
        delta_e = next_h - current_h
        if delta_e < 0 or random.random() < math.exp(-delta_e / temperature):
            direction = get_move_direction(current, next_state)
            new_cost = costs[-1] + (MOVE_COSTS[direction] if direction else 0)
            costs.append(new_cost)
            current = next_state
            path.append(current)
            visited.add(current)
            all_paths.append((path[:], new_cost))
        temperature *= cooling_rate
        if temperature < 0.1:
            break
    return None, None, all_paths

def beam_search(start, goal, beam_width=3):
    queue = [(heuristic(start, goal), start, [start], 0)]
    visited = {start}
    all_paths = [(queue[0][2], 0)]
    
    while queue:
        queue = sorted(queue, key=lambda x: x[0])[:beam_width]
        next_queue = []
        for _, state, path, cost in queue:
            if state == goal:
                return path, calculate_costs(path), all_paths
            for neighbor in get_neighbors(state):
                if neighbor not in visited:
                    visited.add(neighbor)
                    h = heuristic(neighbor, goal)
                    direction = get_move_direction(state, neighbor)
                    new_cost = cost + (MOVE_COSTS[direction] if direction else 0)
                    next_queue.append((h, neighbor, path + [neighbor], new_cost))
                    all_paths.append((path + [neighbor], new_cost))
        queue = next_queue
    return None, None, all_paths