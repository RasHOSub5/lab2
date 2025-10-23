import folium
from folium.plugins import MarkerCluster

class MapView:
    def __init__(self, graph):
        self.graph = graph
        self.map = None
    
    def create_map(self):
        """Create a Folium map with airport markers."""
        # Default to first node's location or fallback to a default
        default_lat = 40.7128
        default_lon = -74.0060
        
        if self.graph.nodes:
            default_lat = self.graph.nodes[0].latitude
            default_lon = self.graph.nodes[0].longitude
        
        self.map = folium.Map(
            location=[default_lat, default_lon],
            zoom_start=12,
            width='100%',
            height='100%'
        )
        
        marker_cluster = MarkerCluster().add_to(self.map)
        
        for node in self.graph.nodes:
            degree = self.graph.get_node_degree(node)
            if degree > 20:
                color = 'red'
            elif degree > 10:
                color = 'orange'
            elif degree > 5:
                color = 'green'
            else:
                color = 'blue'

            html = f'''
            <div style="text-align: center;">
                <h3>{node.get_info()}</h3>
                <button onclick="alert('You selected {node.name}!')"
                        style="background: green; color: white; 
                            padding: 8px 16px; border: none; border-radius: 4px;">
                    Select {node.name}
                </button>
            </div>
            '''

            folium.Marker(
                [node.latitude, node.longitude],
                popup=folium.Popup(html, max_width=250),
                tooltip=f"{node.name}",
                icon=folium.Icon(color=color)
            ).add_to(marker_cluster)
    
    def save_map(self, filename='map.html'):
        """Save the map to an HTML file."""
        if self.map:
            self.map.save(filename)
            return filename
        return None
    
    def get_map_html(self):
        """Return the map as HTML string."""
        if self.map:
            return self.map.get_root().render()
        return ""
