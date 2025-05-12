import heapq
from collections import defaultdict
from .utils import get_neighbors, get_move_direction, calculate_costs
from .informed import heuristic
from constants import MOVE_COSTS

class NondeterministicPuzzleProblem:

    def __init__(self, initial_state, goal_state):
        self.initial_state = initial_state
        self.goal_state = goal_state
    
    def goal_test(self, state):
        """Check if the state is a goal state."""
        return state == self.goal_state
    
    def actions(self, state):
        """Return possible actions from a state."""
        # For the 8-puzzle, actions are moving tiles
        # We'll simply return directions: "up", "down", "left", "right"
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
    
    def results(self, state, action):
      
        zero_i, zero_j = None, None
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    zero_i, zero_j = i, j
                    break
        
        state_list = [list(row) for row in state]
        
        if action == "up" and zero_i > 0:
            state_list[zero_i][zero_j], state_list[zero_i-1][zero_j] = state_list[zero_i-1][zero_j], state_list[zero_i][zero_j]
        elif action == "down" and zero_i < 2:
            state_list[zero_i][zero_j], state_list[zero_i+1][zero_j] = state_list[zero_i+1][zero_j], state_list[zero_i][zero_j]
        elif action == "left" and zero_j > 0:
            state_list[zero_i][zero_j], state_list[zero_i][zero_j-1] = state_list[zero_i][zero_j-1], state_list[zero_i][zero_j]
        elif action == "right" and zero_j < 2:
            state_list[zero_i][zero_j], state_list[zero_i][zero_j+1] = state_list[zero_i][zero_j+1], state_list[zero_i][zero_j]
    
        result_state = tuple(tuple(row) for row in state_list)
        
        
        return [result_state]

def and_or_graph_search(start, goal):
    
    problem = NondeterministicPuzzleProblem(start, goal)
    result = or_search(problem.initial_state, problem, {})
    
    if result == 'failure':
        return None, None, []
    
    path = extract_path(result, problem.initial_state, problem)
    costs = calculate_costs(path)
    all_paths = [(path[:i+1], costs[i]) for i in range(len(path))]
    
    return path, costs, all_paths

def extract_path(solution, start, problem):
    """Extract a simple path from the AND-OR solution structure."""
    if not solution:  
        return [start]
    
    if isinstance(solution, list) and len(solution) == 2:
        action = solution[0]
        and_plan = solution[1]
        
        result_states = problem.results(start, action)
        
        if result_states:
            next_state = result_states[0]  
            return [start] + extract_path(and_plan.get(next_state, []), next_state, problem)
    
    return [start]  

def or_search(state, problem, path):
  
    if problem.goal_test(state):
        return []
    
    if state in path:
        return 'failure'
    
    path = path.copy()  
    path[state] = True  

    for action in problem.actions(state):
        result_states = problem.results(state, action)
        plan = and_search(result_states, problem, path)
        if plan != 'failure':
            return [action, plan]
    
    return 'failure'

def and_search(states, problem, path):
   
    if not states:  
        return []
    
    path = path.copy()  
    plans = {}
    
    for s in states:
        plan = or_search(s, problem, path)
        if plan == 'failure':
            return 'failure'
        plans[s] = plan
    
    return plans  
