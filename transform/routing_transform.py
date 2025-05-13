import pennylane as qml
from pennylane.tape import QuantumTape
import networkx as nx
from mapper.base import MapperType, MapperUpdater
from router import Router
from math import log2
import logging
from time import time_ns

# Setup logger for logging routing information to a file
logger = logging.getLogger(__name__)

# Because of the explanation given in the following error:
# pennylane.transforms.core.transform_dispatcher.TransformError: Decorating a QNode with @transform_fn(**transform_kwargs) has been removed. Please decorate with @functools.partial(transform_fn, **transform_kwargs) instead, or call the transform directly using qnode = transform_fn(qnode, **transform_kwargs). 
# I just called the method apply_routing (is suggested by the error string)

def apply_routing(tape: QuantumTape, connectivity: nx.Graph, mapper_type: str):
    """
    This function applies a routing transformation to a quantum circuit (represented by a QuantumTape) 
    by mapping logical qubits to physical qubits on a given connectivity graph. 
    The routing procedure includes creating an initial mapping, updating the mapping using a lookahead strategy, 
    and applying the routing algorithm to perform swaps where necessary.

    Args:
        tape (QuantumTape): The quantum tape representing the quantum circuit.
        connectivity (nx.Graph): The graph representing the physical qubit connectivity.
        mapper_type (str): The type of the initial mapping strategy (e.g., 'greedy', 'random', etc.).
    
    Returns:
        tuple: A tuple containing:
            - new_ops (list): A list of operations with the updated swaps applied.
            - measurements (list): List of measurements in the tape.
            - logical_qubits (int): Number of logical qubits.
    """
    # Initialize the log file for the routing procedure with a timestamp
    logging.basicConfig(filename='log/routing_transformation_' + str(time_ns())  + '.log', level=logging.INFO)
    logger.info("Starting routing procedure")
    
    # Initialize a list to store new operations with swaps
    new_ops = []

    # Generate a list of CNOT interactions from the quantum tape
    cnots_list = get_interaction_list(tape)
    logger.info("CNOTS to execute are: %s", cnots_list)

    # Add ancilla qubits to match the number of logical and physical qubits
    logger.info("Adding ancilla qubits to pad the number of logical and physical qubits")
    logical_qubits = len(tape.wires)  # Number of logical qubits (based on the tape's wires)
    physical_qubits = connectivity.number_of_nodes()  # Number of physical qubits (from the connectivity graph)
    
    # Check if the circuit has enough physical qubits for the logical qubits
    if logical_qubits > physical_qubits:
        raise RuntimeError("Circuit failed to compile: topology does not contain enough physical qubits to contain all of the logic ones")
    
    # Compute padding if there are more physical qubits than logical ones
    padding = physical_qubits - logical_qubits
    logical_qubits = logical_qubits + padding  # Update logical qubits count with padding

    # Compute initial mapping using the provided strategy
    logger.info("Computing initial mapping with strategy %s", mapper_type)
    mapper = MapperType.MapperType.mapper_from_string(mapper_type, connectivity, cnots_list, logical_qubits)

    # Update the initial mapping using a lookahead strategy
    logger.info("Updating initial mapping using %d cnots", int(log2(len(cnots_list))))
    lookahead = 10  # Number of CNOTs to look ahead for the update strategy
    mapper_updater = MapperUpdater.MapperUpdater(connectivity, mapper, cnots_list[:int(log2(len(cnots_list)))], lookahead)
    mapper = mapper_updater.update_mapping()

    # Perform the routing of the entire set of CNOT operations
    logger.info("Routing the complete set of two qubits operations")
    router = Router.Router(connectivity, mapper, cnots_list, lookahead)

    # Get the number of swaps and the list of swap operations
    swaps_count, swaps = router.route_circuit()
    
    logger.info("Number of swaps required: %d", swaps_count)
    logger.info("Starting from following logical to physical mapping: %s", mapper.l_to_p)
    logger.info("Starting from following physical to logical mapping: %s", mapper.p_to_l)
    logger.info("Swaps required: %s", swaps)

    # Update the quantum circuit with the swaps
    new_ops = __update_circuit(tape, swaps, connectivity.number_of_nodes())
    
    return new_ops, tape.measurements, logical_qubits


def get_interaction_list(tape):
    """
    Generates a list of all pairs of qubits interacting in the quantum circuit represented by the tape. 
    The list also includes the index of the operation for each pair, to track which CNOT operation the pair appears in.

    Args:
        tape (QuantumTape): The quantum tape representing the quantum circuit.
    
    Returns:
        list: A list of tuples representing interacting qubit pairs and their operation index.
    """
    interaction_list = []
    op_count = 0  # Operation counter
    # Iterate through the operations in the tape
    for op in tape.operations:
        wires = op.wires
        # Only consider operations with at least two qubits (CNOT operations)
        if len(wires) >= 2:
            # Add all pairs of interacting qubits to the interaction list
            for i in range(len(wires)):
                for j in range(i + 1, len(wires)):
                    interaction_list.append((wires[i], wires[j], op_count))
                    op_count += 1

    return interaction_list


@staticmethod
def __update_circuit(tape, swaps, qubits):
    """
    Updates the quantum circuit by applying the swaps calculated during the routing procedure.
    This function modifies the operations in the tape by updating the qubit mappings and inserting SWAP operations.

    Args:
        tape (QuantumTape): The quantum tape representing the quantum circuit.
        swaps (list): A list of swap operations, where each entry contains the swaps for a given CNOT operation.
        qubits (int): The number of qubits in the circuit (both logical and physical).
    
    Returns:
        list: A list of updated quantum operations with the SWAP operations applied.
    """
    new_ops = []  # List to store new operations with swaps
    current_wires = {i : i for i in range(qubits)}  # Mapping from logical qubits to physical qubits

    # Iterate through the operations in the tape
    for op in tape.operations:
        wires = op.wires
        # If the operation involves only one qubit, update its mapping directly
        if len(wires) == 1:
            op = qml.map_wires(op, current_wires)
            new_ops.append(op)
        else:
            # For multi-qubit operations (CNOTs), apply the necessary swaps
            swaps_for_current_operation = swaps[0]  # Get the swaps for this operation
            swaps = swaps[1:]  # Remove the first swap entry from the list
            
            if len(swaps_for_current_operation) != 0:
                # Apply SWAP operations for both control and target qubits
                control_movements = swaps_for_current_operation[0]
                target_movements = swaps_for_current_operation[1]

                # Apply SWAP operations for control qubits
                for (q1, q2) in control_movements:
                    new_ops.append(qml.SWAP(wires=[current_wires[q1], current_wires[q2]]))
                    # Update the qubit mapping after the swap
                    aux = current_wires[q1]
                    current_wires[q1] = current_wires[q2]
                    current_wires[q2] = aux

                # Apply SWAP operations for target qubits
                for (q1, q2) in target_movements:
                    new_ops.append(qml.SWAP(wires=[current_wires[q1], current_wires[q2]]))
                    # Update the qubit mapping after the swap
                    aux = current_wires[q1]
                    current_wires[q1] = current_wires[q2]
                    current_wires[q2] = aux

            # Apply the operation with the updated wire mapping
            op = qml.map_wires(op, current_wires)
            new_ops.append(op)

    return new_ops