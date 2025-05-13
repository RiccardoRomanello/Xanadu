import networkx as nx

class UnweightedUndirectedGraph:
    def __init__(self, num_nodes):
        """Initialize the graph with a fixed number of nodes."""
        self.num_nodes = num_nodes
        self.adj_matrix = [[0] * num_nodes for _ in range(num_nodes)]  # Adjacency matrix
        self.dist = None  # Distance matrix (for Floyd-Warshall)
        self.next_node = None  # Matrix to reconstruct shortest paths

    def from_nx(self, graph: nx.Graph):
        for (s, d) in graph.edges:
            self.add_edge(s, d)

    def add_edge(self, u, v):
        """Add an edge between nodes u and v."""
        self.adj_matrix[u][v] = 1
        self.adj_matrix[v][u] = 1

    def floyd_warshall(self):
        """Compute shortest paths between all pairs of nodes using Floyd-Warshall."""
        n = self.num_nodes
        self.dist = [[float('inf')] * n for _ in range(n)]
        self.next_node = [[-1] * n for _ in range(n)]

        # Initialize distances and next_node from adjacency matrix
        for i in range(n):
            for j in range(n):
                if i == j:
                    self.dist[i][j] = 0
                elif self.adj_matrix[i][j] == 1:
                    self.dist[i][j] = 1
                    self.next_node[i][j] = j

        # Floyd-Warshall algorithm
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if self.dist[i][j] > self.dist[i][k] + self.dist[k][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        self.next_node[i][j] = self.next_node[i][k]

    def are_adjacent(self, u, v):
        """Check if nodes u and v are adjacent."""
        return self.adj_matrix[u][v] == 1

    def get_shortest_path(self, start, end):
        """Reconstruct and return the shortest path from start to end."""
        if self.dist is None or self.next_node is None:
            raise ValueError("Floyd-Warshall must be run first to compute shortest paths.")

        if self.dist[start][end] == float('inf'):
            return []  # No path exists

        path = [start]
        while start != end:
            start = self.next_node[start][end]
            if start == -1:
                return []  # No path exists
            path.append(start)
        return path