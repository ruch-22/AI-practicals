import itertools
import math
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import json

np.random.seed(42)

# -------------------------------------------------
# Generate synthetic dataset
# -------------------------------------------------
def generate_synthetic_data(n=2000):
    data = pd.DataFrame(index=range(n), columns=list("ABCDE"))

    data['A'] = (np.random.rand(n) < 0.5).astype(int)

    data['B'] = [np.random.rand() < (0.8 if a == 1 else 0.1) for a in data['A']]
    data['B'] = pd.Series(data['B']).astype(int)

    data['C'] = [np.random.rand() < (0.7 if a == 1 else 0.2) for a in data['A']]
    data['C'] = pd.Series(data['C']).astype(int)

    def p_D(b, c):
        if b == 1 and c == 1: return 0.9
        if b == 1 and c == 0: return 0.6
        if b == 0 and c == 1: return 0.5
        return 0.05

    data['D'] = [np.random.rand() < p_D(b, c) for b, c in zip(data['B'], data['C'])]
    data['D'] = pd.Series(data['D']).astype(int)

    data['E'] = [np.random.rand() < (0.75 if c == 1 else 0.2) for c in data['C']]
    data['E'] = pd.Series(data['E']).astype(int)

    return data


# -------------------------------------------------
# Mutual Information
# -------------------------------------------------
def mutual_information(x, y):
    joint = pd.crosstab(x, y, normalize=True)
    px = joint.sum(axis=1)
    py = joint.sum(axis=0)
    mi = 0.0
    for xi in joint.index:
        for yj in joint.columns:
            pxy = joint.loc[xi, yj]
            if pxy > 0:
                mi += pxy * math.log(pxy / (px[xi] * py[yj]), 2)
    return mi


# -------------------------------------------------
# Chow-Liu Tree
# -------------------------------------------------
def chow_liu_tree(data):
    vars_ = list(data.columns)
    edges = []

    # compute mutual information for all pairs
    for i in range(len(vars_)):
        for j in range(i + 1, len(vars_)):
            mi = mutual_information(data[vars_[i]], data[vars_[j]])
            edges.append((vars_[i], vars_[j], mi))

    # sort by descending MI
    edges_sorted = sorted(edges, key=lambda e: -e[2])

    # Kruskal's MST
    parent = {v: v for v in vars_}

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    def union(a, b):
        ra, rb = find(a), find(b)
        parent[rb] = ra

    tree_edges = []
    for u, v, mi in edges_sorted:
        if find(u) != find(v):
            union(u, v)
            tree_edges.append((u, v, mi))
        if len(tree_edges) == len(vars_) - 1:
            break

    return tree_edges


# -------------------------------------------------
# Entropy
# -------------------------------------------------
def entropy(s):
    probs = s.value_counts(normalize=True)
    return -sum(p * math.log(p, 2) for p in probs if p > 0)


# -------------------------------------------------
# Orient the Chow-Liu tree
# -------------------------------------------------
def orient_tree(tree_edges, data):
    adj = defaultdict(list)
    for u, v, mi in tree_edges:
        adj[u].append(v)
        adj[v].append(u)

    entropies = {v: entropy(data[v]) for v in data.columns}
    root = max(entropies, key=entropies.get)

    parents = {root: None}
    q = deque([root])

    while q:
        node = q.popleft()
        for nb in adj[node]:
            if nb not in parents:
                parents[nb] = node
                q.append(nb)

    return root, parents


