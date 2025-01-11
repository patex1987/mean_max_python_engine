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
    PlayerState,
)


class ExampleBasicScenarioIncomplete:
    enemy_1_destroyer = Unit(
        unit_type=Entity.DESTROYER.value,
        x=200,
        y=200,
        vx=0,
        vy=0,
        radius=30,
        unit_id=1,
        mass=10,
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
        mass=10,
        player=PlayerFieldTypes.ENEMY_2.value,
    )
    tanker_1 = Unit(
        unit_type=Entity.TANKER.value,
        x=2800,
        y=400,
        vx=-0.98994,
        vy=-0.141421,
        radius=30,
        unit_id=3,
        player=PlayerFieldTypes.ENEMY_1.value,
        mass=20,
    )
    tanker_2 = Unit(
        unit_type=Entity.TANKER.value,
        x=2800,
        y=2600,
        vx=-0.707,
        vy=-0.707,
        radius=30,
        unit_id=4,
        player=PlayerFieldTypes.ENEMY_2.value,
        mass=20,
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
        mass=10,
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
        mass=20,
    )
    player_reaper = Unit(
        unit_type=Entity.REAPER.value,
        x=3800,
        y=3800,
        vx=0,
        vy=0,
        radius=30,
        unit_id=7,
        player=PlayerFieldTypes.PLAYER.value,
        mass=30,
    )

    @classmethod
    def get_example_full_grid_state(cls):

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
            cls.enemy_1_destroyer,
            cls.enemy_2_destroyer,
            cls.tanker_1,
            cls.tanker_2,
            cls.player_doof,
            cls.player_destroyer,
            cls.player_reaper,
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

    @classmethod
    def get_example_player_state(cls):

        player_reaper_unit = cls.player_reaper
        player_reaper_position = get_grid_position(coordinate=(player_reaper_unit.x, player_reaper_unit.y))
        reaper_grid_unit = GridUnitState(player_reaper_position, player_reaper_unit)

        player_destroyer_unit = cls.player_destroyer
        player_destroyer_position = get_grid_position(coordinate=(player_destroyer_unit.x, player_destroyer_unit.y))
        destroyer_grid_unit = GridUnitState(player_destroyer_position, player_destroyer_unit)

        player_doof_unit = cls.player_doof
        player_doof_position = get_grid_position(coordinate=(player_doof_unit.x, player_doof_unit.y))
        doof_grid_unit = GridUnitState(player_doof_position, player_doof_unit)

        return PlayerState(
            reaper_state=reaper_grid_unit,
            destroyer_state=destroyer_grid_unit,
            doof_state=doof_grid_unit,
            rage=0,
            score=0,
        )
