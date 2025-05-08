from .uninformed import bfs, dfs, ucs, ids
from .informed import greedy, astar, ida_star
from .local import simple_hill_climbing,stochastic_hill_climbing,simulated_annealing,beam_search
from .nondeterministic import and_or_graph_search
from .sensor_based import sensor_search, belief_state_search  # Add belief_state_search here
from .constraint import solve as backtracking_solve, ac3, solve_with_ac3

ALGORITHM_CATEGORIES = {
    "Uninformed": ["BFS", "DFS", "UCS", "IDS"],
    "Informed": ["Greedy", "A*", "IDA*"],
    "Local": ["Simple HC", "Stochastic HC", "Simulated Annealing", "Beam Search"],
    "Nondeterministic": ["AND-OR Search"],
    "Sensor-Based": ["Sensor Search", "Belief State Search"],  # Add "Belief State Search" here
    "Constraint": ["Backtracking", "AC-3"]  
}