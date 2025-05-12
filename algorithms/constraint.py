def create_grid_from_assignment(assignment, size=3):
    grid = [[0] * size for _ in range(size)]
    for var, value in assignment.items():
        idx = int(var[1:]) - 1 
        row, col = idx // size, idx % size
        grid[row][col] = value
    return [row[:] for row in grid]

def create_constraints():
    constraints = []
    top_bottom_pairs = [('X1', 'X4'), ('X2', 'X5'), ('X3', 'X6'), ('X4', 'X7'), ('X5', 'X8')]
    for top, bottom in top_bottom_pairs:
        constraints.append((top, bottom, lambda t, b: b == t + 3 and t != 0))

    left_right_pairs = [('X1', 'X2'), ('X2', 'X3'), ('X4', 'X5'), ('X5', 'X6'), ('X7', 'X8')]
    for left, right in left_right_pairs:
        constraints.append((left, right, lambda l, r: r == l + 1 and l != 0))

    return constraints

def is_consistent(variable, value, assignment, constraints):
    if value in assignment.values():
        return False
    temp_assignment = assignment.copy()
    temp_assignment[variable] = value
    for var1, var2, constraint_func in constraints:
        if var1 in temp_assignment and var2 in temp_assignment:
            if not constraint_func(temp_assignment[var1], temp_assignment[var2]):
                return False
    return True

def forward_checking(variable, value, assignment, domains, constraints):
    unassigned = [v for v in domains if v not in assignment]
    temp_assignment = assignment.copy()
    temp_assignment[variable] = value
    original_domains = {v: domains[v][:] for v in unassigned}

    for unassigned_var in unassigned:
        invalid_values = []
        for val in domains[unassigned_var][:]:
            temp_assignment[unassigned_var] = val
            for var1, var2, constraint_func in constraints:
                if var1 in temp_assignment and var2 in temp_assignment:
                    if not constraint_func(temp_assignment[var1], temp_assignment[var2]):
                        invalid_values.append(val)
                        break
            del temp_assignment[unassigned_var]  # 👈 Quan trọng!
        for invalid_val in invalid_values:
            domains[unassigned_var].remove(invalid_val)
        if not domains[unassigned_var]:
            # Khôi phục lại domain nếu thất bại
            for v in original_domains:
                domains[v] = original_domains[v]
            return False
    return True

def backtrack(assignment, index, csp, nodes_expanded, max_depth, path, use_forward=False):
    nodes_expanded[0] += 1
    max_depth[0] = max(max_depth[0], len(assignment))
    if assignment:
        path.append(create_grid_from_assignment(assignment))

    if index == len(csp['variables']):
        return assignment

    variable = csp['variables'][index]
    original_domains = {v: csp['domains'][v].copy() for v in csp['variables']}

    for value in csp['domains'][variable][:]:
        if is_consistent(variable, value, assignment, csp['constraints']):
            assignment[variable] = value
            path.append(create_grid_from_assignment(assignment))
            if not use_forward or forward_checking(variable, value, assignment, csp['domains'], csp['constraints']):
                result = backtrack(assignment, index + 1, csp, nodes_expanded, max_depth, path, use_forward)
                if result:
                    return result
            # Khôi phục miền cho mỗi biến
            csp['domains'] = {v: original_domains[v].copy() for v in csp['variables']}
            del assignment[variable]
            path.append(create_grid_from_assignment(assignment))
    return None
def forward_checking(variable, value, assignment, domains, constraints):
    unassigned = [v for v in domains if v not in assignment]
    temp_assignment = assignment.copy()
    temp_assignment[variable] = value
    original_domains = {v: domains[v][:] for v in unassigned}

    for unassigned_var in unassigned:
        invalid_values = []
        for val in domains[unassigned_var][:]:
            temp_assignment[unassigned_var] = val
            for var1, var2, constraint_func in constraints:
                if var1 in temp_assignment and var2 in temp_assignment:
                    if not constraint_func(temp_assignment[var1], temp_assignment[var2]):
                        invalid_values.append(val)
                        break
            del temp_assignment[unassigned_var]  # 👈 Quan trọng!
        for invalid_val in invalid_values:
            domains[unassigned_var].remove(invalid_val)
        if not domains[unassigned_var]:
            # Khôi phục lại domain nếu thất bại
            for v in original_domains:
                domains[v] = original_domains[v]
            return False
    return True

def ac3(csp):
    pairs = [('X1', 'X4'), ('X2', 'X5'), ('X3', 'X6'), ('X4', 'X7'), ('X5', 'X8'),
             ('X1', 'X2'), ('X2', 'X3'), ('X4', 'X5'), ('X5', 'X6'), ('X7', 'X8')]
    queue = list(pairs)
    while queue:
        first_var, second_var = queue.pop(0)
        if remove_inconsistent_values(first_var, second_var, csp):
            if not csp['domains'][first_var]:
                return False
            neighbors = [pair[1] for pair in pairs if pair[0] == first_var] + \
                        [pair[0] for pair in pairs if pair[1] == first_var]
            for neighbor in set(neighbors) - {second_var}:
                queue.append((neighbor, first_var))
    return True

def remove_inconsistent_values(first_var, second_var, csp):
    removed = False
    for constraint in csp['constraints']:
        if constraint[0] == first_var and constraint[1] == second_var:
            domain_first = csp['domains'][first_var].copy()
            for x in domain_first:
                if not any(constraint[2](x, y) for y in csp['domains'][second_var]):
                    csp['domains'][first_var].remove(x)
                    removed = True
    return removed

def solve(initial_state, method='backtracking'):
    flat_state = [num for row in initial_state for num in row]
    variables = [f"X{i+1}" for i in range(9)]
    value_order = flat_state.copy()
    domains = {var: value_order.copy() for var in variables}
    constraints = create_constraints()
    csp = {
        'variables': variables,
        'domains': domains,
        'constraints': constraints
    }

    nodes_expanded = [0]
    max_depth = [0]
    path = []

    if method == 'ac3':
        nodes_expanded[0] = 1  
        if not ac3(csp):
            return {
                'path': [],
                'nodes_expanded': nodes_expanded[0],
                'max_depth': max_depth[0],
                'solution': None
            }
        use_forward = False
    elif method == 'forward':
        use_forward = True
    else:  
        use_forward = False

    result = backtrack({}, 0, csp, nodes_expanded, max_depth, path, use_forward)

    return {
        'path': path,
        'nodes_expanded': nodes_expanded[0],
        'max_depth': max_depth[0],
        'solution': create_grid_from_assignment(result) if result else None 
    }
