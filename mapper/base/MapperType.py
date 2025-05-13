from enum import Enum
import networkx as nx
from mapper.base.Mapper import Mapper
from ..random.RandomMapper import RandomMapper
from ..majority.MajorityMapper import MajorityMapper
from ..max_interacting_pairs.MaxInteractingPairsMapping import MaxInteractingPairsMapping

import logging
logger = logging.getLogger(__name__)

class MapperType(Enum):
    """
    Enumeration of different qubit mapping strategies.

    Each member represents a strategy for mapping logical qubits to physical qubits.
    These strategies define how to initialize the mapping in accordance with a connectivity graph.
    """

    BASIC = "BASIC MAPPER"
    RANDOM = "RANDOM MAPPER"
    MAJORITY = "MAJORITY MAPPER"
    MAX_PAIRS = "MAX PAIRS MAPPER"

    @staticmethod
    def __type_from_string(strategy_name: str):
        """
        Internal helper method that maps a string to a corresponding MapperType enum.

        Args:
            strategy_name (str): Name of the strategy (e.g., 'random', 'majority').

        Returns:
            MapperType: Enum value corresponding to the given strategy name.
        """
        match strategy_name.lower():
            case "random":
                return MapperType.RANDOM
            case "majority":
                return MapperType.MAJORITY
            case "max_pairs":
                return MapperType.MAX_PAIRS
            case _:
                return MapperType.BASIC 

    @staticmethod
    def mapper_from_string(strategy_name: str, connectivity: nx.Graph, cnots_list: list, qubits: int):
        """
        Returns an instance of the appropriate Mapper subclass based on the given strategy name.

        Args:
            strategy_name (str): Strategy name as string ('basic', 'random', 'majority', 'max_pairs').
            connectivity (nx.Graph): Graph representing the physical connectivity of the qubits.
            cnots_list (list): List of CNOT operations in the circuit.
            qubits (int): Total number of qubits in the circuit.

        Returns:
            Mapper: An instance of a subclass of Mapper implementing the desired strategy.
        """
        logger.info("Getting mapper for strategy %s", strategy_name)
        type = MapperType.__type_from_string(strategy_name.lower())

        match type:
            case MapperType.BASIC:
                return Mapper(connectivity, cnots_list, qubits)
            case MapperType.RANDOM:
                return RandomMapper(connectivity, cnots_list, qubits)
            case MapperType.MAJORITY:
                return MajorityMapper(connectivity, cnots_list, qubits)
            case MapperType.MAX_PAIRS:
                return MaxInteractingPairsMapping(connectivity, cnots_list, qubits)
            case _:
                return Mapper(connectivity, cnots_list, qubits)