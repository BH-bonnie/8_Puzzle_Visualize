import heapq
from .utils import get_neighbors, get_move_direction, calculate_costs
from constants import MOVE_COSTS

def heuristic(state, goal):
    return sum(abs(i - x) + abs(j - y)
              for i, row in enumerate(state)
              for j, val in enumerate(row)
              if val
              for x, goal_row in enumerate(goal)
              for y, v in enumerate(goal_row)
              if v == val)

def greedy(start, goal):
    pq = [(heuristic(start, goal), start, [start], 0)]
    visited = {start}
    all_paths = []
    while pq:
        _, state, path, cost = heapq.heappop(pq)
        all_paths.append((path, cost))
        if state == goal:
            return path, calculate_costs(path), all_paths
        for neighbor in get_neighbors(state):
            if neighbor not in visited:
                visited.add(neighbor)
                direction = get_move_direction(state, neighbor)
                new_cost = cost + (MOVE_COSTS[direction] if direction else 0)
                heapq.heappush(pq, (heuristic(neighbor, goal), neighbor, path + [neighbor], new_cost))
    return None, None, all_paths

def astar(start, goal):
    pq = [(heuristic(start, goal), 0, start, [start], 0)]
    visited = {start}
    all_paths = []
    while pq:
        f, g, state, path, cost = heapq.heappop(pq)
        all_paths.append((path, cost))
        if state == goal:
            return path, calculate_costs(path), all_paths
        for neighbor in get_neighbors(state):
            if neighbor not in visited:
                visited.add(neighbor)
                direction = get_move_direction(state, neighbor)
                new_cost = cost + (MOVE_COSTS[direction] if direction else 0)
                g_new = g + (MOVE_COSTS[direction] if direction else 0)
                f_new = g_new + heuristic(neighbor, goal)
                heapq.heappush(pq, (f_new, g_new, neighbor, path + [neighbor], new_cost))
    return None, None, all_paths

def ida_star(start, goal):
    def search(state, g, bound, path, cost, all_paths):
        all_paths.append((path, cost))
        f = g + heuristic(state, goal)
        if f > bound:
            return f, None, None
        if state == goal:
            return f, path, calculate_costs(path)
        min_bound = float('inf')
        for neighbor in get_neighbors(state):
            if neighbor not in path:
                direction = get_move_direction(state, neighbor)
                new_cost = cost + (MOVE_COSTS[direction] if direction else 0)
                g_new = g + (MOVE_COSTS[direction] if direction else 0)
                new_f, result, result_costs = search(neighbor, g_new, bound, path + [neighbor], new_cost, all_paths)
                if result:
                    return new_f, result, result_costs
                min_bound = min(min_bound, new_f)
        return min_bound, None, None

    all_paths = []
    bound = heuristic(start, goal)
    while True:
        f, result, costs = search(start, 0, bound, [start], 0, all_paths)
        if result:
            return result, costs, all_paths
        if f == float('inf'):
            return None, None, all_paths
        bound = f