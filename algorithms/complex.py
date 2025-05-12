import random
import itertools
from collections import deque
from .utils import get_neighbors, get_move_direction, calculate_costs, get_zero_position  # Đảm bảo import get_zero_position
from .informed import heuristic
from constants import MOVE_COSTS

def get_possible_actions(state):
    zero_i, zero_j = get_zero_position(state)  # Sử dụng get_zero_position thay vì list comprehension
    actions = []
    if zero_i > 0: actions.append("up")
    if zero_i < 2: actions.append("down")
    if zero_j > 0: actions.append("left")
    if zero_j < 2: actions.append("right")
    return actions

def result(state, action):
    neighbors = get_neighbors(state)  
    for neighbor in neighbors:
        if get_move_direction(state, neighbor) == action:  
            return neighbor
    return state 
def goal_test(state, goal):
    return state == goal

def results(state, action):
    return [result(state, action)]

def and_or_graph_search(start, goal, max_depth=100):
    result = or_search(start, goal, {}, 0, max_depth)
    if result == 'failure':
        return None, None, []
    path = extract_path(result, start, goal)
    costs = calculate_costs(path)
    all_paths = [(path[:i+1], costs[i]) for i in range(len(path))]
    return path, costs, all_paths

def or_search(state, goal, path, depth, max_depth):
    if depth > max_depth:
        return 'failure'
    if goal_test(state, goal):
        return []
    if state in path:
        return 'failure'
    path = path.copy()
    path[state] = True
    for action in get_possible_actions(state):
        result_states = results(state, action)
        plan = and_search(result_states, goal, path, depth + 1, max_depth)
        if plan != 'failure':
            return [action, plan]
    return 'failure'

def and_search(states, goal, path, depth, max_depth):
    path = path.copy()
    plans = {}
    for s in states:
        plan = or_search(s, goal, path, depth + 1, max_depth)
        if plan == 'failure':
            return 'failure'
        plans[s] = plan
    return plans

def extract_path(solution, start, goal):
    if not solution:
        return [start]
    if isinstance(solution, list) and len(solution) == 2:
        action, and_plan = solution
        result_states = results(start, action)
        if result_states:
            next_state = result_states[0]
            subplan = and_plan.get(next_state, [])
            return [start] + extract_path(subplan, next_state, goal)
    return [start]

def no_observation_belief_state_search(initial_states, goal_states, max_steps=500):
    initial_belief = set(initial_states)
    goal_set = set(goal_states)
    queue = deque([(initial_belief, [], 0)])
    visited = {tuple(sorted(initial_belief))}
    all_paths = []
    rep0 = next(iter(initial_belief))

    while queue and len(all_paths) < max_steps:
        belief, actions, cost = queue.popleft()
        hit = next((s for s in belief if s in goal_set), None)
        if hit:
            path = [rep0]
            for a in actions:
                path.append(result(path[-1], a))
            return path, calculate_costs(path), all_paths

        common_actions = set.intersection(*[set(get_possible_actions(s)) for s in belief])
        for action in common_actions:
            pred = {result(s, action) for s in belief}
            key = tuple(sorted(pred))
            if key not in visited:
                visited.add(key)
                new_cost = cost + MOVE_COSTS.get(action, 1)
                new_actions = actions + [action]
                queue.append((pred, new_actions, new_cost))
                rep_path = [rep0]
                for a in new_actions:
                    rep_path.append(result(rep_path[-1], a))
                all_paths.append((rep_path, new_cost))

    return None, None, all_paths

def partially_observable_search(visible_state, initial_states, goal_states, max_steps=500):
    present = {v for row in visible_state for v in row if v is not None}
    missing = list(set(range(9)) - present)
    blanks = [(i, j) for i in range(3) for j in range(3) if visible_state[i][j] is None]

    initial_belief = set()
    for s in initial_states:
        if all(visible_state[i][j] is None or s[i][j] == visible_state[i][j]
               for i in range(3) for j in range(3)):
            initial_belief.add(s)

    if not initial_belief:
        for perm in itertools.permutations(missing):
            board = [[visible_state[i][j] for j in range(3)] for i in range(3)]
            for (i, j), v in zip(blanks, perm):
                board[i][j] = v
            initial_belief.add(tuple(tuple(r) for r in board))

    return no_observation_belief_state_search(initial_belief, goal_states, max_steps)