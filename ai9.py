"""
Sudoku CSP solver (AC-3 + Backtracking search with MRV, LCV & forward checking)

Usage:
    python sudoku_csp_solver.py

The script contains a sample puzzle (string of length 81, 0 or '.' for empties).
You can replace the `puzzle` variable in the `__main__` block with any other puzzle string.
"""

import itertools
from collections import defaultdict, deque

class SudokuCSP:
    def __init__(self, grid):
        """
        grid: 9x9 list of lists or a single string of length 81 where empty cells are 0 or '.'
        """
        self.cells = [r*9 + c for r in range(9) for c in range(9)]
        # Build rows, cols, boxes
        self.rows = [[r*9 + c for c in range(9)] for r in range(9)]
        self.cols = [[r*9 + c for r in range(9)] for c in range(9)]
        self.boxes = []
        for br in range(3):
            for bc in range(3):
                box = []
                for r in range(3):
                    for c in range(3):
                        box.append((br*3 + r)*9 + (bc*3 + c))
                self.boxes.append(box)
        # neighbors: for each cell, set of cells in same row/col/box except itself
        self.neighbors = {cell: set() for cell in self.cells}
        for unit in (self.rows + self.cols + self.boxes):
            for cell in unit:
                self.neighbors[cell].update(u for u in unit if u != cell)
        # Parse grid and set domains
        self.domains = {cell: set(range(1,10)) for cell in self.cells}
        given = self._parse_grid(grid)
        for cell, val in given.items():
            if val is not None:
                self.domains[cell] = {val}
        # Convert neighbors to list for deterministic order
        self.neighbors = {k: sorted(list(v)) for k, v in self.neighbors.items()}

    def _parse_grid(self, grid):
        """Return a dict cell->value or None for empties"""
        vals = {}
        s = ""
        if isinstance(grid, str):
            s = grid
        else:
            # flatten list of lists
            s = "".join(str(x) for row in grid for x in row)
        if len(s) != 81:
            raise ValueError("Grid must be 81 characters long (9x9)")
        for i, ch in enumerate(s):
            if ch in ".0":
                vals[i] = None
            elif ch.isdigit():
                vals[i] = int(ch)
            else:
                raise ValueError("Unsupported character in grid: " + ch)
        return vals

    def display(self, assignment=None):
        """Prints grid. If assignment (domains with singletons) provided, use that"""
        out = ""
        for r in range(9):
            row = []
            for c in range(9):
                i = r*9 + c
                if assignment is None:
                    d = self.domains[i]
                    ch = str(next(iter(d))) if len(d) == 1 else '.'
                else:
                    d = assignment.get(i, None)
                    ch = str(d) if d is not None else '.'
                row.append(ch)
            out += " ".join(row[0:3]) + " | " + " ".join(row[3:6]) + " | " + " ".join(row[6:9]) + "\n"
            if r % 3 == 2 and r != 8:
                out += "-"*21 + "\n"
        print(out)

    # ---------------- AC-3 Algorithm ----------------
    def ac3(self, queue=None):
        """AC-3 constraint propagation"""
        if queue is None:
            queue = deque((Xi, Xj) for Xi in self.cells for Xj in self.neighbors[Xi])
        else:
            queue = deque(queue)
        while queue:
            Xi, Xj = queue.popleft()
            if self.revise(Xi, Xj):
                if len(self.domains[Xi]) == 0:
                    return False
                for Xk in self.neighbors[Xi]:
                    if Xk != Xj:
                        queue.append((Xk, Xi))
        return True

    def revise(self, Xi, Xj):
        """Revise Xi wrt Xj. If domain values of Xi have no supporting value in Xj remove them."""
        revised = False
        to_remove = set()
        for x in set(self.domains[Xi]):
            # supported if exists y in domain(Xj) such that x != y
            if not any(x != y for y in self.domains[Xj]):
                to_remove.add(x)
        if to_remove:
            self.domains[Xi] -= to_remove
            revised = True
        return revised

    # ---------------- Backtracking Search with Inference ----------------
    def is_solved(self):
        return all(len(self.domains[cell]) == 1 for cell in self.cells)

    def select_unassigned_variable(self):
        """MRV heuristic: choose variable with smallest domain >1.
           Tie-breaker: degree heuristic (most neighbors)"""
        unassigned = [cell for cell in self.cells if len(self.domains[cell]) > 1]
        if not unassigned:
            return None
        # MRV
        mrv = min(len(self.domains[cell]) for cell in unassigned)
        candidates = [cell for cell in unassigned if len(self.domains[cell]) == mrv]
        if len(candidates) == 1:
            return candidates[0]
        # degree heuristic: choose variable involved in most constraints with other unassigned vars
        best = max(candidates, key=lambda c: sum(1 for n in self.neighbors[c] if len(self.domains[n])>1))
        return best

    def order_domain_values(self, var):
        """LCV heuristic: order domain values that rule out the fewest choices for neighbors first"""
        domain = list(self.domains[var])
        def count_conflicts(val):
            count = 0
            for n in self.neighbors[var]:
                if val in self.domains[n]:
                    count += 1
            return count
        domain.sort(key=count_conflicts)
        return domain

    def consistent(self, var, val, assignment):
        """Check if assigning val to var is consistent with assignment (neighbors assigned)"""
        for n in self.neighbors[var]:
            if n in assignment and assignment[n] == val:
                return False
        return True

    def assign(self, var, val, domains):
        """Assign value val to var in a copy of domains and do forward checking (remove val from neighbors). 
           Returns new domains or None if contradiction."""
        new_domains = {v: set(domains[v]) for v in domains}
        new_domains[var] = {val}
        # forward checking: remove val from neighbors
        for n in self.neighbors[var]:
            if val in new_domains[n]:
                new_domains[n] = set(new_domains[n] - {val})
                if len(new_domains[n]) == 0:
                    return None
        return new_domains

    def backtrack(self, domains=None):
        if domains is None:
            domains = {v: set(self.domains[v]) for v in self.domains}

        # If assignment complete
        if all(len(domains[v]) == 1 for v in self.cells):
            return domains

        var = self.select_unassigned_variable_from_domains(domains)
        if var is None:
            return domains
        for value in self.order_domain_values_from_domains(var, domains):
            # check consistency with current domains (no neighbor assigned same single value)
            if self.is_value_consistent_in_domains(var, value, domains):
                # create copy and assign with forward checking
                new_domains = {v: set(domains[v]) for v in domains}
                new_domains[var] = {value}
                # forward check: remove value from neighbors
                failed = False
                for n in self.neighbors[var]:
                    if value in new_domains[n]:
                        new_domains[n] = set(new_domains[n] - {value})
                        if len(new_domains[n]) == 0:
                            failed = True
                            break
                if failed:
                    continue
                # further enforce AC-3 on the new_domains (inference)
                saved_domains = self.domains
                self.domains = new_domains
                if self.ac3():
                    result = self.backtrack(self.domains)
                    if result is not None:
                        return result
                # restore domains and continue
                self.domains = saved_domains
        return None

    # Helpers that operate on an arbitrary domains dict (used for backtracking heuristics)
    def select_unassigned_variable_from_domains(self, domains):
        unassigned = [cell for cell in self.cells if len(domains[cell]) > 1]
        if not unassigned:
            return None
        mrv = min(len(domains[cell]) for cell in unassigned)
        candidates = [cell for cell in unassigned if len(domains[cell]) == mrv]
        if len(candidates) == 1:
            return candidates[0]
        best = max(candidates, key=lambda c: sum(1 for n in self.neighbors[c] if len(domains[n])>1))
        return best

    def order_domain_values_from_domains(self, var, domains):
        domain = list(domains[var])
        def count_conflicts(val):
            count = 0
            for n in self.neighbors[var]:
                if val in domains[n]:
                    count += 1
            return count
        domain.sort(key=count_conflicts)
        return domain

    def is_value_consistent_in_domains(self, var, val, domains):
        for n in self.neighbors[var]:
            if len(domains[n]) == 1 and val in domains[n]:
                return False
        return True


# ---------------- Example usage ----------------
if __name__ == "__main__":
    # Example Sudoku (medium hardness). 0 or . denotes empty cells.
    puzzle = (
        "530070000"
        "600195000"
        "098000060"
        "800060003"
        "400803001"
        "700020006"
        "060000280"
        "000419005"
        "000080079"
    )
    print("Input puzzle (0 = empty):")
    csp = SudokuCSP(puzzle)
    csp.display()

    # initial AC-3 to prune domains
    print("Running AC-3 initial propagation...")
    ac3_ok = csp.ac3()
    print("AC-3 finished:", ac3_ok)
    print("Domains after AC-3 (singletons shown, others as '.'):")
    csp.display()

    print("Starting backtracking search with inference...")
    solution = csp.backtrack()
    if solution:
        print("Sudoku solved!")
        # convert solution domains to assignment dict
        assignment = {cell: next(iter(solution[cell])) for cell in solution}
        csp.display(assignment)
    else:
        print("No solution found.")
