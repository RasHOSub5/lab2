import math

class Node:
    """
    Represents an airport node in the flight network graph.
    
    Attributes:
        code (str): IATA 3-letter airport code (e.g., 'JFK')
        name (str): Full name of the airport
        city (str): City where the airport is located
        country (str): Country where the airport is located
        latitude (float): Geographic latitude in decimal degrees
        longitude (float): Geographic longitude in decimal degrees
    """
    
    def __init__(self, code, name, city, country, latitude, longitude):
        """
        Initializes a new Node object.
        
        Args:
            code (str): IATA 3-letter airport code
            name (str): Full name of the airport
            city (str): City where the airport is located
            country (str): Country where the airport is located
            latitude (float): Geographic latitude in decimal degrees
            longitude (float): Geographic longitude in decimal degrees
        """
        self.code = code
        self.name = name
        self.city = city
        self.country = country
        self.latitude = latitude
        self.longitude = longitude

    def __hash__(self):
        return hash(self.code)
    
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        
        return self.code == other.code

    def __repr__(self):
        return f"Node({self.code})"

    def haversine(self, other):
        """
        Calculate the great-circle distance between two points on Earth's surface.
        Uses the Haversine formula to account for Earth's curvature.
        
        Args:
            other (Node): Another Node object to calculate distance to
            
        Returns:
            float: Distance in meters between the two points
            
        Reference:
            https://community.esri.com/t5/coordinate-reference-systems-blog/distance-on-a-sphere-the-haversine-formula/ba-p/902128
        """
        longitude1 = self.longitude
        latitude1 = self.latitude

        longitude2 = other.longitude
        latitude2 = other.latitude

        earth_radius = 6371000 # meters
        phi1 = math.radians(latitude1)
        phi2 = math.radians(latitude2)

        delta_phi = math.radians(latitude2 - latitude1)
        delta_lambda = math.radians(longitude2 - longitude1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return earth_radius * c # in meters

    def get_info(self):
        return f"{self.name} ({self.code}), {self.city}, {self.county} at ({self.latitude}, {self.longitude})"