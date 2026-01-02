"""
Utility functions for calculating distances between geographic coordinates.
"""
import math


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate the great circle distance between two points on Earth using the Haversine formula.
    
    Args:
        lat1: Latitude of the first point in degrees
        lon1: Longitude of the first point in degrees
        lat2: Latitude of the second point in degrees
        lon2: Longitude of the second point in degrees
    
    Returns:
        Distance between the two points in kilometers
    
    Raises:
        ValueError: If any coordinate is None or invalid
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        raise ValueError("All coordinates must be provided (cannot be None)")
    
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Calculate differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    
    # Distance in kilometers
    distance = R * c
    
    return distance

