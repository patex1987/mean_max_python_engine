"""
This is where we interface with the main entry of the game
We need to be consistent with the actual codingame inputs
This module should contain some simulation and/or testing capabilities
that emulates a "real" game input
"""

from collections import defaultdict
from typing import Any

from python_prototypes.field_types import (
    Unit,
    GridUnitState,
    Entity,
    PlayerFieldTypes,
    GRID_COORD_UNIT_STATE_T,
)
from python_prototypes.field_tools import get_grid_position
from python_prototypes.main_game_engine import MainGameEngine
from python_prototypes.reaper.q_orchestrator import ReaperGameState


def original_game_main():

    # q_state_action_weights: dict[tuple, dict[str, float]] = {}
    reaper_game_state = ReaperGameState()
    main_game_engine = MainGameEngine(reaper_game_state)

    # game loop
    while True:
        my_score = int(input())
        enemy_1_score = int(input())
        enemy_2_score = int(input())
        my_rage = int(input())
        enemy_1_rage = int(input())
        enemy_2_rage = int(input())
        unit_count = int(input())

        full_grid_state: GRID_COORD_UNIT_STATE_T = defaultdict(list)
        wreck_grid_state: GRID_COORD_UNIT_STATE_T = defaultdict(list)
        wreck_id_to_grid_coord: dict[Any, tuple[int, int]] = {}
        tanker_grid_state: GRID_COORD_UNIT_STATE_T = defaultdict(list)
        tanker_id_to_grid_coord: dict[Any, tuple[int, int]] = {}
        enemy_reaper_grid_state: GRID_COORD_UNIT_STATE_T = defaultdict(list)
        enemy_reaper_id_to_grid_coord: dict[Any, tuple[int, int]] = {}
        enemy_others_grid_state: GRID_COORD_UNIT_STATE_T = defaultdict(list)
        enemy_others_id_to_grid_coord: dict[Any, tuple[int, int]] = {}
        player_reaper_grid_unit: GridUnitState | None = None
        player_destroyer_grid_unit: GridUnitState | None = None
        player_doof_grid_unit: GridUnitState | None = None
        enemy_id_to_entities: dict[int, dict[Entity, GridUnitState]] = defaultdict(dict)

        for i in range(unit_count):
            inputs = input().split()
            unit_id = int(inputs[0])
            unit_type = int(inputs[1])
            player = int(inputs[2])
            mass = float(inputs[3])
            radius = int(inputs[4])
            x = int(inputs[5])
            y = int(inputs[6])
            vx = int(inputs[7])
            vy = int(inputs[8])
            extra = int(inputs[9])
            extra_2 = int(inputs[10])

            unit = Unit(
                unit_id=unit_id,
                unit_type=unit_type,
                player=player,
                radius=radius,
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                mass=mass,
                extra=extra,
                extra_2=extra_2,
            )
            grid_coordinate = get_grid_position(coordinate=(x, y))
            grid_unit = GridUnitState(
                grid_coordinate=grid_coordinate,
                unit=unit,
            )
            full_grid_state[grid_coordinate].append(grid_unit)

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

                enemy_id_to_entities[player][Entity.REAPER] = grid_unit
                continue

            if unit_type in [Entity.DESTROYER.value, Entity.DOOF.value] and player != PlayerFieldTypes.PLAYER.value:
                enemy_others_grid_state[grid_coordinate].append(grid_unit)
                enemy_others_id_to_grid_coord[unit_id] = grid_coordinate

                enemy_id_to_entities[player][Entity(unit_type)] = grid_unit
                continue

            if unit_type == Entity.REAPER.value and player == PlayerFieldTypes.PLAYER.value:
                player_reaper_grid_unit = grid_unit

            if unit_type == Entity.DESTROYER.value and player == PlayerFieldTypes.PLAYER.value:
                player_destroyer_grid_unit = grid_unit

            if unit_type == Entity.DOOF.value and player == PlayerFieldTypes.PLAYER.value:
                player_doof_grid_unit = grid_unit

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr, flush=True)
        main_game_engine.run_round_raw(
            enemy_others_grid_state,
            enemy_others_id_to_grid_coord,
            enemy_reaper_grid_state,
            enemy_reaper_id_to_grid_coord,
            full_grid_state,
            my_rage,
            my_score,
            player_destroyer_grid_unit,
            player_doof_grid_unit,
            player_reaper_grid_unit,
            tanker_grid_state,
            tanker_id_to_grid_coord,
            wreck_grid_state,
            wreck_id_to_grid_coord,
            enemy_id_to_entities,
            enemy_1_score,
            enemy_2_score,
            enemy_1_rage,
            enemy_2_rage,
        )

        print("WAIT")
        print("WAIT")
        print("WAIT")
