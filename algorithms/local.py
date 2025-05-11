import random
import math
import heapq
from .utils import get_neighbors, get_move_direction, calculate_costs, generate_random_state
from .informed import heuristic
from constants import MOVE_COSTS

def simple_hill_climbing(start, goal):
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

def stochastic_hill_climbing(start, goal, max_iterations=100):
    current = start
    path = [current]
    costs = [0]
    visited = {current}
    all_paths = [(path, 0)]
    
    for _ in range(max_iterations):
        neighbors = [n for n in get_neighbors(current) if n not in visited]
        
        if not neighbors:
            return None, None, all_paths
        
        current_h = heuristic(current, goal)
        neighbor_evals = [(n, heuristic(n, goal)) for n in neighbors]
        
        improving_neighbors = [(n, h) for n, h in neighbor_evals if h < current_h]
        if not improving_neighbors:
            return None, None, all_paths
        
        next_state, next_h = random.choice(improving_neighbors)
        
        direction = get_move_direction(current, next_state)
        new_cost = costs[-1] + (MOVE_COSTS[direction] if direction else 0)
        costs.append(next_h)  
        current = next_state
        path.append(current)
        visited.add(current)
        all_paths.append((path[:], new_cost))
        
        if current == goal:
            return None, None, all_paths
    
    return None, None, all_paths

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

def steepest_ascent_hill_climbing(start, goal, max_iterations=100):
    current = start
    path = [current]
    costs = [0]
    visited = {current}
    all_paths = [(path, 0)]
    
    for _ in range(max_iterations):
        if current == goal:
            return path, costs, all_paths
            
        neighbors = get_neighbors(current)
        best_neighbor = None
        best_heuristic = float('inf')
        current_h = heuristic(current, goal)
        
        # Evaluate all neighbors
        for neighbor in neighbors:
            if neighbor not in visited:
                h = heuristic(neighbor, goal)
                if h < best_heuristic:
                    best_heuristic = h
                    best_neighbor = neighbor
        
        # If no better neighbor found, we're at a local maximum
        if best_neighbor is None or best_heuristic >= current_h:
            return None, None, all_paths
            
        # Move to the best neighbor
        direction = get_move_direction(current, best_neighbor)
        new_cost = costs[-1] + (MOVE_COSTS[direction] if direction else 0)
        costs.append(new_cost)
        current = best_neighbor
        path.append(current)
        visited.add(current)
        all_paths.append((path[:], new_cost))
    
    return None, None, all_paths

def genetic_algorithm(start, goal, population_size=50, mutation_rate=0.1, max_generations=1000):
    def fitness_fn(state):
        return -heuristic(state, goal)  # Negative because lower heuristic is better
    
    def reproduce(x, y):
        x_flat = [num for row in x for num in row]
        y_flat = [num for row in y for num in row]
        n = len(x_flat)
        c = random.randint(1, n-1)
        child_flat = x_flat[:c] + y_flat[c:]
        used = set(child_flat[:c])
        for i in range(c, n):
            if child_flat[i] in used:
                for num in range(9):
                    if num not in used:
                        child_flat[i] = num
                        used.add(num)
                        break
            else:
                used.add(child_flat[i])
        if len(set(child_flat)) != 9:
            return reproduce(x, y)
        return (
            tuple(child_flat[0:3]),
            tuple(child_flat[3:6]),
            tuple(child_flat[6:9])
        )
    
    def mutate(state):
        state_flat = [num for row in state for num in row]
        i, j = random.sample(range(9), 2)
        state_flat[i], state_flat[j] = state_flat[j], state_flat[i]
        if len(set(state_flat)) != 9:
            return mutate(state)
        return (
            tuple(state_flat[0:3]),
            tuple(state_flat[3:6]),
            tuple(state_flat[6:9])
        )
    
    def random_selection(population, fitness_fn):
        # Tournament selection
        tournament_size = 3
        tournament = random.sample(population, tournament_size)
        return max(tournament, key=fitness_fn)
    
    # Initialize population with start state and random states (no duplicates)
    population = [start]
    while len(population) < population_size:
        state = generate_random_state()
        if state not in population:
            population.append(state)
    best_individual = max(population, key=fitness_fn)
    best_fitness = fitness_fn(best_individual)
    
    path = [best_individual]
    costs = [0]
    all_paths = [(path[:], 0)]
    
    for generation in range(max_generations):
        new_population = set()

        # Create new population (avoid duplicates)
        while len(new_population) < population_size:
            x = random_selection(population, fitness_fn)
            y = random_selection(population, fitness_fn)
            child = reproduce(x, y)

            # Apply mutation
            if random.random() < mutation_rate:
                child = mutate(child)

            new_population.add(child)

        # Convert set back to list for next generation
        population = list(new_population)

                
        # Update best individual
        current_best = max(population, key=fitness_fn)
        current_fitness = fitness_fn(current_best)
        
        if current_fitness > best_fitness:
            best_individual = current_best
            best_fitness = current_fitness
            path.append(best_individual)
            costs.append(-best_fitness)  # Convert back to positive cost
            all_paths.append((path[:], costs[-1]))
        
        # Check if we've found the goal
        if best_individual == goal:
            return path, costs, all_paths
    
    return path, costs, all_paths