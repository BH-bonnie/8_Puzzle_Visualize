from .uninformed import bfs, dfs, ucs, ids
from .informed import greedy, astar, ida_star
from .local import simple_hill_climbing, stochastic_hill_climbing, simulated_annealing, beam_search, genetic_algorithm, steepest_ascent_hill_climbing
from.complex import and_or_graph_search, no_observation_belief_state_search, partially_observable_search
from .constraint import solve as solve
from .Reforcement_learning import q_learning

ALGORITHM_CATEGORIES = {
    "Uninformed": ["BFS", "DFS", "UCS", "IDS"],
    "Informed": ["Greedy", "A*", "IDA*"],
    "Local": ["Simple HC", "Stochastic HC", "Simulated Annealing", "Beam Search", "Steepest Ascent HC", "Genetic Algorithm"],
    "Complex": ["And-Or Graph Search", "No Observation Belief State Search", "Partially Observable Search"],
    "Constraint": ["Backtracking", "AC-3", "Forward Checking"],
    "Reinforcement": ["Q-Learning"]
}