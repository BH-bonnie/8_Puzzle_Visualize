def solve(initial_state):
    nodes_expanded = [0]
    max_depth = [0]
    path = []

    flat_state = [num for row in initial_state for num in row]
    variables = [f"X{i+1}" for i in range(9)]
    value_order = flat_state.copy()
    domains = {var: value_order.copy() for var in variables}
    constraints = create_constraints()

    csp = {
        'variables': variables,
        'domains': domains,
        'constraints': constraints,
        'initial_assignment': {}
    }

    result = backtrack({}, 0, csp, nodes_expanded, max_depth, path)

    if result:
        solution_grid = [[0 for _ in range(3)] for _ in range(3)]
        for var, value in result.items():
            idx = int(var[1:]) - 1
            row, col = idx // 3, idx % 3
            solution_grid[row][col] = value

        return {
            'path': path,
            'nodes_expanded': nodes_expanded[0],
            'max_depth': max_depth[0],
            'solution': solution_grid
        }
    else:
        return {
            'path': [],
            'nodes_expanded': nodes_expanded[0],
            'max_depth': max_depth[0],
            'solution': None
        }

def create_constraints():
    constraints = []

    top_bottom_pairs = [
        ('X1', 'X4'), ('X2', 'X5'), ('X3', 'X6'),
        ('X4', 'X7'), ('X5', 'X8')
    ]
    for top, bottom in top_bottom_pairs:
        constraints.append((top, bottom, lambda t, b: b == t + 3 and t != 0))

    left_right_pairs = [
        ('X1', 'X2'), ('X2', 'X3'), ('X4', 'X5'),
        ('X5', 'X6'), ('X7', 'X8')
    ]

    def create_left_right_constraint(left, right):
        return lambda l, r: r == l + 1 and l != 0

    for left, right in left_right_pairs:
        constraints.append((left, right, create_left_right_constraint(left, right)))

    return constraints

def is_consistent(var, value, assignment, csp):
    if value in assignment.values():
        return False

    temp_assignment = assignment.copy()
    temp_assignment[var] = value

    for constraint in csp['constraints']:
        if len(constraint) == 2:
            name, constraint_func = constraint
            if not constraint_func(temp_assignment):
                return False
        elif len(constraint) == 3:
            var1, var2, constraint_func = constraint
            if var1 in temp_assignment and var2 in temp_assignment:
                if not constraint_func(temp_assignment[var1], temp_assignment[var2]):
                    return False

    return True



def backtrack(assignment, index, csp, nodes_expanded, max_depth, path):
    nodes_expanded[0] += 1
    max_depth[0] = max(max_depth[0], len(assignment))

    def capture_grid(current_assignment):
        grid = [[0 for _ in range(3)] for _ in range(3)]
        for var, value in current_assignment.items():
            idx = int(var[1:]) - 1
            row, col = idx // 3, idx % 3
            grid[row][col] = value
        return [row[:] for row in grid]  # bản sao

    if assignment:
        path.append(capture_grid(assignment))  # lưu trạng thái hiện tại

    if index == len(csp['variables']):
        return assignment

    var = csp['variables'][index]

    for value in csp['domains'][var]:
        if is_consistent(var, value, assignment, csp):
            assignment[var] = value
            path.append(capture_grid(assignment))  # trạng thái sau khi gán mới
            result = backtrack(assignment, index + 1, csp, nodes_expanded, max_depth, path)
            if result:
                return result
            del assignment[var]
            path.append(capture_grid(assignment))  # trạng thái sau khi xóa để quay lui

    return None

def ac3(csp):
    left_right_pairs = [('X1', 'X2'), ('X2', 'X3'), ('X4', 'X5'), ('X5', 'X6'), ('X7', 'X8')]
    top_bottom_pairs = [('X1', 'X4'), ('X2', 'X5'), ('X3', 'X6'), ('X4', 'X7'), ('X5', 'X8')]
    queue = [(Xi, Xj) for Xi, Xj in left_right_pairs + top_bottom_pairs] + \
            [(Xj, Xi) for Xi, Xj in left_right_pairs + top_bottom_pairs]

    while queue:
        Xi, Xj = queue.pop(0)
        if remove_inconsistent_values(Xi, Xj, csp):
            if len(csp['domains'][Xi]) == 0:
                return False
            neighbors = [pair[1] for pair in left_right_pairs + top_bottom_pairs if pair[0] == Xi] + \
                        [pair[0] for pair in left_right_pairs + top_bottom_pairs if pair[1] == Xi]
            for Xk in set(neighbors) - {Xj}:
                queue.append((Xk, Xi))
    return True

def remove_inconsistent_values(Xi, Xj, csp):
    removed = False

    for constraint in csp['constraints']:
        if len(constraint) == 3:
            var1, var2, func = constraint
            if (var1 == Xi and var2 == Xj) or (var1 == Xj and var2 == Xi):
                domain_Xi = csp['domains'][Xi].copy()
                for x in domain_Xi:
                    satisfied = False
                    for y in csp['domains'][Xj]:
                        if var1 == Xi and var2 == Xj and func(x, y):
                            satisfied = True
                            break
                        elif var1 == Xj and var2 == Xi and func(y, x):
                            satisfied = True
                            break
                    if not satisfied:
                        csp['domains'][Xi].remove(x)
                        removed = True

    return removed

def solve_with_ac3(initial_state=None):
    nodes_expanded = [0]
    max_depth = [0]
    path = []

    variables = [f"X{i+1}" for i in range(9)]

    if initial_state is None:
        flat_state = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    else:
        flat_state = [num for row in initial_state for num in row]

    value_order = flat_state.copy()
    domains = {var: value_order.copy() for var in variables}
    constraints = create_constraints()

    csp = {
        'variables': variables,
        'domains': domains,
        'constraints': constraints,
        'initial_assignment': {}
    }

    nodes_expanded[0] += 1
    ac3_result = ac3(csp)

    solution_grid = [[0 for _ in range(3)] for _ in range(3)]
    partial_assignment = {}

    for var in variables:
        idx = int(var[1:]) - 1
        row, col = idx // 3, idx % 3
        domain = csp['domains'][var]
        if len(domain) == 1:
            value = domain[0]
            solution_grid[row][col] = value
            partial_assignment[var] = value
        else:
            if domain:
                min_value = min(domain)
                solution_grid[row][col] = min_value
                partial_assignment[var] = min_value
            else:
                solution_grid[row][col] = 0

    path.append(solution_grid)

    return {
        'path': path,
        'nodes_expanded': nodes_expanded[0],
        'max_depth': max_depth[0],
        'solution': solution_grid if ac3_result else None
    }

