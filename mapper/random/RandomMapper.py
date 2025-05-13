from mapper.base.Mapper import Mapper
import networkx as nx
import random as rnd
import logging

logger = logging.getLogger(__name__)

class RandomMapper(Mapper):
    """
    A Mapper that randomly assigns logical qubits to physical qubits.

    This class extends the base Mapper class by overriding the mapping strategy
    with a uniform random permutation of logical-to-physical qubit assignments.
    """

    def __init__(self, connectivity: nx.Graph, cnots_list: list, qubits: int):
        """
        Initializes the RandomMapper and computes a random initial mapping.

        Args:
            connectivity (nx.Graph): The physical qubit connectivity graph.
            cnots_list (list): List of CNOT operations (logical qubit pairs).
            qubits (int): Total number of logical qubits in the circuit.
        """
        super().__init__(connectivity, cnots_list, qubits)
        logger.info("Computing random mapping between logical and physical qubits")
        self.compute_mapping()
        logger.info("Initial Logic to Physic mapping: %s", self.l_to_p)
        logger.info("Initial Physic to Logic mapping: %s", self.p_to_l)

    def compute_mapping(self) -> list:
        """
        Computes a random permutation of the logical-to-physical mapping.

        This method modifies `self.l_to_p` in-place using random shuffling,
        and updates the reverse mapping (`self.p_to_l`) accordingly.

        Returns:
            list: The updated logical-to-physical mapping.
        """
        rnd.shuffle(self.l_to_p)  # randomly shuffling qubits to nodes
        self.physic_to_logical()  # update reverse mapping