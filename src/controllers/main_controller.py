"""
MainController module for managing the core application logic.

This module contains the MainController class which serves as the central coordinator
for loading airport data, creating the graph structure, and managing the application state.
"""

from models import Graph, Node
from utils.csv_manager import CSVManager

class MainController:
    """
    Main controller class that manages the application's core functionality.
    
    This class is responsible for:
    - Loading and parsing airport data from CSV files
    - Creating and managing the graph structure of airports and routes
    - Coordinating between data loading and visualization components
    
    Attributes:
        csv_manager (CSVManager): Handles CSV file operations and data parsing
        graph (Graph): The graph representation of airports and flight routes
    """
    def __init__(self):
        """Initialize the MainController with default values.
        
        Initializes the controller with empty CSV manager and graph instances.
        These will be populated when data is loaded.
        """
        self.csv_manager = None  # Will hold CSVManager instance after data loading
        self.graph = None        # Will hold Graph instance after data processing

    def load_airport_data(self, csv_file):
        """Load and process airport data from a CSV file.
        
        This method performs the following steps:
        1. Initializes a loading animation for user feedback
        2. Reads and parses the CSV file
        3. Creates Node objects for each airport
        4. Builds a graph with the nodes and their connections
        5. Returns the processed data
        
        Args:
            csv_file (str): Path to the CSV file containing airport and route data
            
        Returns:
            tuple: A tuple containing (csv_manager, graph) instances
            
        Raises:
            FileNotFoundError: If the specified CSV file doesn't exist
            Exception: For any other errors during data loading or processing
        """
        from utils.loading_animation import LoadingAnimation
        
        # Initialize and start loading animation
        loader = LoadingAnimation("Loading airport data")
        loader.start()
        
        try:
            # Step 1: Initialize CSV manager and read the file
            self.csv_manager = CSVManager(csv_file)
            self.csv_manager.read_csv()
            
            # Update loading status
            loader.message = f"Loaded {self.csv_manager.get_row_count()} rows"
            
            # Step 2: Create Node objects for each airport
            loader.message = "Creating airport nodes"
            nodes = self.csv_manager.create_objects(Node)
            
            # Step 3: Initialize graph with nodes
            loader.message = "Initializing graph"
            self.graph = Graph(nodes)
            
            # Step 4: Create edges between connected airports
            loader.message = "Creating flight routes"
            self.csv_manager.create_edges(self.graph)
            
            # Calculate and display edge count for user feedback
            edge_count = sum(1 for i in range(self.graph.n) 
                           for j in range(i+1, self.graph.n) 
                           if self.graph.matrix[i][j] != 0)
            
            loader.message = f"Created graph with {self.graph.n} airports and {edge_count} routes"
            return self.csv_manager, self.graph
            
        except FileNotFoundError as e:
            loader.stop(False)
            raise FileNotFoundError(f"Airport data file not found: {csv_file}") from e
        except Exception as e:
            loader.stop(False)
            raise Exception(f"Error loading airport data: {str(e)}") from e
        finally:
            # Ensure loading animation is always stopped, even if an error occurs
            loader.stop(True)
