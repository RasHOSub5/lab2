from utils.logger import Logger, Level
import heapq
from .path import Path
from collections import deque

class Graph:
    """
    Represents a weighted, undirected graph of airport nodes using an adjacency matrix.
    
    The graph supports various graph algorithms including Dijkstra's shortest path,
    BFS, and DFS. The graph is undirected, meaning edges are bidirectional.
    
    Attributes:
        nodes (list): List of Node objects representing airports
        node_to_index (dict): Maps Node objects to their matrix indices
        code_to_node (dict): Maps IATA codes to Node objects
        n (int): Number of nodes in the graph
        matrix (list): 2D adjacency matrix storing edge weights (distances)
    """
    _graph_logger = Logger("Graph")
    _graph_logger.disable_all()

    def __init__(self, nodes):
        """
        Initialize the graph with a list of nodes.
        
        Args:
            nodes (list): List of Node objects to include in the graph
        """
        self.nodes = nodes # List of Node objects
        # efficient matrix access O(1)
        self.node_to_index = {node: idx for idx, node in enumerate(nodes)}
        self.code_to_node = {node.code: node for node in nodes}
        self.n = len(nodes)
        self.matrix = [[0] * self.n for _ in range(self.n)]

    def has_edge(self, node1, node2):
        i = self.node_to_index[node1]
        j = self.node_to_index[node2]
        return self.matrix[i][j] != 0

    def add_edge(self, node1, node2, weight):
        if not self.has_edge(node1, node2):
            i = self.node_to_index[node1]
            j = self.node_to_index[node2]
            self.matrix[i][j] = weight
            self.matrix[j][i] = weight
            return True

        Graph._graph_logger.error(f"Edge already exists between {node1} and {node2}")
        return False

    def get_weight(self, node1, node2):
        i = self.node_to_index[node1]
        j = self.node_to_index[node2]
        return self.matrix[i][j]
    
    def get_node_by_code(self, code):
        return self.code_to_node.get(code)

    def print_matrix(self):
        for row in self.matrix:
            print(row)

    def get_node_degree(self, node):
        index = self.node_to_index[node]
        return sum(1 for weight in self.matrix[index] if weight != 0)

    def get_nodes_degrees_sorted(self):
        nodes_degrees = []
        for node in self.nodes:
            degree = self.get_node_degree(node)
            nodes_degrees.append(degree)
        return sorted(nodes_degrees, reverse=True)

    def dijkstra(self, start_code, end_code=None):
        """
        Find the shortest path from a start node to an optional end node using Dijkstra's algorithm.
        
        Args:
            start_code (str): IATA code of the starting airport
            end_code (str, optional): IATA code of the destination airport. 
                                    If None, returns shortest paths to all reachable nodes.
                                    
        Returns:
            Path or list: If end_code is provided, returns a Path object containing the shortest path.
                        Otherwise, returns a list of Path objects for all reachable nodes.
        """
        start_node = self.get_node_by_code(start_code)
        end_node = self.get_node_by_code(end_code) if end_code else None

        if not start_node:
            Graph._graph_logger.error(f"Start node with code {start_code} not found.")
            return None

        start_idx = self.node_to_index[start_node]
        end_idx = self.node_to_index[end_node] if end_node else None

        distances = [float('inf')] * self.n
        previous = [None] * self.n
        visited = [False] * self.n

        distances[start_idx] = 0
        queue = [(0, start_idx)]

        while queue:
            current_distance, current_idx = heapq.heappop(queue)

            if visited[current_idx]:
                continue

            visited[current_idx] = True

            if end_idx is not None and current_idx == end_idx:
                break

            for neighbor_idx in range(self.n):
                weight = self.matrix[current_idx][neighbor_idx]

                if weight != 0 and not visited[neighbor_idx]:
                    distance = current_distance + weight

                    if distance < distances[neighbor_idx]:
                        distances[neighbor_idx] = distance
                        previous[neighbor_idx] = current_idx
                        heapq.heappush(queue, (distance, neighbor_idx))

        if end_idx is not None:
            path_indices = self._reconstruct_path_indices(previous, start_idx, end_idx)
            if path_indices:
                path_nodes = [self.nodes[idx] for idx in path_indices]
                #return distances[end_idx], path_nodes
                return Path(start_node, end_node, distances[end_idx], path_nodes)
            else:
                #return float('inf'), []
                return Path(start_node, end_node, float('inf'), []) 
        else:
            node_distances = []
            for idx, node in enumerate(self.nodes):
                path_indices = self._reconstruct_path_indices(previous, start_idx, idx)
                if path_indices:
                    path_nodes = [self.nodes[idx] for idx in path_indices]
                else:
                    path_nodes = []
                node_distances.append(Path(start_node, node, distances[idx], path_nodes)) #= (distances[idx], path_nodes)
            return node_distances
    
    def _reconstruct_path_indices(self, previous, start_idx, end_idx):
        path = []
        current_idx = end_idx

        # Reconstruct the path by following previous nodes
        # Add a safety check to prevent infinite loops
        max_iterations = len(previous)  # Should never need more steps than total nodes
        iterations = 0
        
        while current_idx is not None and current_idx != start_idx and iterations < max_iterations:
            path.append(current_idx)
            current_idx = previous[current_idx]
            iterations += 1
        
        # Add the start node if we found a valid path
        if current_idx == start_idx and iterations < max_iterations:
            path.append(start_idx)
            path.reverse()
            return path
        
        return None
    
    def get_longest_paths(self, start_code, top=10):
        """
        Find the top N longest shortest paths from a given start node.
        
        Args:
            start_code (str): IATA code of the starting airport
            top (int): Number of longest paths to return (default: 10)
            
        Returns:
            list: List of Path objects sorted by distance in descending order
        """
        paths = self.dijkstra(start_code)
        if isinstance(paths, list):
            sorted_paths = sorted([path for path in paths if not path.is_unreachable()], key=lambda x: x.distance, reverse=True)
            return sorted_paths[:top]
        else:
            return

    def bfs(self, start_code, target_code=None):
        """
        Perform a breadth-first search from a start node to an optional target node.
        
        Args:
            start_code (str): IATA code of the starting airport
            target_code (str, optional): IATA code of the target airport. 
                                       If None, performs a complete BFS traversal.
                                       
        Returns:
            Path or list: If target_code is provided, returns a Path object if found.
                        Otherwise, returns the BFS traversal order.
        """
        start_node = self.get_node_by_code(start_code)
        target_node = self.get_node_by_code(target_code) if target_code else None

        if not start_node:
            Graph._graph_logger.error(f'Start node with code {start_code} not found')
            return None
        
        start_idx = self.node_to_index[start_node]
        target_idx = self.node_to_index[target_node] if target_node else None

        visited = [False] * self.n
        previous = [None] * self.n
        queue = deque([start_idx])
        visited[start_idx] = True
        traversal_order = []

        while queue:
            current_idx = queue.popleft()
            current_node = self.nodes[current_idx]
            traversal_order.append(current_node)

            if target_idx is not None and current_idx == target_idx:
                path_indices = self._reconstruct_path_indices(previous, start_idx, target_idx)
                if path_indices:
                    path_nodes = [self.nodes[idx] for idx in path_indices]
                    return Path(start_node, target_node, len(path_nodes) - 1, path_nodes)     
                else:
                    return Path(start_node, target_node, float('inf'), []) 

            for neighbor_idx in range(self.n):
                if self.matrix[current_idx][neighbor_idx] != 0 and not visited[neighbor_idx]:
                    visited[neighbor_idx] = True
                    previous[neighbor_idx] = current_idx
                    queue.append(neighbor_idx)

        if target_idx is not None:
            return Path(start_node, target_node, float('inf'), [])

        return traversal_order
    
    def dfs(self, start_code, target_code=None):
        """
        Perform a depth-first search from a start node to an optional target node.
        
        Args:
            start_code (str): IATA code of the starting airport
            target_code (str, optional): IATA code of the target airport. 
                                       If None, performs a complete DFS traversal.
                                       
        Returns:
            Path or list: If target_code is provided, returns a Path object if found.
                        Otherwise, returns the DFS traversal order.
        """
        start_node = self.get_node_by_code(start_code)
        target_node = self.get_node_by_code(target_code) if target_code else None

        if not start_node:
            Graph._graph_logger.error(f'Start node with code {start_code} not found')
            return None
        
        start_idx = self.node_to_index[start_node]
        target_idx = self.node_to_index[target_node] if target_node else None

        visited = [False] * self.n
        previous = [None] * self.n
        stack = [start_idx]
        traversal_order = []

        while stack:
            current_idx = stack.pop()

            if not visited[current_idx]:
                visited[current_idx] = True
                current_node = self.nodes[current_idx]
                traversal_order.append(current_node)

                if target_idx is not None and current_idx == target_idx:
                    path_indices = self._reconstruct_path_indices(previous, start_idx, target_idx)

                    if path_indices:
                        path_nodes = [self.nodes[idx] for idx in path_indices]
                        return Path(start_node, target_node, len(path_nodes) - 1, path_nodes)
                    else:
                        return Path(start_node, target_node, float('inf'), [])
                    
                for neighbor_idx in range(self.n - 1, -1, -1):
                    if self.matrix[current_idx][neighbor_idx] != 0 and not visited[neighbor_idx]:
                        previous[neighbor_idx] = current_idx
                        stack.append(neighbor_idx)

        if target_idx is not None:
            return Path(start_node, target_node, float('inf'), [])
        
        return traversal_order

    def is_connected(self):
        if self.n == 0:
            return True
        
        traversal_result = self.bfs(self.nodes[0].code)

        if isinstance(traversal_result, list):
            visited_count = len(traversal_result)
            return visited_count == self.n
        else:
            return False

    def get_nodes_from_connected_components(self):
        visited_codes = set()
        components = []

        for node in self.nodes:
            if node.code not in visited_codes:
                component_nodes = self.bfs(node.code)

                if isinstance(component_nodes, list):
                    component_codes = [n.code for n in component_nodes]
                    components.append(component_nodes)
                    visited_codes.update(component_codes)

        return components
    
    def get_connected_subgraphs(self):
        if self.is_connected():
            return [self]
        
        components = self.get_nodes_from_connected_components()
        subgraphs = []

        for component_nodes in components:
            subgraph = Graph(component_nodes)

            for i, node1 in enumerate(component_nodes):
                orig_idx1 = self.node_to_index[node1]
                for j, node2 in enumerate(component_nodes):
                    if i != j:
                        orig_idx2 = self.node_to_index[node2]
                        weight = self.matrix[orig_idx1][orig_idx2]

                        if weight != 0:
                            subgraph.add_edge(node1, node2, weight)

            subgraphs.append(subgraph)

        return subgraphs

    def get_component_count(self):
        if self.is_connected():
            return 1
        else:
            components = self.get_nodes_from_connected_components()
            return len(components)
        
    def get_minimum_spanning_tree(self):
        if self.n == 0:
            return Graph([])
        
        visited = [False] * self.n
        min_edges = [None] * self.n
        min_edges[0] = (0, -1)

        heap = []
        heapq.heappush(heap, (0, 0, -1))

        mst_edges = []

        while heap:
            weight, current_idx, parent_idx = heapq.heappop(heap)

            if visited[current_idx]:
                continue

            visited[current_idx] = True

            if parent_idx != -1:
                mst_edges.append((
                    self.nodes[parent_idx],
                    self.nodes[current_idx],
                    weight
                ))

            for neighbor_idx in range(self.n):
                edge_weight = self.matrix[current_idx][neighbor_idx]

                if (edge_weight != 0 and not visited[neighbor_idx] and (min_edges[neighbor_idx] is None or edge_weight < min_edges[neighbor_idx][0])):
                    min_edges[neighbor_idx] = (edge_weight, current_idx)
                    heapq.heappush(heap, (edge_weight, neighbor_idx, current_idx))

        mst = Graph(self.nodes[:])

        for node1, node2, weight in mst_edges:
            mst.add_edge(node1, node2, weight)

        return mst
    
    def get_mst_total_weight(self):
        if self.n == 0:
            return 0
        
        visited = [False] * self.n
        heap = []
        heapq.heappush(heap, (0, 0))
        total_weight = 0
        nodes_in_mst = 0

        while heap and nodes_in_mst < self.n:
            weight, current_idx = heapq.heappop(heap)

            if visited[current_idx]:
                continue

            visited[current_idx] = True
            total_weight += weight
            nodes_in_mst += 1

            for neighbor_idx in range(self.n):
                edge_weight = self.matrix[current_idx][neighbor_idx]

                if edge_weight != 0 and not visited[neighbor_idx]:
                    heapq.heappush(heap, (edge_weight, neighbor_idx))

        return total_weight