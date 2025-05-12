import random
import math
from collections import defaultdict
from .utils import get_neighbors, get_move_direction
from .informed import heuristic
from constants import MOVE_COSTS

def q_learning(initial_state, goal_state,
               episodes=2000, alpha=0.1, gamma=0.9,
               epsilon_start=1.0, epsilon_end=0.01,
               max_steps=100,
               Q=None, distance_cache=None,
               **kwargs):
    if Q is None:
        Q = defaultdict(lambda: defaultdict(float))
    else:
        Q = defaultdict(lambda: defaultdict(float), Q)
    if distance_cache is None:
        distance_cache = {}
    epsilon = epsilon_start
    eps_decay = (epsilon_start - epsilon_end) / episodes

    def state_key(s): return str(s)

    for ep in range(episodes):
        state = initial_state
        for step in range(max_steps):
            sk = state_key(state)
            neigh = get_neighbors(state)
            acts = [(get_move_direction(state, n), n) for n in neigh]

            if random.random() < epsilon:
                action, next_s = random.choice(acts)
            else:
                vals = {a: Q[sk][a] for a, _ in acts}
                action, next_s = max(acts, key=lambda x: vals.get(x[0], 0))

            h_cur = heuristic(state, goal_state)
            h_next = heuristic(next_s, goal_state)
            reward = (h_cur - h_next)

            nk = state_key(next_s)
            future = Q[nk].values() and max(Q[nk].values()) or 0
            Q[sk][action] += alpha * (reward + gamma * future - Q[sk][action])

            state = next_s
            if state == goal_state:
                break

        epsilon = max(epsilon_end, epsilon - eps_decay)

    path = [initial_state]
    costs = [0]
    cur = initial_state
    visited = {initial_state}
    while cur != goal_state:
        sk = state_key(cur)
        if sk not in Q or not Q[sk]:
            break
        action = max(Q[sk].items(), key=lambda kv: kv[1])[0]
        for n in get_neighbors(cur):
            if get_move_direction(cur, n) == action:
                nxt = n
                break
        else:
            break

        direction = action.lower()
        step_cost = MOVE_COSTS.get(direction, 1)
        costs.append(costs[-1] + step_cost)
        path.append(nxt)
        if nxt in visited:
            break
        visited.add(nxt)
        cur = nxt

    return path, costs, []