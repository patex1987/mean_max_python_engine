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
    GameGridInformation,
    PlayerState,
    GRID_COORD_UNIT_STATE_T,
)
from python_prototypes.field_tools import get_grid_position
from python_prototypes.real_game_mocks.full_grid_state import ExampleBasicScenarioIncomplete
from python_prototypes.reaper.decision_maker import reaper_decider
from python_prototypes.reaper.input_to_q_state import calculate_reaper_q_state
from python_prototypes.reaper.q_orchestrator import ReaperGameState


def original_game_main():

    q_state_action_weights: dict[tuple, dict[str, float]] = {}

    # game loop
    while True:
        my_score = int(input())
        enemy_score_1 = int(input())
        enemy_score_2 = int(input())
        my_rage = int(input())
        enemy_rage_1 = int(input())
        enemy_rage_2 = int(input())
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
        player_reaper_grid_unit = None
        player_destroyer_grid_unit = None
        player_doof_grid_unit = None
        reaper_game_state = ReaperGameState()

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
                continue

            if unit_type in [Entity.DESTROYER.value, Entity.DOOF.value] and player != PlayerFieldTypes.PLAYER.value:
                enemy_others_grid_state[grid_coordinate].append(grid_unit)
                enemy_others_id_to_grid_coord[unit_id] = grid_coordinate
                continue

            if unit_type == Entity.REAPER.value and player == PlayerFieldTypes.PLAYER.value:
                player_reaper_grid_unit = grid_unit

            if unit_type == Entity.DESTROYER.value and player == PlayerFieldTypes.PLAYER.value:
                player_destroyer_grid_unit = grid_unit

            if unit_type == Entity.DOOF.value and player == PlayerFieldTypes.PLAYER.value:
                player_doof_grid_unit = grid_unit

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr, flush=True)
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

        player_state = PlayerState(
            reaper_state=player_reaper_grid_unit,
            destroyer_state=player_destroyer_grid_unit,
            doof_state=player_doof_grid_unit,
            rage=my_rage,
            score=my_score,
        )

        reaper_q_state = calculate_reaper_q_state(
            game_grid_information=game_grid_information, player_state=player_state
        )
        next_step = reaper_decider(
            reaper_game_state=reaper_game_state,
            reaper_q_state=reaper_q_state,
            game_grid_information=game_grid_information,
            player_state=player_state,
        )
        print("WAIT")
        print("WAIT")
        print("WAIT")


class TestGameInputHandler:

    def test_get_example_full_grid_state(self):
        game_grid_information = ExampleBasicScenarioIncomplete.get_example_full_grid_state()
        full_grid_state = game_grid_information.full_grid_state

        # print(full_grid_state)
        assert len(full_grid_state[(0, 0)]) == 1
        assert len(full_grid_state[(2, 0)]) == 2
        assert len(full_grid_state[(2, 2)]) == 1
        assert len(full_grid_state[(3, 2)]) == 1
        assert len(full_grid_state[(2, 3)]) == 1

        enemy_other_grid_state = game_grid_information.enemy_others_grid_state
        assert len(enemy_other_grid_state[(0, 0)]) == 1
        assert len(enemy_other_grid_state[(2, 0)]) == 1

        tanker_grid_state = game_grid_information.tanker_grid_state
        assert len(tanker_grid_state[(2, 0)]) == 1
        assert len(tanker_grid_state[(2, 2)]) == 1
