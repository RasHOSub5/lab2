class Path:
    """
    Represents a path between two nodes in the airport network.
    
    Attributes:
        start_node (Node): Starting node of the path
        end_node (Node): Destination node of the path
        distance (float): Total distance of the path in meters
        nodes (list): Ordered list of nodes that form the path
    """

    def __init__(self, start_node, end_node, distance, nodes):
        """
        Initialize a new Path object.
        
        Args:
            start_node (Node): Starting node of the path
            end_node (Node): Destination node of the path
            distance (float): Total distance of the path in meters
            nodes (list): Ordered list of nodes from start to end
        """
        self.start_node = start_node
        self.end_node = end_node
        self.distance = distance
        self.nodes = nodes

    def __repr__(self):
        path_str = ' -> '.join(str(node) for node in self.nodes)
        if self.is_unreachable():
            return f'Unreacheable node: Not path from {self.start_node} to {self.end_node}'
        else:
            return f"From {self.start_node} to {self.end_node}: {self.distance}, Path: {path_str}"
        
    def is_unreachable(self):
        """
        Check if the destination node is unreachable from the start node.
        
        Returns:
            bool: True if the destination is unreachable, False otherwise
        """
        return self.distance == float('inf')