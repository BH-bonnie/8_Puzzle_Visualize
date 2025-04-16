from collections import deque
import heapq
from .utils import get_neighbors, get_move_direction, calculate_costs
from constants import MOVE_COSTS

def bfs(start, goal):
    queue = deque([(start, [start], 0)])
    visited = {start}
    all_paths = []
    while queue:
        state, path, cost = queue.popleft()
        all_paths.append((path, cost))
        if state == goal:
            return path, calculate_costs(path), all_paths
        for neighbor in get_neighbors(state):
            if neighbor not in visited:
                visited.add(neighbor)
                direction = get_move_direction(state, neighbor)
                new_cost = cost + (MOVE_COSTS[direction] if direction else 0)
                queue.append((neighbor, path + [neighbor], new_cost))
    return None, None, all_paths

def dfs(start, goal, max_depth=30):
    def dfs_recursive(state, path, visited, depth, cost_so_far, all_paths):
        all_paths.append((path, cost_so_far))
        if state == goal:
            return path, calculate_costs(path)
        if depth >= max_depth:
            return None, None
        for neighbor in get_neighbors(state):
            if neighbor not in visited:
                visited.add(neighbor)
                direction = get_move_direction(state, neighbor)
                new_cost = cost_so_far + (MOVE_COSTS[direction] if direction else 0)
                result_path, result_costs = dfs_recursive(neighbor, path + [neighbor], visited, depth + 1, new_cost, all_paths)
                if result_path:
                    return result_path, result_costs
        return None, None
    
    visited = {start}
    all_paths = []
    path, costs = dfs_recursive(start, [start], visited, 0, 0, all_paths)
    return path, costs, all_paths

def ucs(start, goal):
    pq = [(0, start, [start])]
    visited = {start}
    all_paths = []
    while pq:
        cost, state, path = heapq.heappop(pq)
        all_paths.append((path, cost))
        if state == goal:
            return path, calculate_costs(path), all_paths
        for neighbor in get_neighbors(state):
            if neighbor not in visited:
                visited.add(neighbor)
                direction = get_move_direction(state, neighbor)
                new_cost = cost + (MOVE_COSTS[direction] if direction else 0)
                heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))
    return None, None, all_paths

def ids(start, goal):
    def dls(state, path, depth, cost, visited, all_paths):
        all_paths.append((path, cost))
        if depth < 0:
            return None, None
        if state == goal:
            return path, calculate_costs(path)
        for neighbor in get_neighbors(state):
            if neighbor not in visited:
                visited.add(neighbor)
                direction = get_move_direction(state, neighbor)
                new_cost = cost + (MOVE_COSTS[direction] if direction else 0)
                result, result_costs = dls(neighbor, path + [neighbor], depth - 1, new_cost, visited, all_paths)
                if result:
                    return result, result_costs
        return None, None
    
    all_paths = []
    depth = 0
    while True:
        visited = {start}
        result, costs = dls(start, [start], depth, 0, visited, all_paths)
        if result:
            return result, costs, all_paths
        depth += 1
        if depth > 50:
            return None, None, all_paths