"""
TODO: these can be later moved to some sort of test suite (most probably conftest.py)
"""

from collections import defaultdict
from typing import Any

from python_prototypes.field_tools import get_grid_position
from python_prototypes.field_types import (
    Unit,
    Entity,
    PlayerFieldTypes,
    GRID_COORD_UNIT_STATE_T,
    GridUnitState,
    GameGridInformation,
)


def get_example_full_grid_state():

    enemy_1_destroyer = Unit(
        unit_type=Entity.DESTROYER.value,
        x=200,
        y=200,
        vx=0,
        vy=0,
        radius=30,
        unit_id=1,
        player=PlayerFieldTypes.ENEMY_1.value,
    )
    enemy_2_destroyer = Unit(
        unit_type=Entity.DESTROYER.value,
        x=2600,
        y=200,
        vx=0,
        vy=0,
        radius=30,
        unit_id=2,
        player=PlayerFieldTypes.ENEMY_2.value,
    )
    tanker_1 = Unit(
        unit_type=Entity.TANKER.value, x=2800, y=400, vx=-0.98994, vy=-0.141421, radius=30, unit_id=3, player=None
    )
    tanker_2 = Unit(
        unit_type=Entity.TANKER.value, x=2800, y=2600, vx=-0.707, vy=-0.707, radius=30, unit_id=4, player=None
    )
    player_doof = Unit(
        unit_type=Entity.DOOF.value,
        x=3800,
        y=2600,
        vx=0,
        vy=0,
        radius=30,
        unit_id=5,
        player=PlayerFieldTypes.PLAYER.value,
    )
    player_destroyer = Unit(
        unit_type=Entity.DESTROYER.value,
        x=2800,
        y=3800,
        vx=0,
        vy=0,
        radius=30,
        unit_id=6,
        player=PlayerFieldTypes.PLAYER.value,
    )

    full_grid_state: GRID_COORD_UNIT_STATE_T = defaultdict(list)

    wreck_grid_state: GRID_COORD_UNIT_STATE_T = defaultdict(list)
    wreck_id_to_grid_coord: dict[Any, tuple[int, int]] = {}
    tanker_grid_state: GRID_COORD_UNIT_STATE_T = defaultdict(list)
    tanker_id_to_grid_coord: dict[Any, tuple[int, int]] = {}
    enemy_reaper_grid_state: GRID_COORD_UNIT_STATE_T = defaultdict(list)
    enemy_reaper_id_to_grid_coord: dict[Any, tuple[int, int]] = {}
    enemy_others_grid_state: GRID_COORD_UNIT_STATE_T = defaultdict(list)
    enemy_others_id_to_grid_coord: dict[Any, tuple[int, int]] = {}

    for unit in (
        enemy_1_destroyer,
        enemy_2_destroyer,
        tanker_1,
        tanker_2,
        player_doof,
        player_destroyer,
    ):
        grid_coordinate = get_grid_position(coordinate=(unit.x, unit.y))
        grid_unit = GridUnitState(grid_coordinate, unit)
        full_grid_state[grid_coordinate].append(grid_unit)

        unit_type = unit.unit_type
        unit_id = unit.unit_id
        player = unit.player

        if unit_type == Entity.WRECK.value:
            wreck_grid_state[grid_coordinate].append(grid_unit)
            wreck_id_to_grid_coord[unit_id] = grid_coordinate
            continue

        if unit_type == Entity.TANKER.value:
            tanker_grid_state[grid_coordinate].append(grid_unit)
            tanker_id_to_grid_coord[unit_id] = grid_coordinate
            continue

        if unit_type == Entity.REAPER.value and player != PlayerFieldTypes.PLAYER.value:
            enemy_reaper_grid_state[grid_coordinate].append(grid_unit)
            enemy_reaper_id_to_grid_coord[unit_id] = grid_coordinate
            continue

        if unit_type in [Entity.DESTROYER.value, Entity.DOOF.value] and player != PlayerFieldTypes.PLAYER.value:
            enemy_others_grid_state[grid_coordinate].append(grid_unit)
            enemy_others_id_to_grid_coord[unit_id] = grid_coordinate
            continue

    game_grid_information = GameGridInformation(
        full_grid_state=full_grid_state,
        wreck_grid_state=wreck_grid_state,
        wreck_id_to_grid_coord=wreck_id_to_grid_coord,
        tanker_grid_state=tanker_grid_state,
        tanker_id_to_grid_coord=tanker_id_to_grid_coord,
        enemy_reaper_grid_state=enemy_reaper_grid_state,
        enemy_reaper_id_to_grid_coord=enemy_reaper_id_to_grid_coord,
        enemy_others_grid_state=enemy_others_grid_state,
        enemy_others_id_to_grid_coord=enemy_others_id_to_grid_coord,
    )

    return game_grid_information
