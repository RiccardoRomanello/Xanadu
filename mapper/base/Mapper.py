import networkx as nx
import logging

logger = logging.getLogger(__name__)

class Mapper:
    """
    Mapper handles the mapping between logical and physical qubits for quantum circuit compilation.
    
    It maintains bidirectional mappings between logical and physical qubits,
    taking into account the connectivity constraints given as a graph.

    Attributes:
        connectivity (nx.Graph): The graph defining physical qubit connectivity.
        cnots_list (list): A list of CNOT operations (as tuples of qubit indices).
        qubits (int): Total number of qubits in the circuit.
        l_to_p (list): Mapping from logical to physical qubits.
        p_to_l (list): Mapping from physical to logical qubits.
    """

    def __init__(self, connectivity: nx.Graph, cnots_list: list, qubits: int):
        """
        Initializes the Mapper with default one-to-one logical-to-physical mapping.

        Args:
            connectivity (nx.Graph): A graph representing physical qubit connectivity.
            cnots_list (list): List of CNOT gate pairs (logical qubit indices).
            qubits (int): Number of qubits in the circuit.
        """
        logger.info("Init Basic Mapper")
        self.connectivity = connectivity
        self.cnots_list = cnots_list
        self.qubits = qubits

        # l_to_p[q] = u <-> logical qubit q is mapped to physical node u
        self.l_to_p = [i for i in range(qubits)]
        # p_to_l[u] = q <-> physical node u hosts logical qubit q
        self.p_to_l = [i for i in range(qubits)]
        logger.info("Each qubit has been mapped to the node with the same index in the topology")

    def physic_to_logical(self) -> list:
        """
        Recomputes the physical-to-logical mapping based on the current logical-to-physical mapping.

        Returns:
            list: Updated p_to_l list where p_to_l[u] = q indicates physical node u hosts logical qubit q.
        """
        for q, v in enumerate(self.l_to_p):
            self.p_to_l[v] = q

    def get_physic_to_logical(self) -> list:
        """
        Returns the current mapping from physical qubits to logical qubits.

        Returns:
            list: Mapping list where p_to_l[u] = q.
        """
        return self.p_to_l

    def get_logical_to_physic(self) -> list:
        """
        Returns the current mapping from logical qubits to physical qubits.

        Returns:
            list: Mapping list where l_to_p[q] = u.
        """
        return self.l_to_p

    def compute_mapping(self):
        """
        Stub method to be overridden in subclasses.
        Intended to compute a mapping strategy from logical to physical qubits.

        Returns:
            None
        """
        pass

    @staticmethod
    def from_static_mapping(connectivity, cnots_list: list, qubits: int, l_to_p: list, p_to_l: list):
        """
        Initializes a Mapper from a predefined static mapping.

        Args:
            connectivity (nx.Graph): A graph representing physical qubit connectivity.
            cnots_list (list): List of CNOT gate pairs (logical qubit indices).
            qubits (int): Number of qubits.
            l_to_p (list): Predefined logical-to-physical mapping.
            p_to_l (list): Predefined physical-to-logical mapping.

        Returns:
            Mapper: An instance of Mapper initialized with the given mappings.
        """
        mapper = Mapper(connectivity, cnots_list, qubits)
        mapper.l_to_p = l_to_p.copy()
        mapper.p_to_l = p_to_l.copy()
        logger.info("Initialized a mapper from a pre-computed mapping")
        logger.info("Logical to physical mapping: %s", l_to_p)
        logger.info("Physical to logical mapping: %s", p_to_l)
        return mapper
