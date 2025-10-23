import folium
from folium.plugins import MarkerCluster
import webbrowser
import tempfile
import os

# Local imports
from models import Graph, Node

class GUIConsole:
    # ANSI color codes
    COLORS = {
        # Reset and styles
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'underline': '\033[4m',
        'blink': '\033[5m',
        'reverse': '\033[7m',
        'hidden': '\033[8m',
        
        # Regular colors
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        
        # Bright colors
        'bright_black': '\033[90m',
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m',
        'bright_white': '\033[97m',
        
        # Background colors
        'bg_black': '\033[40m',
        'bg_red': '\033[41m',
        'bg_green': '\033[42m',
        'bg_yellow': '\033[43m',
        'bg_blue': '\033[44m',
        'bg_magenta': '\033[45m',
        'bg_cyan': '\033[46m',
        'bg_white': '\033[47m',
        
        # Bright background colors
        'bg_bright_black': '\033[100m',
        'bg_bright_red': '\033[101m',
        'bg_bright_green': '\033[102m',
        'bg_bright_yellow': '\033[103m',
        'bg_bright_blue': '\033[104m',
        'bg_bright_magenta': '\033[105m',
        'bg_bright_cyan': '\033[106m',
        'bg_bright_white': '\033[107m',
        
        # Custom combinations
        'highlight': '\033[38;5;231;48;5;33m',  # White on blue
        'success': '\033[38;5;40m',             # Bright green
        'warning': '\033[38;5;208m',            # Orange
        'error': '\033[38;5;196m',              # Bright red
        'info': '\033[38;5;45m',                # Bright cyan
        'menu_item': '\033[38;5;39m',           # Bright blue
        'menu_number': '\033[38;5;214m',        # Orange-yellow
        'header': '\033[38;5;45;1m',            # Bright cyan, bold
        'subheader': '\033[38;5;39m',           # Bright blue
        'dim_text': '\033[38;5;245m'            # Light gray
    }
    
    def __init__(self, graph):
        self.graph = graph
        self.current_airport = None
    
    def _color_text(self, text, color):
        """Helper method to color text"""
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"
    
    def mainloop(self):
        """Main console interface loop"""
        title = self._color_text("AIRPORT NETWORK ANALYSIS SYSTEM", "bright_blue")
        print("=" * 60)
        print(f"      {title}")
        print("=" * 60)
        loaded_text = self._color_text(f"Loaded: {self.graph.n} airports", "bright_green")
        print(loaded_text)
        
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (0-6): ").strip()
            
            if choice == '1':
                self.analyze_connectivity()
            elif choice == '2':
                self.analyze_mst()
            elif choice == '3':
                self.analyze_airport_info()
            elif choice == '4':
                self.analyze_longest_paths()
            elif choice == '5':
                self.find_shortest_path()
            elif choice == '6':
                self.show_folium_map()
            elif choice == '0':
                print(self._color_text("\nThank you for using the Airport Network Analysis System!", "success"))
                print(self._color_text("Goodbye! ✈️\n", "info"))
                break
            else:
                print(self._color_text("\n❌ Invalid choice. Please enter a number between 0 and 6.", "error"))
                input("\nPress Enter to continue...")
                continue
            
            input("\nPress Enter to continue...")
    
    def display_menu(self):
        """Display the main menu with improved formatting and colors"""
        # Clear screen for better visibility
        print("\033[H\033[J", end="")  # ANSI escape code to clear screen
        
        # Header with gradient effect
        print("\n" + self._color_text("╔" + "═" * 50 + "╗", "header"))
        print(self._color_text(f"║{'✈️  AIRPORT NETWORK ANALYSIS  ✈️':^50}  ║", "header"))
        print(self._color_text("╚" + "═" * 50 + "╝", "header"))
        
        # Menu options
        print("\n" + self._color_text("MAIN MENU", "subheader") + self._color_text(" " * 35 + "◈", "dim_text"))
        print(self._color_text("─" * 50, "dim_text"))
        
        # Menu items with consistent styling
        menu_items = [
            ("1", "Graph Connectivity"),
            ("2", "Minimum Spanning Tree"),
            ("3", "Airport Details"),
            ("4", "Longest Paths"),
            ("5", "Find Shortest Path"),
            ("6", "View Interactive Map")
        ]
        
        for num, text in menu_items:
            print(f"{self._color_text(num, 'menu_number')}. {self._color_text(text, 'menu_item')}")
        
        # Exit option in different style
        print(f"\n{self._color_text('0', 'error')}. {self._color_text('Exit', 'error')}")
        
        # Current airport info if set
        if self.current_airport:
            print("\n" + self._color_text("✈ CURRENT AIRPORT", "info") + 
                  f"\n{self._color_text('─' * 50, 'dim_text')}")
            print(f"  {self._color_text(self.current_airport.code, 'highlight')} - "
                  f"{self._color_text(self.current_airport.name, 'bright_white')}")
            print(f"  {self._color_text(f'{self.current_airport.city}, {self.current_airport.country}', 'dim_text')}")
        
        # System info
        print("\n" + self._color_text("ℹ ", "info") + 
              self._color_text(f"Loaded: {self.graph.n} airports", "dim_text"))
        
        # Footer
        print("\n" + self._color_text("─" * 50, "dim_text"))
    
    def show_folium_map(self):
        """Display map view options with simplified interface"""
        from utils.loading_animation import LoadingAnimation
        
        # Display header with map emoji
        print("\n" + self._color_text("╔" + "═" * 50 + "╗", "header"))
        print(self._color_text(f"║{'🗺️  INTERACTIVE AIRPORT MAP  🗺️':^50}  ║", "header"))
        print(self._color_text("╚" + "═" * 50 + "╝", "header"))
        
        while True:
            # Display options
            print("\n" + self._color_text("MAP VIEW OPTIONS", "bright_cyan"))
            print(self._color_text("─" * 50, "bright_cyan"))
            print(f"{self._color_text('1', 'bright_yellow')}. Basic Airport View")
            print(f"{self._color_text('2', 'bright_yellow')}. View All Flight Routes")
            print(f"{self._color_text('3', 'bright_yellow')}. Routes from Specific Airport")
            print(f"{self._color_text('4', 'bright_red')}. Return to Main Menu")
            
            choice = input("\n" + self._color_text("Enter your choice (1-4): ", "bright_white")).strip()
            
            if choice in ['1', '2', '3', '4']:
                break
                
            print(self._color_text("\nInvalid choice. Please enter a number between 1 and 4.", "bright_red"))
            
        if choice == '4':
            return  # Return to main menu
            
        # Start loading animation (purely visual feedback)
        loader = LoadingAnimation("Preparing map...")
        loader.start()
        
        try:
            # Calculate center of the map based on average coordinates
            loader.message = "Calculating map center"
            if self.graph.nodes:
                avg_lat = sum(node.latitude for node in self.graph.nodes) / len(self.graph.nodes)
                avg_lon = sum(node.longitude for node in self.graph.nodes) / len(self.graph.nodes)
            else:
                avg_lat, avg_lon = 40.7128, -74.0060  # Default to New York
            
            # Create the map
            loader.message = "Creating map"
            m = folium.Map(
                location=[avg_lat, avg_lon],
                zoom_start=3,
                tiles='OpenStreetMap'
            )
            
            # Create separate feature groups for better layer control
            routes_group = folium.FeatureGroup(name="Flight Routes", show=False)
            marker_group = folium.FeatureGroup(name="Airports")
            
            # Add marker cluster to marker group for better performance
            loader.message = "Setting up marker clusters"
            marker_cluster = MarkerCluster().add_to(marker_group)
            
            # Store nodes by code for easy lookup and create index mapping
            nodes_by_code = {node.code: node for node in self.graph.nodes}
            node_to_index = {node: i for i, node in enumerate(self.graph.nodes)}
            
            # Add markers for each airport
            loader.message = "Adding airport markers"
            total_nodes = len(self.graph.nodes)
            for i, node in enumerate(self.graph.nodes, 1):
                if i % 100 == 0:  # Update progress every 100 nodes
                    loader.message = f"Adding airport markers ({i}/{total_nodes})"
                # Determine marker color based on connectivity
                degree = self.graph.get_node_degree(node)
                if degree > 20:
                    color = 'red'
                elif degree > 10:
                    color = 'orange'
                elif degree > 5:
                    color = 'green'
                else:
                    color = 'blue'
                
                # Create popup content
                popup_html = f"""
                <div style="width: 250px;">
                    <h4 style="margin: 5px 0; color: #2c3e50;">{node.name}</h4>
                    <hr style="margin: 8px 0;">
                    <p style="margin: 3px 0;"><b>Code:</b> {node.code}</p>
                    <p style="margin: 3px 0;"><b>City:</b> {node.city}</p>
                    <p style="margin: 3px 0;"><b>Country:</b> {node.country}</p>
                    <p style="margin: 3px 0;"><b>Connections:</b> {degree}</p>
                    <p style="margin: 3px 0;"><b>Coordinates:</b><br>{node.latitude:.4f}, {node.longitude:.4f}</p>
                </div>
                """
                
                folium.Marker(
                    location=[node.latitude, node.longitude],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"{node.code}: {node.name} ({degree} connections)",
                    icon=folium.Icon(color=color, icon='plane', prefix='fa')
                ).add_to(marker_cluster)
            
            # Add edges based on user choice
            edge_count = 0
            loader.message = "Preparing routes"
            
            if choice == '2':  # All routes
                edge_count = self._add_all_routes(routes_group, nodes_by_code, node_to_index, loader)
                routes_group.show = True  # Make routes visible by default
                map_title = f"Airport Network with {edge_count} Routes"
                
            elif choice == '3':  # Routes from selected airport
                loader.stop(True)
                airport_code = input(self._color_text("Enter airport code to show its routes: ", "bright_cyan")).strip().upper()
                loader.start()
                loader.message = "Preparing routes"
                
                if airport_code in nodes_by_code:
                    edge_count = self._add_routes_from_airport(routes_group, nodes_by_code, node_to_index, airport_code, loader)
                    routes_group.show = True  # Make routes visible by default
                    map_title = f"Routes from {airport_code} ({edge_count} routes)"
                else:
                    print(self._color_text(f"Airport '{airport_code}' not found. Showing basic map.", "red"))
                    map_title = "Airport Network"
            else:  # Basic map
                map_title = "Airport Network"
            
            # Add all feature groups to the map
            loader.message = "Finalizing map"
            marker_group.add_to(m)
            routes_group.add_to(m)
            
            # Add layer control to toggle routes on/off
            folium.LayerControl().add_to(m)
            
            # Add title and legend
            title_html = f'''
                <h3 align="center" style="font-size:20px"><b>🌍 {map_title}</b></h3>
                '''
            m.get_root().html.add_child(folium.Element(title_html))
            
            # Save to temporary file and open in browser
            loader.message = "Saving map"
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w') as f:
                temp_file = f.name
                m.save(temp_file)
            
            loader.message = f"Opening map with {len(self.graph.nodes)} airports"
            if routes_group.show:
                loader.message += f" and {edge_count} routes"
            
            # Open in default web browser
            webbrowser.open('file://' + os.path.abspath(temp_file))
            
            loader.stop(True)
            print(self._color_text("\nMap opened in browser!", "bright_green"))
            print(self._color_text("Note: The map file is temporary and will be deleted when you close your browser.", "bright_yellow"))
            if routes_group.show:
                print(self._color_text("Tip: Use the layer control in the top-right to toggle routes on/off", "bright_cyan"))
            
        except Exception as e:
            print(self._color_text(f"Error generating map: {str(e)}", "bright_red"))
            import traceback
            traceback.print_exc()

    def _add_all_routes(self, routes_group, nodes_by_code, node_to_index, loader=None):
        """Add all flight routes to the map"""
        if loader:
            loader.message = "Adding all routes to map"
        else:
            print(self._color_text("Adding all routes to map...", "bright_cyan"))
        
        edge_count = 0
        for i, node1 in enumerate(self.graph.nodes):
            for j, node2 in enumerate(self.graph.nodes):
                if i < j and self.graph.matrix[i][j] != 0:  # Only check upper triangle to avoid duplicates
                    distance = self.graph.matrix[i][j]
                    
                    # Create a line for the route with better visibility
                    folium.PolyLine(
                        locations=[
                            [node1.latitude, node1.longitude],
                            [node2.latitude, node2.longitude]
                        ],
                        popup=f"Route: {node1.code} ↔ {node2.code}<br>Distance: {distance:,.0f} meters ({distance/1000:,.1f} km)",
                        tooltip=f"{node1.code} ↔ {node2.code}",
                        color='#1f77b4',  # Better blue color
                        weight=2,
                        opacity=0.7,
                        dash_array='5, 5'  # Dashed line for better visibility
                    ).add_to(routes_group)
                    edge_count += 1
        
        print(self._color_text(f"\nAdded {edge_count} routes to map", "bright_green"))
        return edge_count

    def _add_routes_from_airport(self, routes_group, nodes_by_code, node_to_index, airport_code, loader=None):
        """Add routes only from a specific airport"""
        if loader:
            loader.message = f"Adding routes from {airport_code}"
        else:
            print(self._color_text(f"Adding routes from {airport_code}...", "bright_cyan"))
        
        source_node = nodes_by_code[airport_code]
        source_index = node_to_index[source_node]
        
        edge_count = 0
        for i, node in enumerate(self.graph.nodes):
            if self.graph.matrix[source_index][i] != 0 and source_index != i:
                distance = self.graph.matrix[source_index][i]
                
                # Create a line for the route
                folium.PolyLine(
                    locations=[
                        [source_node.latitude, source_node.longitude],
                        [node.latitude, node.longitude]
                    ],
                    popup=f"Route: {source_node.code} → {node.code}<br>Distance: {distance:,.0f} meters ({distance/1000:,.1f} km)",
                    tooltip=f"{source_node.code} → {node.code}",
                    color='#ff0000',  # Bright red
                    weight=3,
                    opacity=0.8
                ).add_to(routes_group)
                edge_count += 1
        
        print(self._color_text(f"\nAdded {edge_count} routes from {airport_code}", "bright_green"))
        return edge_count
    
    def _debug_graph_structure(self):
        """Debug method to check graph structure"""
        print("\n=== DEBUG GRAPH STRUCTURE ===")
        print(f"Total nodes: {len(self.graph.nodes)}")
        
        edge_count = 0
        for i, node1 in enumerate(self.graph.nodes):
            for j, node2 in enumerate(self.graph.nodes):
                if i < j and self.graph.matrix[i][j] != 0:
                    edge_count += 1
                    if edge_count <= 5:  # Show first 5 edges
                        print(f"Edge: {node1.code} -> {node2.code} = {self.graph.matrix[i][j]}")
        
        print(f"Total edges found: {edge_count}")
        print("=============================\n")
    
    def analyze_connectivity(self):
        """Requirement 1: Analyze graph connectivity"""
        title = self._color_text("GRAPH CONNECTIVITY ANALYSIS", "bright_blue")
        print("\n" + "=" * 50)
        print(f"      {title}")
        print("=" * 50)
        
        if self.graph.is_connected():
            status = self._color_text("CONNECTED", "bright_green")
            print(f"✅ The airport network is {status}")
            airports_text = self._color_text(f"{self.graph.n}", "bright_yellow")
            print(f"All {airports_text} airports are reachable from each other")
        else:
            status = self._color_text("DISCONNECTED", "bright_red")
            print(f"❌ The airport network is {status}")
            
            components = self.graph.get_nodes_from_connected_components()
            component_sizes = [len(comp) for comp in components]
            
            count_text = self._color_text(str(len(components)), "bright_yellow")
            print(f"\nFound {count_text} connected components:")
            print("-" * 40)
            
            for i, (component, size) in enumerate(zip(components, component_sizes), 1):
                size_text = self._color_text(str(size), "bright_yellow")
                print(f"Component {self._color_text(str(i), 'bright_cyan')}: {size_text} airports")
                if size <= 10:
                    codes = [node.code for node in component]
                    codes_text = self._color_text(', '.join(codes), "bright_green")
                    print(f"   Airports: {codes_text}")
    
    def analyze_mst(self):
        """Requirement 2: Analyze Minimum Spanning Tree"""
        from utils.loading_animation import LoadingAnimation
        
        # Start loading animation
        loader = LoadingAnimation("Analyzing network topology")
        loader.start()
        
        try:
            title = self._color_text("MINIMUM SPANNING TREE ANALYSIS", "bright_blue")
            print("\n" + "=" * 50)
            print(f"   {title}")
            print("=" * 50)
            
            loader.message = "Checking network connectivity"
            if self.graph.is_connected():
                loader.message = "Calculating MST for connected network"
                total_weight = self.graph.get_mst_total_weight()
                loader.stop(True)
                
                status = self._color_text("Connected Network - Single MST", "bright_green")
                print(f"\n🌍 {status}")
                distance_m = self._color_text(f"{total_weight:,.0f}", "bright_yellow")
                distance_km = self._color_text(f"{total_weight/1000:,.0f}", "bright_yellow")
                print(f"Total MST distance: {distance_m} meters")
                print(f"                     {distance_km} kilometers")
            else:
                loader.message = "Analyzing disconnected components"
                components = self.graph.get_connected_subgraphs()
                loader.stop(True)
                
                status = self._color_text("Disconnected Network - Multiple MSTs (Forest)", "bright_yellow")
                print(f"\n🌐 {status}")
                
                total_system_distance = 0
                subtitle = self._color_text("MST Analysis per Component:", "bright_cyan")
                print(f"\n{subtitle}")
                print("-" * 50)
                
                for i, component in enumerate(components, 1):
                    if component.n >= 2:
                        loader = LoadingAnimation(f"Analyzing component {i}")
                        loader.start()
                        comp_weight = component.get_mst_total_weight()
                        total_system_distance += comp_weight
                        loader.stop(True)
                        
                        comp_size = self._color_text(str(component.n), "bright_yellow")
                        comp_weight_text = self._color_text(f"{comp_weight:,.0f}", "bright_yellow")
                        print(f"Component {self._color_text(str(i), 'bright_cyan')} ({comp_size} airports): {comp_weight_text} meters")
                
                total_distance = self._color_text(f"{total_system_distance:,.0f}", "bright_yellow")
                total_distance_km = self._color_text(f"{total_system_distance/1000:,.0f}", "bright_yellow")
                print(f"\n🌐 {self._color_text('Total system MST distance:', 'bright_cyan')} {total_distance} meters")
                print(f"   {self._color_text('                             ', 'bright_cyan')} {total_distance_km} kilometers")
                
        except Exception as e:
            loader.stop(False)
            print(self._color_text(f"\n❌ Error analyzing MST: {str(e)}", "bright_red"))
    
    def analyze_airport_info(self):
        """Requirement 3a: Show airport information"""
        print("\n" + self._color_text("✈️  AIRPORT INFORMATION", "bright_cyan"))
        print(self._color_text("─" * 50, "bright_cyan"))
        
        while True:
            airport_code = input("Enter airport code (or '0' to return): ").strip().upper()
            
            if airport_code == '0':
                return
                
            airport = self.graph.get_node_by_code(airport_code)
            
            if airport:
                self.current_airport = airport  # Store the selected airport
                self._display_airport_info(airport)
                return
            else:
                print(self._color_text(f"Airport '{airport_code}' not found. Please try again.", "bright_red"))

    def _display_airport_info(self, airport):
        """Helper method to display airport information"""
        header = self._color_text(f"AIRPORT INFORMATION: {airport.code}", "bright_blue")
        print(f"\n 📋 {header}")
        print("-" * 50)
        print(f"Code: {self._color_text(airport.code, 'bright_yellow')}")
        print(f"Name: {self._color_text(airport.name, 'bright_green')}")
        print(f"City: {self._color_text(airport.city, 'bright_cyan')}")
        print(f"Country: {self._color_text(airport.country, 'bright_cyan')}")
        coords = self._color_text(f"({airport.latitude:.4f}, {airport.longitude:.4f})", "bright_yellow")
        print(f"Coordinates: {coords}")
        
        # Show connectivity information
        degree = self.graph.get_node_degree(airport)
        degree_text = self._color_text(str(degree), "bright_yellow")
        print(f"Connected to: {degree_text} other airports")

    def _prompt_airport_selection(self, action):
        """Helper method to prompt for airport selection with current airport context"""
        while True:
            print("\n" + self._color_text("✈️  AIRPORT SELECTION", "bright_cyan"))
            print(self._color_text("─" * 50, "bright_cyan"))
            
            if self.current_airport:
                print(f"Current airport: {self._color_text(self.current_airport.code, 'highlight')} - "
                      f"{self._color_text(self.current_airport.name, 'bright_white')}")
                print(f"{self._color_text('1', 'bright_cyan')}. {action} from {self.current_airport.code}")
                print(f"{self._color_text('2', 'bright_cyan')}. Select a different airport")
            else:
                print(f"{self._color_text('1', 'bright_cyan')}. {action} from an airport")
            
            print(f"{self._color_text('0', 'bright_red')}. Return to main menu")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '0':
                return None
                
            if self.current_airport and choice == '1':
                return self.current_airport
                
            if (not self.current_airport and choice == '1') or (self.current_airport and choice == '2'):
                while True:
                    airport_code = input("\nEnter airport code (or '0' to cancel): ").strip().upper()
                    if airport_code == '0':
                        break
                    airport = self.graph.get_node_by_code(airport_code)
                    if airport:
                        self.current_airport = airport
                        return airport
                    print(self._color_text(f"Airport '{airport_code}' not found. Please try again.", "bright_red"))
            
            print(self._color_text("Invalid choice. Please try again.", "bright_red"))

    def _display_path_on_map(self, path_nodes, title):
        """Display a single path on an interactive map
        
        Args:
            path_nodes (list): List of Node objects representing the path
            title (str): Title to display on the map
        """
        if not path_nodes:
            print(self._color_text("No valid path to display.", "bright_yellow"))
            return
            
        try:
            # Create a map centered on the first node
            first_node = path_nodes[0]
            m = folium.Map(
                location=[first_node.latitude, first_node.longitude],
                zoom_start=3,
                tiles='OpenStreetMap'
            )
            
            # Add the path as a polyline
            locations = [[node.latitude, node.longitude] for node in path_nodes]
            folium.PolyLine(
                locations=locations,
                color='blue',
                weight=2.5,
                opacity=1,
                tooltip=title
            ).add_to(m)
            
            # Add markers for each airport in the path
            for i, node in enumerate(path_nodes):
                # Different color for start and end points
                color = 'green' if i == 0 else 'red' if i == len(path_nodes) - 1 else 'blue'
                
                folium.Marker(
                    location=[node.latitude, node.longitude],
                    popup=f"""
                        <div style="width: 200px;">
                            <h4>{node.code} - {node.name}</h4>
                            <p><b>City:</b> {node.city}</p>
                            <p><b>Country:</b> {node.country}</p>
                            <p><b>Coordinates:</b><br>{node.latitude:.4f}, {node.longitude:.4f}</p>
                        </div>
                    """,
                    tooltip=f"{i+1}. {node.code}: {node.name}",
                    icon=folium.Icon(color=color, icon='plane', prefix='fa')
                ).add_to(m)
            
            # Save to temporary file and open in browser
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w') as f:
                temp_file = f.name
                m.save(temp_file)
            
            webbrowser.open('file://' + os.path.abspath(temp_file))
            print(self._color_text("\nMap opened in browser!", "bright_green"))
            
        except Exception as e:
            print(self._color_text(f"Error displaying map: {str(e)}", "bright_red"))
    
    def analyze_longest_paths(self):
        """Requirement 3b: Show top 10 longest shortest paths from a selected airport"""
        # Prompt for airport selection
        airport = self._prompt_airport_selection("Find longest paths")
        if not airport:
            return
            
        print("\n" + self._color_text(f"🛫  LONGEST PATHS FROM {airport.code}", "bright_cyan"))
        print(self._color_text("─" * 50, "bright_cyan"))
        
        # Calculate shortest paths from the selected airport
        print(f"Calculating shortest paths from {airport.code}...")
        # Call get_longest_paths which internally uses dijkstra with the airport code
        paths = self.graph.get_longest_paths(airport.code)
        
        if not paths:
            print(self._color_text("No reachable paths found from this airport.", "bright_yellow"))
            return
            
        # Display top 10
        print("\n" + self._color_text(f"TOP 10 LONGEST PATHS FROM {airport.code}", "bright_yellow"))
        print(self._color_text("─" * 50, "bright_yellow"))
        
        for idx, path in enumerate(paths[:10], 1):
            print(f"{self._color_text(str(idx).rjust(2), 'bright_cyan')}. "
                  f"{self._color_text(f'{path.start_node.code} → {path.end_node.code}', 'highlight')} - "
                  f"{self._color_text(f'{path.distance/1000:,.1f} km', 'bright_green')}")
            print(f"   {path.end_node.name} ({path.end_node.city}, {path.end_node.country})")
        
        # Show all paths on map by default
        show_map = input("\nShow all paths on map? (y/n): ").strip().lower()
        if show_map == 'y':
            # Create a map centered on the source airport
            m = folium.Map(
                location=[airport.latitude, airport.longitude],
                zoom_start=3,
                tiles='OpenStreetMap'
            )
            
            # Add the source airport marker
            folium.Marker(
                location=[airport.latitude, airport.longitude],
                popup=f"""
                    <div style="width: 200px;">
                        <h4>{airport.code} - {airport.name}</h4>
                        <p><b>City:</b> {airport.city}</p>
                        <p><b>Country:</b> {airport.country}</p>
                        <p><b>Coordinates:</b><br>{airport.latitude:.4f}, {airport.longitude:.4f}</p>
                    </div>
                """,
                tooltip=f"Source: {airport.code}",
                icon=folium.Icon(color='green', icon='plane', prefix='fa')
            ).add_to(m)
            
            # Add paths to the top 10 destinations
            for i, path in enumerate(paths[:10], 1):
                if not path.nodes:
                    continue
                    
                # Add the path as a polyline
                locations = [[node.latitude, node.longitude] for node in path.nodes]
                folium.PolyLine(
                    locations=locations,
                    color='blue',
                    weight=1.5,
                    opacity=0.7,
                    tooltip=f"{path.start_node.code} → {path.end_node.code}: {path.distance/1000:,.1f} km"
                ).add_to(m)
                
                # Add destination marker
                dest = path.end_node
                folium.Marker(
                    location=[dest.latitude, dest.longitude],
                    popup=f"""
                        <div style="width: 200px;">
                            <h4>{dest.code} - {dest.name}</h4>
                            <p><b>Distance:</b> {path.distance/1000:,.1f} km</p>
                            <p><b>City:</b> {dest.city}</p>
                            <p><b>Country:</b> {dest.country}</p>
                        </div>
                    """,
                    tooltip=f"{i}. {dest.code}: {path.distance/1000:,.1f} km",
                    icon=folium.Icon(color='red', icon='plane', prefix='fa')
                ).add_to(m)
            
            # Save to temporary file and open in browser
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w') as f:
                temp_file = f.name
                m.save(temp_file)
            
            webbrowser.open('file://' + os.path.abspath(temp_file))
            print(self._color_text("\nMap opened in browser!", "bright_green"))

    def _display_path_on_map(self, path_nodes, title):
        """Display a single path on an interactive map
        
        Args:
            path_nodes (list): List of Node objects representing the path
            title (str): Title to display on the map
        """
        if not path_nodes:
            print(self._color_text("No valid path to display.", "bright_yellow"))
            return
                
        try:
            # Create a map centered on the first node
            first_node = path_nodes[0]
            m = folium.Map(
                location=[first_node.latitude, first_node.longitude],
                zoom_start=3,
                tiles='OpenStreetMap'
            )
            
            # Add the path as a polyline
            locations = [[node.latitude, node.longitude] for node in path_nodes]
            folium.PolyLine(
                locations=locations,
                color='blue',
                weight=2.5,
                opacity=1,
                tooltip=title
            ).add_to(m)
            
            # Add markers for each airport in the path
            for i, node in enumerate(path_nodes):
                # Different color for start and end points
                color = 'green' if i == 0 else 'red' if i == len(path_nodes) - 1 else 'blue'
                
                folium.Marker(
                    location=[node.latitude, node.longitude],
                    popup=f"""
                        <div style="width: 200px;">
                            <h4>{node.code} - {node.name}</h4>
                            <p><b>City:</b> {node.city}</p>
                            <p><b>Country:</b> {node.country}</p>
                            <p><b>Coordinates:</b><br>{node.latitude:.4f}, {node.longitude:.4f}</p>
                        </div>
                    """,
                    tooltip=f"{i+1}. {node.code}: {node.name}",
                    icon=folium.Icon(color=color, icon='plane', prefix='fa')
                ).add_to(m)
            
            # Save to temporary file and open in browser
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w') as f:
                temp_file = f.name
                m.save(temp_file)
            
            webbrowser.open('file://' + os.path.abspath(temp_file))
            print(self._color_text("\nMap opened in browser!", "bright_green"))
            
        except Exception as e:
            print(self._color_text(f"Error displaying map: {str(e)}", "bright_red"))
    
    def analyze_longest_paths(self):
        """Requirement 3b: Show top 10 longest shortest paths from a selected airport"""
        # Prompt for airport selection
        airport = self._prompt_airport_selection("Find longest paths")
        if not airport:
            return
            
        print("\n" + self._color_text(f"🛫  LONGEST PATHS FROM {airport.code}", "bright_cyan"))
        print(self._color_text("─" * 50, "bright_cyan"))
        
        # Calculate shortest paths from the selected airport
        print(f"Calculating shortest paths from {airport.code}...")
        paths = self.graph.get_longest_paths(airport.code)
        
        if not paths:
            print(self._color_text("No reachable paths found from this airport.", "bright_yellow"))
            return
            
        # Display top 10
        print("\n" + self._color_text(f"TOP 10 LONGEST PATHS FROM {airport.code}", "bright_yellow"))
        print(self._color_text("─" * 50, "bright_yellow"))
        
        for idx, path in enumerate(paths[:10], 1):
            print(f"{self._color_text(str(idx).rjust(2), 'bright_cyan')}. "
                f"{self._color_text(f'{path.start_node.code} → {path.end_node.code}', 'highlight')} - "
                f"{self._color_text(f'{path.distance/1000:,.1f} km', 'bright_green')}")
            print(f"   {path.end_node.name} ({path.end_node.city}, {path.end_node.country})")
        
        # Show all paths on map by default
        show_map = input("\nShow all paths on map? (y/n): ").strip().lower()
        if show_map == 'y':
            # Create a map centered on the source airport
            m = folium.Map(
                location=[airport.latitude, airport.longitude],
                zoom_start=3,
                tiles='OpenStreetMap'
            )
            
            # Define a list of distinct colors for the paths
            path_colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 
                        'lightred', 'beige', 'darkblue', 'darkgreen', 
                        'lightgreen', 'darkpurple', 'pink', 'lightblue', 
                        'gray', 'black', 'lightgray']
            
            # Add the source airport marker (special marker)
            folium.Marker(
                location=[airport.latitude, airport.longitude],
                popup=f"""
                    <div style="width: 250px;">
                        <h4 style="color: green; margin-bottom: 10px;">🚀 SOURCE AIRPORT</h4>
                        <h5>{airport.code} - {airport.name}</h5>
                        <p><b>City:</b> {airport.city}</p>
                        <p><b>Country:</b> {airport.country}</p>
                        <p><b>Coordinates:</b><br>{airport.latitude:.4f}, {airport.longitude:.4f}</p>
                    </div>
                """,
                tooltip=f"🚀 Source: {airport.code}",
                icon=folium.Icon(color='green', icon='star', prefix='fa')
            ).add_to(m)
            
            # Create a feature group for paths to organize them
            paths_group = folium.FeatureGroup(name="Longest Paths")
            
            # Track all airports that have been marked to avoid duplicates
            marked_airports = set([airport.code])
            
            # Add paths to the top 10 destinations
            for i, path in enumerate(paths[:10], 1):
                if not path.nodes:
                    continue
                    
                # Get color for this path (cycle through colors if more than 10 paths)
                color = path_colors[i % len(path_colors)]
                
                # Add the path as a polyline
                locations = [[node.latitude, node.longitude] for node in path.nodes]
                folium.PolyLine(
                    locations=locations,
                    color=color,
                    weight=3,
                    opacity=0.8,
                    tooltip=f"Path {i}: {path.start_node.code} → {path.end_node.code} ({path.distance/1000:,.1f} km)",
                    popup=f"""
                        <div style="width: 250px;">
                            <h4 style="color: {color};">Path #{i}</h4>
                            <p><b>Route:</b> {path.start_node.code} → {path.end_node.code}</p>
                            <p><b>Distance:</b> {path.distance/1000:,.1f} km</p>
                            <p><b>Number of stops:</b> {len(path.nodes)}</p>
                            <p><b>Color:</b> <span style="color: {color};">{color.upper()}</span></p>
                        </div>
                    """
                ).add_to(paths_group)
                
                # Add markers for each airport in this path
                for j, node in enumerate(path.nodes):
                    # Skip if we've already marked this airport (to avoid duplicate markers)
                    if node.code in marked_airports:
                        continue
                        
                    marked_airports.add(node.code)
                    
                    # Determine if this is the start, end, or intermediate node
                    if node.code == path.start_node.code:
                        node_type = "START"
                        icon_color = 'green'
                        icon_type = 'play'  # Start icon
                    elif node.code == path.end_node.code:
                        node_type = f"END (Path {i})"
                        icon_color = color
                        icon_type = 'flag'  # End icon
                    else:
                        node_type = f"Intermediate (Path {i})"
                        icon_color = 'gray'
                        icon_type = 'circle'
                    
                    # Create marker for this airport
                    folium.Marker(
                        location=[node.latitude, node.longitude],
                        popup=f"""
                            <div style="width: 250px;">
                                <h4 style="color: {icon_color};">{node_type}</h4>
                                <h5>{node.code} - {node.name}</h5>
                                <p><b>City:</b> {node.city}</p>
                                <p><b>Country:</b> {node.country}</p>
                                <p><b>Path #{i}:</b> {path.start_node.code} → {path.end_node.code}</p>
                                <p><b>Distance:</b> {path.distance/1000:,.1f} km</p>
                                <p><b>Coordinates:</b><br>{node.latitude:.4f}, {node.longitude:.4f}</p>
                            </div>
                        """,
                        tooltip=f"{node_type}: {node.code}",
                        icon=folium.Icon(color=icon_color, icon=icon_type, prefix='fa')
                    ).add_to(m)
            
            # Add the paths group to the map
            paths_group.add_to(m)
            
            # Add layer control
            folium.LayerControl().add_to(m)
            
            # Add a legend
            legend_html = '''
            <div style="position: fixed; 
                        top: 10px; left: 50px; width: 300px; height: auto; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px">
                <h4 style="margin-top:0">Longest Paths Legend</h4>
                <p><i class="fa fa-star" style="color: green"></i> Source Airport</p>
            '''
            
            # Add legend items for each path
            for i, path in enumerate(paths[:10], 1):
                color = path_colors[i % len(path_colors)]
                legend_html += f'<p><i class="fa fa-flag" style="color: {color}"></i> Path {i}: {path.start_node.code} → {path.end_node.code}</p>'
            
            legend_html += '</div>'
            m.get_root().html.add_child(folium.Element(legend_html))
            
            # Save to temporary file and open in browser
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w') as f:
                temp_file = f.name
                m.save(temp_file)
            
            webbrowser.open('file://' + os.path.abspath(temp_file))
            print(self._color_text("\nMap opened in browser!", "bright_green"))
            print(self._color_text(f"Showing {min(10, len(paths))} longest paths from {airport.code}", "bright_cyan"))
            print(self._color_text("Each path is shown in a different color with markers for all airports", "bright_cyan"))

    def find_shortest_path(self):
        """Requirement 4: Find shortest path between two airports"""
        title = self._color_text("SHORTEST PATH FINDER", "bright_blue")
        print("\n" + "=" * 50)
        print(f"      {title}")
        print("=" * 50)
        
        # Get source airport
        while True:
            code1 = input(self._color_text("Enter source airport code: ", "bright_cyan")).strip().upper()
            if not code1:
                continue
                
            source_airport = self.graph.get_node_by_code(code1)
            if source_airport:
                break
                
            print(self._color_text(f"Airport '{code1}' not found. Please try again.", "bright_red"))
        
        # Get destination airport
        while True:
            code2 = input(self._color_text("Enter destination airport code: ", "bright_cyan")).strip().upper()
            if not code2:
                continue
                
            dest_airport = self.graph.get_node_by_code(code2)
            if not dest_airport:
                print(self._color_text(f"Airport '{code2}' not found. Please try again.", "bright_red"))
                continue
                
            if dest_airport == source_airport:
                print(self._color_text("Source and destination airports cannot be the same. Please enter a different destination.", "bright_yellow"))
                continue
                
            break
        
        print("\n" + self._color_text(f"Finding shortest path from {source_airport.code} to {dest_airport.code}...\n", "bright_cyan"))
        
        # Find the shortest path using Dijkstra's algorithm
        print("🔍 Calculating optimal route...")
        path = self.graph.dijkstra(source_airport.code, dest_airport.code)
        
        if not path or path.is_unreachable():
            error_msg = self._color_text(f"No path found from {source_airport.code} to {dest_airport.code}", "bright_red")
            print(f"\n❌ {error_msg}")
            return
        
        # Display the path
        print(f"\n{self._color_text('🛫 SHORTEST PATH:', 'bright_green')} {source_airport.code} → {dest_airport.code}")
        print("=" * 60)
        
        # Display path details
        print(f"{self._color_text('From:', 'bright_cyan')} {source_airport.name} ({source_airport.code})")
        print(f"{self._color_text('  To:', 'bright_cyan')} {dest_airport.name} ({dest_airport.code})")
        print(f"{self._color_text('Total Distance:', 'bright_cyan')} {path.distance/1000:,.1f} km")
        
        # Display the route if available
        if path.nodes and len(path.nodes) > 1:
            print("\n" + self._color_text("Route:", "bright_cyan"))
            for i, node in enumerate(path.nodes):
                if i > 0:
                    prev_node = path.nodes[i-1]
                    dist = prev_node.haversine(node)
                    print(f"   {self._color_text('✈', 'bright_red')} {prev_node.code} → {node.code}: {dist/1000:,.1f} km")
                print(f"   {self._color_text('●', 'bright_green')} {node.name} ({node.code})")
        
        # Ask to show on map
        show_map = input("\nShow this path on map? (y/n): ").strip().lower()
        if show_map == 'y':
            self._display_path_on_map(path.nodes, f"{source_airport.code} → {dest_airport.code} ({path.distance/1000:,.1f} km)")
        
        print("\n" + "=" * 60)