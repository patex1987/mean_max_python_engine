from dataclasses import dataclass
from enum import Enum


class Entity(Enum):
    """
    TODO: this doesn't differentiate between player and enemies
    """

    REAPER = 0
    DESTROYER = 1
    DOOF = 2
    TANKER = 3
    WRECK = 4
    TAR_POOL = 5
    OIL_POOL = 6


class EntitiesForReaper(Enum):
    REAPER = 0
    DESTROYER = 1
    DOOF = 2
    TANKER = 3
    WRECK = 4
    TAR_POOL = 5
    OIL_POOL = 6
    OTHER_ENEMY = 7


class PlayerFieldTypes(Enum):
    PLAYER = 0
    ENEMY_1 = 1
    ENEMY_2 = 2


class Unit:
    def __init__(
        self,
        x,
        y,
        vx,
        vy,
        radius,
        unit_type,
        player=None,
        unit_id=None,
        mass=None,
        extra=None,
        extra_2=None,
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.unit_type = unit_type
        self.player = player
        self.unit_id = unit_id
        self.mass = mass
        self.extra = extra
        self.extra_2 = extra_2


class GridUnitState:
    """
    TODO: this stores only the units today, we need to create an
        interface as we **might** need the exact implementation
    TODO: think about moving the grid_coordinate into the unit
        object (Unit class)
    """

    def __init__(self, grid_coordinate: tuple[int, int], unit: Unit):
        self.grid_coordinate = grid_coordinate
        self.unit = unit


GRID_COORD_UNIT_STATE_T = dict[tuple[int, int], list[GridUnitState]]


@dataclass
class GameGridInformation:
    """
    right now recreated on every round
    """

    full_grid_state: GRID_COORD_UNIT_STATE_T
    wreck_grid_state: GRID_COORD_UNIT_STATE_T
    wreck_id_to_grid_coord: dict[int, tuple[int, int]]
    tanker_grid_state: GRID_COORD_UNIT_STATE_T
    tanker_id_to_grid_coord: dict[int, tuple[int, int]]
    enemy_reaper_grid_state: GRID_COORD_UNIT_STATE_T
    enemy_reaper_id_to_grid_coord: dict[int, tuple[int, int]]
    enemy_others_grid_state: GRID_COORD_UNIT_STATE_T
    enemy_others_id_to_grid_coord: dict[int, tuple[int, int]]
    oil_pool_grid_state: GRID_COORD_UNIT_STATE_T
    oil_pool_id_to_grid_coord: dict[int, tuple[int, int]]


@dataclass
class PlayerState:
    """
    TODO: most probably other fields will be needed, but let's start with
        the bare minimum
    """

    reaper_state: GridUnitState
    destroyer_state: GridUnitState
    doof_state: GridUnitState
    rage: int
    score: int
    rage_gained: int = 0
    score_gained: int = 0
    oil_pool_tracker: OilPoolTracker = field(default_factory=OilPoolTracker)

    def __init__(
        self,
        reaper_state: GridUnitState,
        destroyer_state: GridUnitState,
        doof_state: GridUnitState,
        rage: int,
        score: int,
        prev_rage: int | None,
        prev_score: int | None,
    ):
        self.reaper_state = reaper_state
        self.destroyer_state = destroyer_state
        self.doof_state = doof_state
        self.rage = rage
        self.score = score
        if prev_rage:
            self.rage_gained = rage - prev_rage
        if prev_score:
            self.score_gained = score - prev_score


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
