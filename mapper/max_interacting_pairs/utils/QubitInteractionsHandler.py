class QubitInteractionsHandler:
    """
    This class handles the interactions between qubits in a quantum circuit, tracking how many interactions 
    each qubit has with others based on the provided list of CNOT operations.
    
    It provides methods to:
    - Track the number of interactions between qubits.
    - Find the qubits with the most interactions.
    - Handle the mapping of qubits based on their interactions.

    Attributes:
        qubits (int): Total number of qubits.
        n (range): A range object representing qubit indices.
        free_qubits (set): A set of qubits that are still free (unmapped).
        interactions_count (list of lists): A 2D matrix storing the number of interactions between each pair of qubits.
    """

    def __init__(self, cnots_list: list, qubits: int):
        """
        Initializes the QubitInteractionsHandler with a list of CNOT operations and a specified number of qubits.

        Args:
            cnots_list (list): A list of CNOT operations represented as tuples (i, j, _), where i and j are qubit indices.
            qubits (int): The total number of qubits in the circuit.
        """
        self.qubits = qubits  # Set the number of qubits
        self.n = range(self.qubits)  # Create a range object for qubit indices

        self.free_qubits = set([q for q in self.n])  # Initially, all qubits are free

        # Initialize a matrix to store interaction counts between qubits
        self.interactions_count = [[0 for _ in self.n] for _ in self.n]
        # Populate the interaction counts based on the CNOT list
        for (i, j, _) in cnots_list:
            self.interactions_count[i][j] += 1
            self.interactions_count[j][i] += 1

    def __get_first_d_free_non_zero(self, d, list):
        """
        Finds the first d free qubits from a sorted list of qubits and their interaction counts 
        that have non-zero interactions.

        Args:
            d (int): The number of qubits to find.
            list (list): A sorted list of tuples (qubit, interaction_count) sorted by interaction_count in descending order.

        Returns:
            set: A set of qubits with the most interactions that are still free.
        """
        result = set()  # Initialize an empty set to store the result
        found = 0  # Track how many free qubits have been found
        for qubit, interactions in list:
            if interactions == 0:  # Stop if interactions count reaches zero
                break
            if qubit in self.free_qubits:  # Only consider free qubits
                result.add(qubit)
                found += 1
                if found == d:  # Stop once we've found d qubits
                    break
        
        return result

    def d_interactions(self, qubit, d):
        """
        Returns the set of d qubits that interact the most with the specified qubit.

        Args:
            qubit (int): The qubit for which we want to find the most interacted qubits.
            d (int): The number of interacting qubits to return.

        Returns:
            set: A set of d qubits that interact the most with the specified qubit.
        """
        # Create a list of pairs (qubit, interaction_count) for the specified qubit
        interactions_count_pairs = [(j, self.interactions_count[qubit][j]) for j in self.n]

        # Sort the list by interaction count in descending order
        interactions_count_pairs.sort(key=lambda e: e[1], reverse=True) 
        
        # Return the first d free qubits with non-zero interactions
        return self.__get_first_d_free_non_zero(d, interactions_count_pairs)
    
    def qubit_with_most_d_interactions_from_set(self, d: int, target_qubits):
        """
        Finds the qubit from a set of target qubits that has the most interactions with its d most-interacting qubits.

        Args:
            d (int): The number of interactions to consider.
            target_qubits (set): A set of qubits to consider.

        Returns:
            tuple: The qubit with the most interactions and its d most-interacting neighbors.
        """
        # Create a list of interactions for each qubit
        interactions_count_pairs = [[(j, self.interactions_count[i][j]) for j in self.n] for i in self.n]

        # Sort each qubit's interaction list by interaction count in descending order
        for i in self.n:
            interactions_count_pairs[i].sort(key=lambda e: e[1], reverse=True)

        # Track the qubit with the highest sum of interactions with the top d neighbors
        max_i = -1
        max_val = -1

        for i in self.n:
            if i in target_qubits:
                total_interactions = 0
                # Sum the interactions with the first d free neighbors
                for k in range(d):
                    if interactions_count_pairs[i][k][0] in self.free_qubits:
                        total_interactions += interactions_count_pairs[i][k][1]

                if total_interactions > max_val:
                    max_i = i
                    max_val = total_interactions

        # The candidate qubit with the most interactions
        candidate = max_i

        # Get the d most-interacting neighbors of the candidate qubit
        candidate_d_neighbours = self.__get_first_d_free_non_zero(d, interactions_count_pairs[candidate])
        
        return candidate, candidate_d_neighbours

    def qubit_with_most_d_interactions(self, d: int):
        """
        Finds the qubit with the most interactions from the set of free qubits.

        Args:
            d (int): The number of interactions to consider.

        Returns:
            tuple: The qubit with the most interactions and its d most-interacting neighbors.
        """
        return self.qubit_with_most_d_interactions_from_set(d, self.free_qubits)
    
    def map_qubit(self, q: int):
        """
        Marks a qubit as mapped, removing it from the set of free qubits.

        Args:
            q (int): The qubit to map (mark as occupied).
        """
        if q not in self.n:  # Ensure the qubit index is valid
            return
        self.free_qubits.discard(q)  # Remove the qubit from the set of free qubits