# -------------------------------------------------
# Estimate Conditional Probability Tables (CPTs)
# -------------------------------------------------
def estimate_cpts(data, parents):
    cpts = {}
    for var, parent in parents.items():
        if parent is None:  # root variable
            counts = data[var].value_counts().to_dict()
            total = len(data)
            values = sorted(data[var].unique())
            probs = {}
            for val in values:
                probs[(val,)] = (counts.get(val, 0) + 1) / (total + len(values))
            cpts[var] = {'parent': None, 'probs': probs, 'values': values}
        else:  # child variable
            probs = {}
            values = sorted(data[var].unique())
            parent_values = sorted(data[parent].unique())
            for pv in parent_values:
                subset = data[data[parent] == pv]
                total = len(subset)
                counts = subset[var].value_counts().to_dict()
                for val in values:
                    probs[(val, pv)] = (counts.get(val, 0) + 1) / (total + len(values))
            cpts[var] = {
                'parent': parent,
                'probs': probs,
                'values': values,
                'parent_values': parent_values
            }
    return cpts


# -------------------------------------------------
# Inference Functions
# -------------------------------------------------
def joint_probability(assignment, parents, cpts):
    prob = 1.0
    for var, parent in parents.items():
        if parent is None:
            prob *= cpts[var]['probs'][(assignment[var],)]
        else:
            prob *= cpts[var]['probs'][(assignment[var], assignment[parent])]
    return prob


def enumerate_all(vars_, evidence, parents, cpts):
    hidden = [v for v in vars_ if v not in evidence]
    total_prob = 0.0
    for prod in itertools.product([0, 1], repeat=len(hidden)):
        full_assign = dict(evidence)
        full_assign.update({h: int(val) for h, val in zip(hidden, prod)})
        total_prob += joint_probability(full_assign, parents, cpts)
    return total_prob


def query_probability(query_var, query_val, evidence, data, parents, cpts):
    vars_ = list(data.columns)
    evidence_with_query = dict(evidence)
    evidence_with_query[query_var] = int(query_val)

    numerator = enumerate_all(vars_, evidence_with_query, parents, cpts)
    denominator = enumerate_all(vars_, evidence, parents, cpts)

    if denominator == 0:
        return None
    return numerator / denominator


# -------------------------------------------------
# Run Pipeline
# -------------------------------------------------
data = generate_synthetic_data(n=2000)

tree_edges = chow_liu_tree(data)
root, parents = orient_tree(tree_edges, data)
cpts = estimate_cpts(data, parents)

print("Learned tree edges (undirected with MI):")
for u, v, mi in tree_edges:
    print(f"  {u} -- {v}  (MI={mi:.4f})")

print("\nOriented parents (child: parent):")
for child, parent in parents.items():
    print(f"  {child}: {parent}")

print("\nLearned CPTs (subset shown):")
for var, info in cpts.items():
    print(f"\nVariable: {var}  (parent = {info['parent']})")
    if info['parent'] is None:
        for (val,), p in sorted(info['probs'].items()):
            print(f"  P({var}={val}) = {p:.4f}")
    else:
        parent = info['parent']
        for pv in info['parent_values']:
            row = ", ".join(
                [f"P({var}={val}|{parent}={pv})={info['probs'][(val,pv)]:.3f}"
                 for val in info['values']]
            )
            print(f"  {row}")

# Example Queries
queries = [
    ('B', 1, {}),
    ('C', 1, {'A': 1}),
    ('D', 1, {'B': 1, 'C': 0}),
    ('E', 1, {'C': 1}),
]

print("\nExample inference results:")
for var, val, ev in queries:
    p = query_probability(var, val, ev, data, parents, cpts)
    if p is None:
        print(f"  P({var}={val} | {ev}) = undefined (zero evidence probability)")
    else:
        print(f"  P({var}={val} | {ev}) = {p:.4f}")

# -------------------------------------------------
# Save model to JSON
# -------------------------------------------------
def make_json_safe(obj):
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            if isinstance(k, tuple):
                new_key = ",".join(map(str, k))
            else:
                new_key = str(k)
            new[new_key] = make_json_safe(v)
        return new
    elif isinstance(obj, list):
        return [make_json_safe(x) for x in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        return str(obj)


model = {'root': root, 'parents': parents, 'cpts': cpts}
with open('learned_bn_model.json', 'w') as f:
    json.dump(make_json_safe(model), f, indent=2)

print("\nModel saved to learned_bn_model.json")
