"""
Various tools related to playfield and distance calculations
TODO: I hate calling something as tools
"""

import math

PLAYFIELD_RADIUS = 6000
FIELD_SIZE = PLAYFIELD_RADIUS * 2
SQUARE_COUNT = 10
SQUARE_SPLIT = FIELD_SIZE // SQUARE_COUNT
WATER_TOWN_RADIUS = 3000




def dot_product(x: float, y: float, vx: float, vy: float) -> float:
    return x * vx + y * vy


def is_moving_towards_center(x: float, y: float, vx: float, vy: float) -> bool:
    dot_prod = dot_product(x, y, vx, vy)

    if dot_prod < 0:
        return True

    return False


def is_inside_water_town(x: int, y: int, radius_threshold: int = WATER_TOWN_RADIUS) -> bool:
    return (x**2 + y**2) ** 0.5 <= radius_threshold


def is_inside_playfield(x: int, y: int, radius_threshold: int = PLAYFIELD_RADIUS):
    return (x**2 + y**2) ** 0.5 <= radius_threshold


def calculate_velocity(v0x: float, v0y: float, throttle: int, m: float, f: float) -> tuple[float, float]:
    """
    Calculate the new velocities (vx, vy) given the initial velocities in x and y directions,
    the overall throttle, and the mass and friction.

    Parameters:
    - v0x: Initial velocity in the x direction
    - v0y: Initial velocity in the y direction
    - throttle: Overall throttle applied (affects both x and y components)
    - m: Mass
    - f: Friction factor

    Returns:
    - vx: New velocity in the x direction
    - vy: New velocity in the y direction
    """

    # Step 1: Calculate the initial magnitude of the velocity vector
    v0 = math.sqrt(v0x**2 + v0y**2)

    # Step 2: Apply throttle to the velocity magnitude
    v = (v0 + (throttle / m)) * (1 - f)

    # Step 3: Calculate the angle (direction) of the velocity vector
    theta = math.atan2(v0y, v0x)

    # Step 4: Break the new velocity magnitude into x and y components
    vx = v * math.cos(theta)
    vy = v * math.sin(theta)

    return vx, vy


def get_grid_position(coordinate: tuple[int, int], split_size=SQUARE_SPLIT) -> tuple[int, int]:
    """
    Get the grid position of a coordinate.
    """
    x, y = coordinate
    return x // split_size, y // split_size


def get_manhattan_distance(coordinate_a: tuple[int, int], coordinate_b: tuple[int, int]) -> int:
    return abs(coordinate_a[0] - coordinate_b[0]) + abs(coordinate_a[1] - coordinate_b[1])


def get_euclidean_distance(coordinate_a: tuple[int, int], coordinate_b: tuple[int, int]):
    return math.sqrt((coordinate_a[0] - coordinate_b[0]) ** 2 + (coordinate_a[1] - coordinate_b[1]) ** 2)


# grid_state: dict[tuple[int, int], list[Entity]] = {}
# tanker_grid_positions: list[GridUnitState]


# coordinate -> total water content, list of tanker objects
# tanker_grid_water_summary: dict[tuple[int, int], int]
