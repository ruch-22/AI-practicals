import heapq

def prims_mst(graph, V):
    visited = [False] * V
    min_heap = [(0, 0)]  # (cost, start_node)
    mst_cost = 0
    mst_edges = []

    while min_heap:
        cost, u = heapq.heappop(min_heap)
        if visited[u]:
            continue
        visited[u] = True
        mst_cost += cost

        for v, w in graph[u]:
            if not visited[v]:
                heapq.heappush(min_heap, (w, v))
                mst_edges.append((u, v, w))

    return mst_cost, mst_edges


# Graph as adjacency list
V = 5
graph = {
    0: [(1, 2), (2, 3)],
    1: [(0, 2), (2, 1), (3, 4)],
    2: [(0, 3), (1, 1), (3, 5)],
    3: [(1, 4), (2, 5), (4, 7)],
    4: [(3, 7)]
}

mst_cost, mst_edges = prims_mst(graph, V)

print("Minimum Cost of MST:", mst_cost)
print("Edges in MST:", mst_edges)
