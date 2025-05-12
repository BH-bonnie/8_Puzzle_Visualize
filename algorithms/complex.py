import random
import itertools
from collections import deque
from .utils import get_neighbors, get_move_direction, calculate_costs, get_zero_position
from .informed import heuristic
from constants import MOVE_COSTS

def get_possible_actions(state):
    zero_i, zero_j = get_zero_position(state)
    return [
        action for action, (di, dj) in [
            ("up", (-1, 0)), ("down", (1, 0)), ("left", (0, -1)), ("right", (0, 1))
        ] if 0 <= zero_i + di < 3 and 0 <= zero_j + dj < 3
    ]

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
    for state in states:
        plan = or_search(state, goal, path, depth + 1, max_depth)
        if plan == 'failure':
            return 'failure'
        plans[state] = plan
    return plans

def extract_path(solution, start, goal):
    path = [start]
    if not solution:
        return path
    if isinstance(solution, list) and len(solution) == 2:
        action, and_plan = solution
        next_state = results(start, action)[0]
        if next_state in and_plan:
            return path + extract_path(and_plan[next_state], next_state, goal)
    return path

def no_observation_belief_state_search(initial_states, goal_states, max_steps=500):
    belief = set(initial_states)
    goal_set = set(goal_states)
    queue = deque([(belief, [], 0)])
    visited = {tuple(sorted(belief))}
    all_paths = []
    representative_state = next(iter(belief))

    while queue and len(all_paths) < max_steps:
        current_belief, actions, cost = queue.popleft()
        goal_hit = next((s for s in current_belief if s in goal_set), None)
        if goal_hit:
            path = [representative_state]
            for action in actions:
                path.append(result(path[-1], action))
            return path, calculate_costs(path), all_paths

        common_actions = set.intersection(*[set(get_possible_actions(s)) for s in current_belief])
        for action in common_actions:
            next_belief = {result(s, action) for s in current_belief}
            belief_key = tuple(sorted(next_belief))
            if belief_key not in visited:
                visited.add(belief_key)
                new_cost = cost + MOVE_COSTS.get(action, 1)
                new_actions = actions + [action]
                queue.append((next_belief, new_actions, new_cost))
                path = [representative_state]
                for a in new_actions:
                    path.append(result(path[-1], a))
                all_paths.append((path, new_cost))

    return None, None, all_paths

def partially_observable_search(visible_state, initial_states, goal_states, max_steps=500):
    present = {v for row in visible_state for v in row if v is not None}
    missing = list(set(range(9)) - present)
    blanks = [(i, j) for i in range(3) for j in range(3) if visible_state[i][j] is None]

    initial_belief = set()
    for state in initial_states:
        if all(visible_state[i][j] is None or state[i][j] == visible_state[i][j]
               for i in range(3) for j in range(3)):
            initial_belief.add(state)

    if not initial_belief and len(missing) <= 4:
        for perm in itertools.permutations(missing):
            board = [[visible_state[i][j] for j in range(3)] for i in range(3)]
            for (i, j), value in zip(blanks, perm):
                board[i][j] = value
            initial_belief.add(tuple(tuple(row) for row in board))

    return no_observation_belief_state_search(initial_belief, goal_states, max_steps)