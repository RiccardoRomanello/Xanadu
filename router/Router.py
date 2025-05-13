from mapper.base.Mapper import Mapper
from router.utils.UnweightedUndirectedGraph import UnweightedUndirectedGraph
import networkx as nx
from math import ceil
from random import choice

import logging
logger = logging.getLogger(__name__)

class Router:
    """
    Router class handles the routing of a quantum circuit's CNOT operations
    by moving qubits across the physical qubit topology. It minimizes swaps 
    by analyzing the connectivity of qubits and leveraging lookahead strategies.
    """
    
    def __init__(self, topology: nx.Graph, mapper : Mapper, cnots_list : list, lookahead : int):
        """
        Initializes the Router with a quantum circuit's CNOTs, the mapping between logical and physical qubits, 
        and the physical topology of the qubits.
        
        Args:
            topology (nx.Graph): The physical qubit network topology represented as an undirected graph.
            mapper (Mapper): The current mapping between logical qubits and physical qubits.
            cnots_list (list): A list of CNOT operations to be routed.
            lookahead (int): The number of subsequent CNOTs to look ahead in the routing strategy.
        """
        self.l_to_p = mapper.l_to_p.copy()
        self.p_to_l = mapper.p_to_l.copy()

        logger.info("Creating router with the following initial mapping:")
        logger.info("Logical to physical: %s", mapper.l_to_p)
        logger.info("Physical to logical: %s", mapper.p_to_l)
        logger.info("Routing the following set of CNOTS: %s", cnots_list)

        self.cnots_list = cnots_list
        self.lookahead = lookahead
        self.topology = UnweightedUndirectedGraph(topology.number_of_nodes())
        self.topology.from_nx(topology)
        self.topology.floyd_warshall()

    def get_current_mapping(self):
        """
        Returns the current mapping between logical and physical qubits.

        Returns:
            tuple: A tuple containing two lists:
                - logical to physical mapping (`l_to_p`)
                - physical to logical mapping (`p_to_l`)
        """
        return self.l_to_p, self.p_to_l

    def __swap_strategy_by_lookahead(self, begin : int, control : int, target : int):
        """
        Determines the strategy for moving the control or target qubit based on the next `lookahead` CNOTs.
        It considers the number of operations involving each qubit and selects the qubit to move or swap.
        
        Args:
            begin (int): The index to start looking at in the CNOT list.
            control (int): The logical qubit representing the control qubit in the CNOT operation.
            target (int): The logical qubit representing the target qubit in the CNOT operation.
        
        Returns:
            int: A decision on which qubit to move (-1 for both, `control` for control qubit, `target` for target qubit).
        """
        logger.info("Getting informations on next %d cnots", self.lookahead)
        logger.info("Will be used to decide whether to move control or target")

        operations = self.cnots_list[begin:min(begin + self.lookahead, len(self.cnots_list))]
        control_count = sum([1 for (c, t, _) in operations if c == control or t == control])
        target_count = sum([1 for (c, t, _) in operations if c == target or t == target])

        if control_count == 0 and target_count == 0: 
            logger.info("Both control and target are not effected by next %d cnots. Randomly picking the strategy", self.lookahead)
            return choice([control, target, -1])
        elif control_count == 0 or control_count >= 2*target_count: 
            logger.info("Since (i) either the control is not used or (ii) used twice with respect to target in the next %d operations", self.lookahead)
            logger.info("Target qubit will be routed all way to the control")
            return target
        elif target_count == 0 or target_count >= 2*control_count:
            logger.info("Since (i) either the target is not used or (ii) used twice with respect to control in the next %d operations", self.lookahead)
            logger.info("Control qubit will be routed all way to the target")
            return control 
        else:
            logger.info("Since no particular information have been gathered using the %d subsequent cnots", self.lookahead)
            logger.info("Half of the path will be done by target and the other half by control")
            return -1
            
    def __move_through_path(self, qubit : int, qubit_node : int, path : list):
        """
        Moves a qubit through a given path of nodes, updating the logical-to-physical and physical-to-logical mappings 
        accordingly. This is done by swapping the qubit with the qubits already mapped to the nodes in the path.
        
        Args:
            qubit (int): The logical qubit to be moved.
            qubit_node (int): The current physical node where the qubit is mapped.
            path (list): A list of nodes through which the qubit needs to be moved.
        
        Returns:
            tuple: A list of swap operations and the total number of swaps performed.
        """
        swaps = 0
        swaps_list = []

        logger.info("Moving qubit %d, mapped to node %d, towards the following path of nodes %s", qubit, qubit_node, path)

        for node in path:
            swap_qubit = self.p_to_l[node]
            swaps_list.append((qubit, swap_qubit))
            self.p_to_l[node] = qubit
            self.p_to_l[qubit_node] = swap_qubit
            self.l_to_p[qubit] = node
            self.l_to_p[swap_qubit] = qubit_node 

            qubit_node = node

            swaps += 1
            
        return swaps_list, swaps

    def __apply_cnot(self, control : int, target : int, i : int):
        """
        Applies a CNOT operation between the control and target qubits, ensuring that they are mapped 
        to adjacent physical qubits. If they are not adjacent, it finds the shortest path to swap them.
        
        Args:
            control (int): The logical control qubit.
            target (int): The logical target qubit.
            i (int): The index of the current CNOT operation in the list.
        
        Returns:
            tuple: A list of swaps performed and the total number of swaps required to apply the CNOT.
        """
        logger.info("Attempt at doing cnot between qubit %d and qubit %d", control, target)
        swaps_count = 0
        swaps = []

        control_node = self.l_to_p[control]
        target_node = self.l_to_p[target]

        if self.topology.are_adjacent(control_node, target_node): 
            logger.info("Qubits %d and %d are adjacent according to their mapping (currently mapped in nodes %d and %d, respectively)", control, target, control_node, target_node)
            logger.info("No swap required")
            return [], 0

        logger.info("The two nodes in which the qubits are mapped to are not adjacent")
        logger.info("Using shortest path to move them")

        shortest_path = self.topology.get_shortest_path(control_node, target_node)

        strategy = self.__swap_strategy_by_lookahead(i, control, target)
        
        if strategy == -1:
            logger.info("Half of the path will be done by control, the remainder by target")
            shortest_path_len = len(shortest_path) # number of edges

            if shortest_path_len % 2 == 0:
                control_edges = int(shortest_path_len/2)
                logger.info("Control qubit will be moved of %d edges", control_edges)
            else:
                control_edges = int(ceil(shortest_path_len/2))
                logger.info("Target qubit will be moved of %d edges", control_edges)

            control_path = shortest_path[:control_edges]
            target_path = shortest_path[control_edges:]

            control_path = control_path[1:]
            target_path = target_path[:-1]

        if strategy == control:
            logger.info("Move control all the way to target")
            control_path = shortest_path[1:-1]
            target_path = []
        
        if strategy == target:
            logger.info("Move target all the way to control")
            control_path = []
            target_path = shortest_path[1:-1]
            target_path.reverse()

        logger.info("Path followed by control qubit is:  %s", control_path)
        logger.info("Path followed by target qubit is:  %s", target_path)


        control_swaps, control_swaps_count = self.__move_through_path(control, control_node, control_path)
        target_swaps, target_swaps_count = self.__move_through_path(target, target_node, target_path)
        
        swaps.append(control_swaps)
        swaps.append(target_swaps)

        swaps_count += (control_swaps_count + target_swaps_count)

        return swaps, swaps_count

    def route_circuit(self):
        """
        Routes the entire circuit by applying all the CNOT operations in the provided list.
        
        Returns:
            tuple: A tuple containing:
                - swaps_count (int): Total number of swaps performed.
                - swaps (list): A list of swaps made during routing.
        """
        logger.info("Routing the entire cnot list")
        return self.route_circuit_portion(len(self.cnots_list))
    
    def route_circuit_portion(self, m : int):
        """
        Routes the first `m` CNOT operations in the list, performing any necessary swaps to ensure qubits 
        are mapped to adjacent physical qubits.
        
        Args:
            m (int): The number of CNOT operations to route.
        
        Returns:
            tuple: A tuple containing:
                - swaps_count (int): Total number of swaps performed.
                - swaps (list): A list of swaps made during routing.
        """
        logger.info("Routing the first %d cnots", m)
        swaps_count = 0
        swaps = []

        for c, t, i in self.cnots_list[:m]:
            new_swaps, new_swaps_count = self.__apply_cnot(c, t, i)
            swaps.append(new_swaps)
            swaps_count += new_swaps_count

        return swaps_count, swaps