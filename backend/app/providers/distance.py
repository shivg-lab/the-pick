from math import asin, cos, radians, sin, sqrt
from typing import Protocol
from app.models.domain import Coordinates

LOCATIONS = {
    "san jose": (37.3382, -121.8863),
    "95112": (37.3382, -121.8863),
    "95113": (37.3382, -121.8863),
    "san francisco": (37.7749, -122.4194),
    "94103": (37.7749, -122.4194),
    "oakland": (37.8044, -122.2712),
    "94612": (37.8044, -122.2712),
    "berkeley": (37.8715, -122.273),
    "94704": (37.8715, -122.273),
    "palo alto": (37.4419, -122.143),
    "94301": (37.4419, -122.143),
    "santa clara": (37.3541, -121.9552),
    "95050": (37.3541, -121.9552),
    "stanford": (37.4275, -122.1697),
    "94305": (37.4275, -122.1697),
}


class DistanceProvider(Protocol):
    def miles(self, origin: Coordinates, destination: Coordinates) -> float: ...


class HaversineDistanceProvider:
    def miles(self, origin: Coordinates, destination: Coordinates) -> float:
        a, b = radians(origin.lat), radians(destination.lat)
        delta = sin((b - a) / 2) ** 2 + cos(a) * cos(b) * sin(radians(destination.lon - origin.lon) / 2) ** 2
        return 3958.7613 * 2 * asin(min(1, sqrt(delta)))


def locate(location: str) -> Coordinates | None:
    value = LOCATIONS.get(location.lower().strip())
    return Coordinates(lat=value[0], lon=value[1]) if value else None
