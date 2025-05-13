from mapper.base.Mapper import Mapper
from router.Router import Router
import networkx as nx

import logging
logger = logging.getLogger(__name__)

class MapperUpdater:
    def __init__(self, topology: nx.Graph, mapper : Mapper, cnots_list : list, lookahead : int):
        logger.info("Init mapper updater")
        logger.info("Initial logical to physical mapping: %s", mapper.l_to_p)
        logger.info("Initial physical to logical mapping: %s", mapper.p_to_l)
        logger.info("The following set of cnots will be used to update the mapping: %s", cnots_list)

        self.router = Router(topology, mapper, cnots_list, lookahead)
        self.initial_mapper = mapper
        self.topology = topology 
        self.cnots_list = cnots_list

    def update_mapping(self):
        # routes self.cnots_list using self.mapper initial map
        # Checks swap count and remembers final mapping
        # Creates a new router that uses a new map
        # routes again 
        # Checks if the swaps count has decreased

        swaps_count, _= self.router.route_circuit()
        
        logger.info("Routing with initial mapping completed, obtained %d swaps", swaps_count)
        logger.info("Logical to physical mapping after the routing: %s", self.router.l_to_p)
        logger.info("Physical to logical mapping after the routing: %s", self.router.p_to_l)
        logger.info("Using such mappings as initial mappings for a new routing step")

        new_mapper = Mapper.from_static_mapping(self.topology, self.cnots_list, self.topology.number_of_nodes(), self.router.l_to_p, self.router.p_to_l)
        new_router = Router(self.topology, new_mapper, self.cnots_list, self.router.lookahead)
        
        new_swaps_count, _ = new_router.route_circuit()

        logger.info("Second round of mapping completed, completed with %d swaps", new_swaps_count)

        if new_swaps_count < swaps_count:
            logger.info("The final mapping of the first routing round induces a better routing. Returning such new mapping.")
            return new_mapper
        else:
            logger.info("The second round of routing did not improve performances. Keeping the mapping as it is")
            return self.initial_mapper