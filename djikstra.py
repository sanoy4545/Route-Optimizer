import heapq

def dijkstra(graph, start):
    n = len(graph)
    distances = [float('inf')] * n
    distances[start] = 0
    pq = [(0, start)]

    while pq:
        dist, u = heapq.heappop(pq)
        if dist > distances[u]:
            continue

        for v, weight in enumerate(graph[u]):
            if weight is not None and distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
                heapq.heappush(pq, (distances[v], v))

    return distances

def find_ideal_sequence(distance_matrix, start=0):
    """
    Returns the ideal visiting sequence starting from the 'start' index,
    using a greedy approach on shortest paths from Dijkstra.
    """
    n = len(distance_matrix)
    
    # Build all-pairs shortest path matrix using Dijkstra
    shortest_paths = [dijkstra(distance_matrix, i) for i in range(n)]

    visited = [False] * n
    sequence = [start]
    visited[start] = True
    current = start

    for _ in range(n - 1):
        nearest = None
        min_dist = float('inf')
        for i in range(n):
            if not visited[i] and shortest_paths[current][i] < min_dist:
                nearest = i
                min_dist = shortest_paths[current][i]
        if nearest is not None:
            sequence.append(nearest)
            visited[nearest] = True
            current = nearest

    return sequence
