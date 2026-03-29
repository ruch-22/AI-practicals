from collections import deque

def solve_water_jug_bfs(capacity1, capacity2, target):
 
    queue = deque([(0, 0)]) 
    visited = set([(0, 0)])
    parent = {}

    while queue:
        current_jug1, current_jug2 = queue.popleft()

        if current_jug1 == target or current_jug2 == target:
            path = []
            state = (current_jug1, current_jug2)
            while state in parent:
                path.append(state)
                state = parent[state]
            path.append((0, 0)) # Add initial state
            return path[::-1] # Reverse to get correct order

        # Generate next states
        next_states = []

       
        next_states.append((capacity1, current_jug2))
        
        next_states.append((current_jug1, capacity2))
        
        next_states.append((0, current_jug2))
        
        next_states.append((current_jug1, 0))

        pour_amount = min(current_jug1, capacity2 - current_jug2)
        next_states.append((current_jug1 - pour_amount, current_jug2 + pour_amount))
        
        # Pour Jug 2 to Jug 1
        pour_amount = min(current_jug2, capacity1 - current_jug1)
        next_states.append((current_jug1 + pour_amount, current_jug2 - pour_amount))

        for next_jug1, next_jug2 in next_states:
            if (next_jug1, next_jug2) not in visited:
                visited.add((next_jug1, next_jug2))
                parent[(next_jug1, next_jug2)] = (current_jug1, current_jug2)
                queue.append((next_jug1, next_jug2))

    return None 

capacity_a = 4
capacity_b = 3
target_amount = 2

solution_path = solve_water_jug_bfs(capacity_a, capacity_b, target_amount)

if solution_path:
    print(f"Solution found for target {target_amount} with jugs {capacity_a}L and {capacity_b}L:")
    for state in solution_path:
        print(state)
else:
    print(f"No solution found for target {target_amount} with jugs {capacity_a}L and {capacity_b}L.")