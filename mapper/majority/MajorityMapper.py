from mapper.base.Mapper import Mapper
import networkx as nx
from mapper.majority.utils import MaxHeap 
from mapper.majority.utils import KeyValMaxHeapObj
import logging

logger = logging.getLogger(__name__)

class MajorityMapper(Mapper):
    """
    MajorityMapper handles the mapping between logical and physical qubits using a majority-based strategy.
    
    This strategy involves sorting the logical qubits by the number of interactions (CNOT operations) and
    sorting the physical qubits by their number of neighbors in the connectivity graph. The qubit with the
    most interactions is mapped to the physical node with the most neighbors.
    
    Attributes:
        interact (list): A list of sets where interact[i] contains the qubits that logical qubit i interacts with.
        heap (MaxHeap): A max heap used to prioritize qubits based on the number of interactions.
        graph_neighbours_heap (MaxHeap): A max heap used to prioritize physical qubits based on the number of neighbors.
    """

    def __init__(self, connectivity: nx.Graph, cnots_list: list, qubits: int):
        """
        Initializes the MajorityMapper with connectivity graph, CNOT operations, and the number of qubits.

        Args:
            connectivity (nx.Graph): A graph representing physical qubit connectivity.
            cnots_list (list): List of CNOT gate pairs (logical qubit indices).
            qubits (int): Number of qubits in the circuit.
        """
        super().__init__(connectivity, cnots_list, qubits)  # Initialize the base Mapper class
        logger.info("Computing majority mapping between logical to physical qubits")
        
        # Initialize interactions for each logical qubit
        self.interact = [set() for _ in range(qubits)]  # interact[i] = the set of qubits i interacts with
        for (i, j, _) in cnots_list:
            self.interact[i].add(j)
            self.interact[j].add(i)

        # Create a max heap for logical qubits based on the number of interactions
        self.heap = MaxHeap()
        for q in range(qubits):
            pair = KeyValMaxHeapObj(q, len(self.interact[q]))  # pair = (logical qubit, number of interactions)
            self.heap.heappush(pair)  # Push the qubit onto the heap with its interaction count

        # Create a max heap for physical qubits based on the number of neighbors in the connectivity graph
        self.graph_neighbours_heap = MaxHeap()
        connectivity_nodes_neighbour_size = [
            KeyValMaxHeapObj(u, len(list(self.connectivity.adj(u)))) for u in list(self.connectivity.nodes)
        ]

        # Push each physical qubit and its neighbor count onto the heap
        for el in connectivity_nodes_neighbour_size:
            self.graph_neighbours_heap.heappush(el)
        
        # Compute the initial mapping between logical and physical qubits
        self.compute_mapping()
        logger.info("Initial Logic to Physic mapping: %s", self.l_to_p)
        logger.info("Initial Physic to Logic mapping: %s", self.p_to_l)


    def compute_mapping(self):
        """
        Computes the mapping between logical qubits and physical qubits using the majority strategy.
        
        The method iterates through all qubits, selects the qubit with the most interactions,
        and maps it to the physical node with the most neighbors.
        
        """
        for _ in range(self.qubits): 
            # Pop the qubit with the most interactions
            qubit_heap_max = self.heap.heappop()
            # Pop the physical node with the most neighbors
            node_heap_max = self.graph_neighbours_heap.heappop()

            qubit = qubit_heap_max.key
            node = node_heap_max.key

            # Log information about the selected qubit and node
            logger.info("The (yet to be mapped) qubit that interacts with the greater amount of other qubits is %d", qubit)
            logger.info("The free node with the greater amount of neighbours is %d", node)

            # Perform the mapping
            self.l_to_p[qubit] = node
            self.p_to_l[node] = qubit

            # Log the mapping
            logger.info("Mapping qubit %d to node %d", qubit, node)