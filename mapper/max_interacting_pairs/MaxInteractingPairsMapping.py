from mapper.base.Mapper import Mapper
import networkx as nx
from mapper.max_interacting_pairs.utils.QubitInteractionsHandler import QubitInteractionsHandler
from mapper.max_interacting_pairs.utils.FreeTopologyNodesHandler import FreeTopologyNodesHandler
import logging 

logger = logging.getLogger(__name__)

class MaxInteractingPairsMapping(Mapper):
    """
    This class implements the max interacting pairs mapping strategy for quantum circuits.

    It attempts to find the best mapping between logical qubits and physical qubits by:
    1. Maximizing the number of interactions between qubits during mapping.
    2. Prioritizing physical nodes that have the most free neighbors, while mapping logical qubits to them.
    3. Iteratively handling neighbors to ensure maximum interaction between qubits and nodes.
    """

    def __init__(self, connectivity: nx.Graph, cnots_list : list, qubits : int):   
        """
        Initializes the MaxInteractingPairsMapping object by computing the initial mapping between 
        logical and physical qubits using the max-interacting-pairs strategy.

        Args:
            connectivity (nx.Graph): The connectivity graph representing the physical qubits and their connections.
            cnots_list (list): The list of CNOT operations between logical qubits.
            qubits (int): The total number of qubits in the quantum system.
        """
        super().__init__(connectivity, cnots_list, qubits)
        logger.info("Computing max interacting pairs mapping between logical and physical qubits")
        self.l_to_p = [-1 for _ in range(qubits)]  # Mapping from logical qubits to physical qubits
        self.p_to_l = [-1 for _ in range(qubits)]  # Mapping from physical qubits to logical qubits
        self.compute_mapping()  # Computes the initial mapping
        logger.info("Initial Logic to Physic mapping: %s", self.l_to_p)
        logger.info("Initial Physic to Logic mapping: %s", self.p_to_l)

    def compute_mapping(self) -> list:
        """
        Computes the mapping between logical qubits and physical qubits using the max-interacting-pairs strategy.

        This method iteratively selects free qubits and physical nodes, mapping them in such a way that maximizes 
        the number of interactions between qubits.

        Returns:
            list: The final mapping between logical qubits and physical qubits.
        """
        # ------------------------------------------------------------------------------- #
        # Computing all of the useful structures

        # 1. Interactions count
        qubit_interactions = QubitInteractionsHandler(self.cnots_list, self.qubits)

        # 2. Graph Topology handler
        topology_handler = FreeTopologyNodesHandler(self.connectivity)

        # 3. List of next in queue qubits/nodes to handle
        queue = []

        # 4. What is left?
        to_do = self.qubits

        while to_do != 0:
            if len(queue) == 0:  # if no old result must be handled
                logger.info("No previous pair was left to be handled. Picking a fresh pair node-qubit with the max-interacting-pairs strategy")
                
                # 5.1. Pick the free node with the greater amount of free neighbours
                node, node_neighbours = topology_handler.free_node_with_most_free_neighbours()
                logger.info("The free node with the greater number of free neighbours is %d", node)
                logger.info("Such node has %d free neighbours", len(node_neighbours))

                # 5.2. Find the (not mapped) qubit that maximises the number of interactions with d qubits 
                qubit, qubit_neighbours = qubit_interactions.qubit_with_most_d_interactions(len(node_neighbours))
                logger.info("The qubit that maximise the number of interactions with other %d qubits is: %d", len(node_neighbours), qubit)
                logger.info("Such qubit interacts with other %d (yet to be mapped) qubits", len(qubit_neighbours))

                # 5.3. Store the mapping
                self.l_to_p[qubit] = node 
                self.p_to_l[node] = qubit
                logger.info("Mapping qubit %d to node %d", qubit, node)

                to_do -= 1

                # 5.4. Update auxiliary structure
                topology_handler.occupy_node(node)
                qubit_interactions.map_qubit(qubit)

            else:  # handling nodes coming from previous iterations
                node = queue[0][0]
                qubit = queue[0][1]
                logger.info("A pair qubit-node was left to be handled from some previous iteration.")
                logger.info("Current handled pair is qubit: %d, node: %d", qubit, node)

                queue = queue[1:]  # removing 

                node_neighbours = topology_handler.get_free_neighbours(node)
                logger.info("Node %d has %d free neighbours", node, len(neighbour_neighbours))
                qubit_neighbours = qubit_interactions.d_interactions(qubit, len(node_neighbours))
                logger.info("It interacts with %d (yet to be mapped) qubits", len(qubit_neighbours))
            
            # This could be removed...
            iters = min(len(qubit_neighbours), len(node_neighbours))

            for i in range(iters):
                # 5.5. Pick the node, between node_neighbours, with bigger amount free neighbours
                neighbour, neighbour_neighbours = topology_handler.node_with_most_free_neighbours_set(node_neighbours)
                logger.info("The free neighbour of %d with the greater amount of free neighbours is %d", node, neighbour)
                logger.info("It has %d free neighbours", len(neighbour_neighbours))

                # 5.6. map neighbour to the qubit, between qubit_neighbours, that maximizes the number of len(neighbour_neighbours) interactions
                neighbour_qubit, neighbour_qubit_interactions = qubit_interactions.qubit_with_most_d_interactions_from_set(len(neighbour_neighbours), qubit_neighbours)
                logger.info("The (yet to be mapped) qubit that maximise the number of interactions with other %d qubits is %d. Note that %d is picked only between the qubits interacting with %d",  len(neighbour_neighbours), neighbour_qubit, neighbour_qubit, qubit)
                logger.info("It interacts with %d (yet to be mapped) qubits", len(neighbour_qubit_interactions))

                if qubit != -1:
                    qubit_interactions.map_qubit(neighbour_qubit)
                    topology_handler.occupy_node(neighbour)

                    # 5.7. Store mapping 
                    self.l_to_p[neighbour_qubit] = neighbour
                    self.p_to_l[neighbour] = neighbour_qubit
                    logger.info("Mapping qubit %d to node %d", neighbour_qubit, neighbour)

                    to_do -= 1

                    # 5.8. Update structures
                    node_neighbours.discard(neighbour)
                    qubit_neighbours.discard(neighbour_qubit)

                    # 5.9. Recall that the next iterations must handle the neighbours of node first
                    queue.append((neighbour, neighbour_qubit))