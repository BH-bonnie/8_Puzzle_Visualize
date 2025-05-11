from .uninformed import bfs, dfs, ucs, ids
from .informed import greedy, astar, ida_star
from .local import simple_hill_climbing, stochastic_hill_climbing, simulated_annealing, beam_search, genetic_algorithm, steepest_ascent_hill_climbing
from .nondeterministic import and_or_graph_search
from .sensor_based import sensor_search, belief_state_search, no_observation_belief_state_search
from .constraint import solve as backtracking_solve, ac3, solve_with_ac3
from .Reforcement_learning import QLearning

ALGORITHM_CATEGORIES = {
    "Uninformed": ["BFS", "DFS", "UCS", "IDS"],
    "Informed": ["Greedy", "A*", "IDA*"],
    "Local": ["Simple HC", "Stochastic HC", "Simulated Annealing", "Beam Search", "Steepest Ascent HC", "Genetic Algorithm"],
    "Nondeterministic": ["AND-OR Search"],
    "Sensor-Based": ["Sensor Search", "Belief State Search", "No-Observation Belief State Search"],
    "Constraint": ["Backtracking", "AC-3", "Forward Checking"],
    "Reinforcement": ["Q-Learning"]
}