from dataclasses import dataclass

@dataclass
class School:
    name: str
    rating: float
    level: str
    city: str
    state: str
    zipcode: str

