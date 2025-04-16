from .uninformed import bfs, dfs, ucs, ids
from .informed import greedy, astar, ida_star
from .local import hill_climbing, stochastic_hill_climbing, simple_hill_climbing, simulated_annealing, beam_search

ALGORITHM_CATEGORIES = {
    "Uninformed": ["BFS", "DFS", "UCS", "IDS"],
    "Informed": ["Greedy", "A*", "IDA*"],
    "Local": ["Hill Climbing", "Stochastic HC", "Simple HC", "Simulated Annealing", "Beam Search"]
}