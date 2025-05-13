import networkx as nx

class FreeTopologyNodesHandler:
    """
    This class handles the management of free nodes and their free neighbors in a graph topology.
    
    It provides methods for:
    - Tracking free nodes.
    - Finding the node with the most free neighbors.
    - Marking nodes as occupied and updating the neighbors' free status accordingly.

    Attributes:
        nodes (dict): The nodes in the graph.
        free_nodes (set): A set of nodes that are currently free.
        free_neighbours (list): A list of sets where each set contains the free neighbors of a corresponding node.
    """

    def __init__(self, graph: nx.Graph):
        """
        Initializes the FreeTopologyNodesHandler with the given graph.

        Args:
            graph (nx.Graph): A networkx graph representing the topology, where nodes can be marked as free or occupied.
        """
        self.nodes = graph.nodes  # Store the nodes of the graph
        self.free_nodes = set([u for u in graph.nodes])  # Initialize all nodes as free
        self.free_neighbours = [set() for _ in graph.nodes]  # Initialize an empty set for each node's free neighbors

        # Populate the free_neighbours list with the neighbors of each node
        # This optimization helps in quickly finding the neighbors of free nodes
        for v in graph.nodes:
            for u in graph.neighbors(v):
                self.free_neighbours[v].add(u)  # Add u as a free neighbor of v

    def node_with_most_free_neighbours_set(self, nodes):
        """
        Finds the node with the most free neighbors from a given set of nodes.

        Args:
            nodes (iterable): A collection of nodes to check.

        Returns:
            tuple: The node with the most free neighbors and its free neighbors.
        """
        # Select the node with the most free neighbors using a max function
        node, _ = max([(v, len(self.free_neighbours[v])) for v in nodes], key=lambda el: el[1])
        return node, self.get_free_neighbours(node)  # Return the node and its free neighbors

    def free_node_with_most_free_neighbours(self):
        """
        Finds the free node with the most free neighbors.

        Returns:
            tuple: The free node with the most free neighbors and its free neighbors.
        """
        return self.node_with_most_free_neighbours_set(self.free_nodes)

    def get_free_neighbours(self, v):
        """
        Gets the free neighbors of a specific node.

        Args:
            v (node): The node for which to retrieve the free neighbors.

        Returns:
            set: A set of free neighbors for the node v.
        """
        return self.free_neighbours[v]

    def occupy_node(self, v):
        """
        Marks a node as occupied, removing it from the free nodes and updating the free neighbors accordingly.

        Args:
            v (node): The node to occupy.
        """
        # Remove the node v from the set of free nodes
        self.free_nodes.remove(v)
        # Update the free neighbors of other nodes to reflect that v is now occupied
        for w in self.nodes:
            self.free_neighbours[w].discard(v)  # Remove v from the free neighbors of all other nodes