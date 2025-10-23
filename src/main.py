"""
Main Application Module

This module serves as the entry point for the Flight Route Finder application.
It provides both a command-line interface and a web interface for visualizing
airport networks and finding shortest paths between airports.

Features:
- Interactive console interface for path finding
- Web-based visualization using Folium/Leaflet
- Airport network analysis and visualization

Dependencies:
- Flask: Web framework
- folium: Interactive map visualization
- folium.plugins.MarkerCluster: For handling large numbers of markers
"""

from flask import Flask, g
import folium
from folium.plugins import MarkerCluster

# Local imports
from models import Graph, Node
from utils.csv_manager import CSVManager
from controllers.main_controller import MainController
from views.gui_console import GUIConsole

# Initialize Flask application
app = Flask(__name__)

# Global variables to store data for Flask
csv_manager_global = None  # Will hold the CSV manager instance
graph_global = None       # Will hold the graph instance

def main():
    """
    Main function that initializes and runs the application.
    
    This function:
    1. Initializes the main controller
    2. Loads airport data from CSV
    3. Starts the appropriate interface based on configuration
    """
    try:
        # Initialize controller
        controller = MainController()
        
        # Load data with progress feedback
        print("Loading airport data...")
        global csv_manager_global, graph_global
        
        # Load data using the controller
        file_path = 'C:/Users/athen/Desktop/Workspace/PythonProjects/lab2/src/data/flights_final.csv'
        csv_manager_global, graph_global = controller.load_airport_data(file_path)
        
        # Calculate and display statistics
        edge_count = sum(1 for i in range(graph_global.n) 
                        for j in range(i+1, graph_global.n) 
                        if graph_global.matrix[i][j] != 0)
        print(f"Successfully loaded data: {graph_global.n} airports and {edge_count} routes")
        
        # Start the GUI console with loading animation
        print("\nInitializing map viewer...")
        from utils.loading_animation import LoadingAnimation
        loader = LoadingAnimation("Preparing map interface")
        loader.start()
        
        try:
            # Initialize and start the GUI console
            console = GUIConsole(graph_global)
            loader.stop(True)
            print("Map viewer ready!")
            
            # Start the main event loop
            console.mainloop()
            
        except Exception as e:
            loader.stop(False)
            print(f"Error initializing GUI: {e}")
            raise
            
    except FileNotFoundError as e:
        print(f"Error: Required data file not found. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

def get_minimum_path_from_to(graph: Graph):
    """
    Find and display the shortest path between two airports.
    
    This function provides a command-line interface for finding the shortest path
    between two airports using their IATA codes.
    
    Args:
        graph (Graph): The graph containing airport and route data
    """
    try:
        # Get user input for start and end airports
        start_code = input('Enter start airport code (e.g., JFK): ').strip().upper()
        end_code = input('Enter destination airport code (e.g., LAX): ').strip().upper()
        
        # Find the shortest path using Dijkstra's algorithm
        path = graph.dijkstra(start_code, end_code)
        
        # Display the results
        print(f'\nRoute from {path.start_node.code} to {path.end_node.code}:')
        print(f'Total distance: {path.distance:,.0f} meters')
        print('\nPath details:')
        for node in path.nodes:
            print(f' - {node.get_info()}')
            
    except KeyError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

@app.before_request
def before_request():
    """
    Flask before_request handler.
    
    Makes the CSV manager and graph available to all routes.
    These are stored in Flask's application context (g).
    """
    g.csv_manager = csv_manager_global
    g.graph = graph_global

@app.route('/')
def home():
    """
    Main route for the web interface.
    
    Renders an interactive map showing all airports with markers.
    Markers are color-coded based on the number of connections (degree).
    
    Returns:
        str: HTML content for the web page
    """
    # Check if data is loaded
    if g.graph is None:
        return "<h1>Data not loaded</h1><p>Please run the console interface first.</p>"
    
    try:
        # Create a map centered on New York (default)
        map = folium.Map(
            location=[40.7128, -74.0060],  # Default to New York
            zoom_start=4,
            width='100%',
            height='100%',
            tiles='OpenStreetMap'  # Use OpenStreetMap as the base layer
        )
        
        # Add marker cluster for better performance with many markers
        marker_cluster = MarkerCluster().add_to(map)

        # Add each airport as a marker
        for node in g.graph.nodes:
            # Determine marker color based on node degree (number of connections)
            degree = g.graph.get_node_degree(node)
            if degree > 20:
                color = 'red'     # Major hub
            elif degree > 10:
                color = 'orange'  # Medium hub
            elif degree > 5:
                color = 'green'   # Small hub
            else:
                color = 'blue'    # Regional airport

            # Create HTML content for the popup
            html = f'''
            <div style="text-align: center;">
                <h3>{node.get_info()}</h3>
                <p>Connections: {degree}</p>
                <button onclick="alert('You selected {node.name}!')"
                        style="background: #4CAF50; color: white; 
                               padding: 8px 16px; border: none; 
                               border-radius: 4px; cursor: pointer;">
                    View Details
                </button>
            </div>
            '''

            # Add marker to the map
            folium.Marker(
                [node.latitude, node.longitude],
                popup=folium.Popup(html, max_width=300),
                tooltip=f"{node.name} ({node.code})",
                icon=folium.Icon(color=color, icon='plane', prefix='fa')
            ).add_to(marker_cluster)

        # Generate the HTML for the map
        map_html = map.get_root().render()

        # Return the complete HTML page
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Flight Route Finder</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
            <style>
                body {{ margin: 0; padding: 0; }}
                .header {{ 
                    background: #2c3e50; 
                    color: white; 
                    padding: 1rem; 
                    text-align: center;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .container {{ 
                    width: 100%; 
                    height: calc(100vh - 80px); 
                }}
                .legend {{
                    position: absolute;
                    bottom: 30px;
                    right: 10px;
                    z-index: 1000;
                    background: white;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.2);
                }}
                .legend-item {{
                    margin: 5px 0;
                    display: flex;
                    align-items: center;
                }}
                .legend-color {{
                    width: 20px;
                    height: 20px;
                    margin-right: 8px;
                    border-radius: 50%;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌍 Flight Route Finder</h1>
                <p>Explore airports and their connections</p>
            </div>
            <div class="container">
                {map_html}
                <div class="legend">
                    <h4>Airport Size</h4>
                    <div class="legend-item">
                        <div class="legend-color" style="background: red;"></div>
                        <span>Major Hub (20+ connections)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: orange;"></div>
                        <span>Medium Hub (11-20 connections)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: green;"></div>
                        <span>Small Hub (6-10 connections)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: blue;"></div>
                        <span>Regional (1-5 connections)</span>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''
        
    except Exception as e:
        return f"<h1>Error</h1><p>An error occurred: {str(e)}</p>"

if __name__ == "__main__":
    """
    Entry point for the application.
    
    By default, this runs the console interface. To run the web interface instead,
    uncomment the app.run() line and comment out the main() call.
    """
    # Run console interface (default)
    main()
    
    # To run the web interface instead, uncomment the following line
    # and comment out the main() call above:
    # app.run(host='0.0.0.0', port=5000, debug=True)