"""
CSV Manager module for handling CSV file operations.

This module provides the CSVManager class which handles reading, parsing,
and processing CSV files containing airport and route data.
"""

import csv

class CSVManager:
    """
    A class to manage CSV file operations for airport and route data.
    
    This class provides methods to:
    - Read and parse CSV files
    - Create Node objects from CSV data
    - Generate graph edges from route information
    - Access and manipulate CSV data programmatically
    
    Attributes:
        file_path (str): Path to the CSV file
        delimiter (str): Delimiter used in the CSV file (default: ',')
        encoding (str): File encoding (default: 'utf-8')
        headers (list): List of column headers from the CSV
        data (list): List of rows containing the CSV data
    """

    def __init__(self, file_path, delimiter=',', encoding='utf-8'):
        """Initialize the CSVManager with file path and configuration.
        
        Args:
            file_path (str): Path to the CSV file to be managed
            delimiter (str, optional): Delimiter used in the CSV file. Defaults to ','.
            encoding (str, optional): File encoding. Defaults to 'utf-8'.
        """
        self.file_path = file_path
        self.delimiter = delimiter
        self.encoding = encoding
        self.headers = []  # Will store column headers
        self.data = []     # Will store the actual CSV data

    def read_csv(self):
        """Read and parse the CSV file into memory.
        
        Reads the CSV file specified in file_path and stores the headers and data
        in the instance variables. Handles file operations and common errors.
        
        Raises:
            FileNotFoundError: If the specified file doesn't exist
            Exception: For any other file reading or parsing errors
        """
        try:
            with open(self.file_path, mode='r', encoding=self.encoding) as file:
                csv_reader = csv.reader(file, delimiter=self.delimiter)
                self.headers = next(csv_reader)  # Read and store column headers
                self.data = [row for row in csv_reader]  # Store remaining rows
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.file_path}")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}")
        
    def get_row_count(self):
        return len(self.data)
        
    def get_headers(self):
        return self.headers
    
    def get_data(self):
        return self.data
    
    def get_row(self, index):
        try:
            return self.data[index]
        except IndexError:
            raise IndexError(f"Row index {index} out of range")
        
    def get_column(self, column_name):
        try:
            col_index = self.headers.index(column_name)
            return [row[col_index] for row in self.data]
        except ValueError:
            raise ValueError(f"Column '{column_name}' not found in headers")

    def get_value(self, row_index, column_name):
        try:
            col_index = self.headers.index(column_name)
            return self.data[row_index][col_index]
        except IndexError:
            raise IndexError(f"Row index {row_index} out of range")
        except ValueError:
            raise ValueError(f"Column '{column_name}' not found in headers")
        
    def __str__(self):
        return f"CSV file: {self.file_path}\nRows: {self.get_row_count()}\nHeaders: {self.headers}"
    
    def get_unique_codes(self):
        unique_codes = set()
        for row in self.data:
            code = row[self.headers.index('Source Airport Code')]
            unique_codes.add(code)

        for row in self.data:
            code = row[self.headers.index('Destination Airport Code')]
            unique_codes.add(code)

        return unique_codes

    def create_objects(self, object_class):
        """Create Node objects from the CSV data.
        
        Processes the CSV data to create unique Node objects for each airport.
        Handles both source and destination airports, ensuring no duplicates.
        
        Args:
            object_class (class): The class to use for creating objects (typically Node)
            
        Returns:
            list: List of created Node objects
            
        Note:
            This method processes approximately 3,256 unique airport nodes
        """
        unique_codes = self.get_unique_codes()
        objects = []
        
        # Process source airports
        for index, row in enumerate(self.data):
            code = self.get_value(index, 'Source Airport Code')

            if code in unique_codes:
                # Extract airport details
                name = self.get_value(index, 'Source Airport Name')
                city = self.get_value(index, 'Source Airport City')
                country = self.get_value(index, 'Source Airport Country')
                latitude = self.get_value(index, 'Source Airport Latitude')
                longitude = self.get_value(index, 'Source Airport Longitude')

                # Create and store new node
                obj = object_class(code, name, city, country, 
                                 float(latitude), float(longitude))
                objects.append(obj)
                unique_codes.remove(code)

        # Process destination airports
        for index, row in enumerate(self.data):
            code = self.get_value(index, 'Destination Airport Code')

            if code in unique_codes:
                # Extract airport details
                name = self.get_value(index, 'Destination Airport Name')
                city = self.get_value(index, 'Destination Airport City')
                country = self.get_value(index, 'Destination Airport Country')
                latitude = self.get_value(index, 'Destination Airport Latitude')
                longitude = self.get_value(index, 'Destination Airport Longitude')

                # Create and store new node
                obj = object_class(code, name, city, country, 
                                 float(latitude), float(longitude))
                objects.append(obj)
                unique_codes.remove(code)

        return objects

    def create_edges(self, graph):
        """Create edges in the graph based on flight routes from CSV data.
        
        Processes each row in the CSV to create directed edges between
        source and destination airports, with distances calculated using
        the haversine formula.
        
        Args:
            graph (Graph): The graph instance to add edges to
            
        Note:
            - Creates directed edges from source to destination airports
            - Edge weights represent distances in kilometers using haversine formula
        """
        for index, row in enumerate(self.data):
            # Get source and destination nodes
            source_code = self.get_value(index, 'Source Airport Code')
            dest_code = self.get_value(index, 'Destination Airport Code')
            
            source_node = graph.get_node_by_code(source_code)
            destination_node = graph.get_node_by_code(dest_code)
            
            # Add edge with distance as weight
            if source_node and destination_node:  # Ensure both nodes exist
                distance = source_node.haversine(destination_node)
                graph.add_edge(source_node, destination_node, distance)