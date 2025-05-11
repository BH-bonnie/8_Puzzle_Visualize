import random
from collections import deque
from .utils import get_neighbors, get_move_direction, calculate_costs
from .informed import heuristic
from constants import MOVE_COSTS
import itertools

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
    queue = [(belief, [], 0) for belief in initial_beliefs]
    visited = set()
    all_paths = []
    
    while queue and len(all_paths) < max_steps:
        current_belief, path, current_cost = queue.pop(0)
        
        for goal_belief in goal_beliefs:
            if current_belief.issubset(goal_belief):
                state_path = []
                current_state = list(current_belief)[0]
                state_path.append(current_state)
                
                for action in path:
                    current_state = result(current_state, action)
                    state_path.append(current_state)
                
                return state_path, calculate_costs(state_path), all_paths
        
        common_actions = set.intersection(*[set(get_possible_actions(state)) for state in current_belief])
        
        for action in common_actions:
            new_belief = set()
            for state in current_belief:
                new_state = result(state, action)
                new_belief.add(new_state)
            
            new_belief_tuple = tuple(sorted(new_belief))
            
            if new_belief_tuple not in visited:
                visited.add(new_belief_tuple)
                new_path = path + [action]
                action_cost = MOVE_COSTS.get(action, 1)
                new_cost = current_cost + action_cost
                queue.append((new_belief, new_path, new_cost))
                
                state_path = []
                current_state = list(current_belief)[0]
                state_path.append(current_state)
                
                for a in new_path:
                    current_state = result(current_state, a)
                    state_path.append(current_state)
                
                all_paths.append((state_path, new_cost))
    
    return None, None, all_paths

def partially_observable_search(visible_state, initial_states, goal_states, max_steps=500):
    """
    Implements partially observable search for the 8-puzzle problem using belief updates.

    Args:
        visible_state: 3x3 tuple of tuples; các ô khóa (locked) có số, các ô mở là None.
        initial_states: List of complete states ứng viên ban đầu.
        goal_states: List of complete goal states.
        max_steps: giới hạn bước tìm.

    Returns:
        path: List of states từ một đại diện initial → goal
        costs: chi phí tích lũy
        all_paths: danh sách các đường đi đại diện ở mỗi bước
    """
    from collections import deque
    from .utils import calculate_costs
    # 1. Build initial belief
    present = {v for row in visible_state for v in row if v is not None}
    missing = list(set(range(9)) - present)
    blanks = [(i, j) for i in range(3) for j in range(3) if visible_state[i][j] is None]

    initial_belief = set()
    for s in initial_states:
        if all(visible_state[i][j] is None or s[i][j] == visible_state[i][j]
               for i in range(3) for j in range(3)):
            initial_belief.add(s)
    if not initial_belief:
        import itertools
        for perm in itertools.permutations(missing):
            board = [[visible_state[i][j] for j in range(3)] for i in range(3)]
            for (i, j), v in zip(blanks, perm):
                board[i][j] = v
            initial_belief.add(tuple(tuple(r) for r in board))

    # 2. Goal set for quick test
    goal_set = set(goal_states)

    # 3. BFS on belief-space
    queue = deque([(initial_belief, [], 0)])
    visited = {tuple(sorted(initial_belief))}
    all_paths = []
    # chọn một representative state từ initial_belief để dựng path
    rep0 = next(iter(initial_belief))

    while queue and len(all_paths) < max_steps:
        belief, actions, cost = queue.popleft()
        # goal-test: nếu có bất kỳ state nào trong belief nằm trong goal_set
        hit = next((s for s in belief if s in goal_set), None)
        if hit:
            # dựng đường đi từ rep0 qua chuỗi actions
            path = [rep0]
            for a in actions:
                path.append(result(path[-1], a))
            return path, calculate_costs(path), all_paths

        # tìm các action khả thi (common to all states)
        common = set.intersection(*[set(get_possible_actions(s)) for s in belief])
        for a in common:
            # 3.1 predict
            pred = {result(s, a) for s in belief}
            # 3.2 update với visible_state
            updated = {s for s in pred
                       if all(visible_state[i][j] is None or s[i][j] == visible_state[i][j]
                              for i in range(3) for j in range(3))}
            key = tuple(sorted(updated))
            if updated and key not in visited:
                visited.add(key)
                new_cost = cost + MOVE_COSTS.get(a, 1)
                new_actions = actions + [a]
                queue.append((updated, new_actions, new_cost))
                # ghi lại 1 đường đại diện cho all_paths
                rep_path = [rep0]
                for aa in new_actions:
                    rep_path.append(result(rep_path[-1], aa))
                all_paths.append((rep_path, new_cost))

    return None, None, all_paths