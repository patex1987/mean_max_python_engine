"""
This modules contains only a simple way to simulate the movement of a tanker.
Starting somewhere in the playfield, moving towards the center of the field, then
turning around and moving back to the edge of the field
"""

import math

FIELD_SIZE = 6000 * 2
SQUARE_COUNT = 10
SQUARE_SPLIT = FIELD_SIZE // SQUARE_COUNT
WATER_TOWN_RADIUS = 3000
PLAYFIELD_RADIUS = 6000


def get_next_tanker_state(tanker_state: 'TankerState') -> 'TankerState':
    """
    Simulate the movement of a tanker for a given duration and throttle.
    """
    if tanker_state.water_quantity == tanker_state.water_capacity:
        towards_center = is_moving_towards_center(tanker_state.x, tanker_state.y, tanker_state.vx, tanker_state.vy)
        if towards_center:
            print('[DEBUG] turning the direction of the tanker, as the capacity is full')
            opposite_vx, opposite_vy = -tanker_state.vx, -tanker_state.vy

            updated_vx, updated_vy = calculate_velocity(
                opposite_vx,
                opposite_vy,
                tanker_state.throttle,
                tanker_state.mass,
                tanker_state.friction,
            )
            updated_x, updated_y = tanker_state.x + updated_vx, tanker_state.y + updated_vy
            new_tanker_state = TankerState(
                updated_x,
                updated_y,
                updated_vx,
                updated_vy,
                tanker_state.radius,
                tanker_state.water_capacity,
                tanker_state.water_quantity,
            )
            return new_tanker_state

        updated_vx, updated_vy = calculate_velocity(
            tanker_state.vx,
            tanker_state.vy,
            tanker_state.throttle,
            tanker_state.mass,
            tanker_state.friction,
        )
        updated_x, updated_y = tanker_state.x + updated_vx, tanker_state.y + updated_vy
        new_tanker_state = TankerState(
            updated_x,
            updated_y,
            updated_vx,
            updated_vy,
            tanker_state.radius,
            tanker_state.water_capacity,
            tanker_state.water_quantity,
        )
        return new_tanker_state

    inside_water_town = is_inside_water_town(tanker_state.x, tanker_state.y)
    water_quantity = tanker_state.water_quantity
    if inside_water_town:
        water_quantity = min(tanker_state.water_capacity, tanker_state.water_quantity + 1)

    updated_vx, updated_vy = calculate_velocity(
        tanker_state.vx,
        tanker_state.vy,
        tanker_state.throttle,
        tanker_state.mass,
        tanker_state.friction,
    )
    updated_x, updated_y = tanker_state.x + updated_vx, tanker_state.y + updated_vy
    new_tanker_state = TankerState(
        updated_x,
        updated_y,
        updated_vx,
        updated_vy,
        tanker_state.radius,
        tanker_state.water_capacity,
        water_quantity,
    )

    return new_tanker_state


def calculate_velocity(v0x, v0y, throttle, m, f):
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


def get_grid_position(coordinate: tuple[int, int], split_size=SQUARE_SPLIT):
    """
    Get the grid position of a coordinate.
    """
    x, y = coordinate
    return x // split_size, y // split_size


class TankerState:
    def __init__(self, x, y, vx, vy, radius, water_capacity, water_quantity):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.friction = 0.4
        self.throttle = 500
        self.water_quantity = water_quantity
        self.water_capacity = water_capacity
        self.mass = 2.5 + (0.5 * water_quantity)

    def __repr__(self):
        return (
            f"TankerState("
            f"x={self.x:.02f}, "
            f"y={self.y:.02f}, "
            f"vx={self.vx:.02f}, "
            f"vy={self.vy:.02f}, "
            f"radius={self.radius}, "
            f"water_quantity={self.water_quantity}, "
            f"mass={self.mass})"
        )


def dot_product(x, y, vx, vy):
    return x * vx + y * vy


def is_moving_towards_center(x, y, vx, vy):
    dot_prod = dot_product(x, y, vx, vy)

    if dot_prod < 0:
        return True

    return False


def is_inside_water_town(x, y, radius_threshold=WATER_TOWN_RADIUS):
    return (x**2 + y**2) ** 0.5 <= radius_threshold


def is_inside_playfield(x, y, radius_threshold=PLAYFIELD_RADIUS):
    return (x**2 + y**2) ** 0.5 <= radius_threshold
