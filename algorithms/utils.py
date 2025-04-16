import random

def get_zero_position(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j
    return None

def get_move_direction(prev_state, curr_state):
    prev_x, prev_y = get_zero_position(prev_state)
    curr_x, curr_y = get_zero_position(curr_state)
    if curr_x < prev_x: return "up"
    elif curr_x > prev_x: return "down"
    elif curr_y < prev_y: return "left"
    elif curr_y > prev_y: return "right"
    return None

def get_neighbors(state):
    state_list = [list(row) for row in state]
    x, y = get_zero_position(state)
    moves = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            new_state = [row[:] for row in state_list]
            new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
            moves.append(tuple(tuple(row) for row in new_state))
    return moves

def calculate_costs(path):
    from constants import MOVE_COSTS  
    costs = [0]
    for i in range(1, len(path)):
        direction = get_move_direction(path[i-1], path[i])
        costs.append(costs[-1] + (MOVE_COSTS[direction] if direction else 0))
    return costs

def generate_random_state():
    """Generate a random valid 8-puzzle state"""
    numbers = list(range(9)) 
    random.shuffle(numbers)
    
    state = (
        tuple(numbers[0:3]),
        tuple(numbers[3:6]),
        tuple(numbers[6:9])
    )
    
    flat_state = [num for row in state for num in row if num != 0]
    inversions = 0
    for i in range(len(flat_state)):
        for j in range(i+1, len(flat_state)):
            if flat_state[i] > flat_state[j]:
                inversions += 1
    
   
    if inversions % 2 != 0:
        for i in range(len(flat_state) - 1):
            if flat_state[i] != 0 and flat_state[i+1] != 0:
                flat_state[i], flat_state[i+1] = flat_state[i+1], flat_state[i]
                break
        
        counter = 0
        new_state = []
        for i in range(3):
            row = []
            for j in range(3):
                if state[i][j] == 0:
                    row.append(0)
                else:
                    row.append(flat_state[counter])
                    counter += 1
            new_state.append(tuple(row))
        state = tuple(new_state)
    
    return state