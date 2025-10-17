"""
TODO: these can be later moved to some sort of test suite (most probably conftest.py)
"""

from collections import defaultdict
from typing import Any

from python_prototypes.destroyer_simulation import Coordinate
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


class ReaperAndWreckOnlyScenario:
    """
    There is only a player's reaper and a wreck, useful
    to test the long term gains from harvest success tracker
    """

    def __init__(self, wreck: Unit | None, player_reaper: Unit | None):
        if not wreck:
            wreck = Unit(
                unit_type=Entity.WRECK.value,
                x=1400,
                y=1400,
                vx=0,
                vy=0,
                radius=30,
                unit_id=1,
                mass=10,
                player=None,
            )
        if not player_reaper:
            player_reaper = Unit(
                unit_type=Entity.REAPER.value,
                x=500,
                y=1400,
                vx=0,
                vy=0,
                radius=30,
                unit_id=7,
                player=PlayerFieldTypes.PLAYER.value,
                mass=30,
            )
        self.wreck = wreck
        self.player_reaper = player_reaper

    @classmethod
    def create_with_coordinates(
        cls, wreck_coordinate: Coordinate, reaper_coordinate: Coordinate
    ) -> 'ReaperAndWreckOnlyScenario':
        wreck = Unit(
            unit_type=Entity.WRECK.value,
            x=wreck_coordinate.x,
            y=wreck_coordinate.y,
            vx=0,
            vy=0,
            radius=30,
            unit_id=1,
            mass=10,
            player=None,
        )
        player_reaper = Unit(
            unit_type=Entity.REAPER.value,
            x=reaper_coordinate.x,
            y=reaper_coordinate.y,
            vx=0,
            vy=0,
            radius=30,
            unit_id=7,
            player=PlayerFieldTypes.PLAYER.value,
            mass=30,
        )
        return cls(wreck=wreck, player_reaper=player_reaper)

    def get_full_grid_state(self) -> GameGridInformation:

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
            self.wreck,
            self.player_reaper,
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

    def get_player_state(self, water_gain: int | None = None) -> PlayerState:
        """
        Gets the player state and fakes its water gain to the provided level.

        Used to emulate a game round's player state, where the water gain is
        at the desired level

        :param water_gain:
        :return:
        """

        player_reaper_unit = self.player_reaper
        player_reaper_position = get_grid_position(coordinate=(player_reaper_unit.x, player_reaper_unit.y))
        reaper_grid_unit = GridUnitState(player_reaper_position, player_reaper_unit)

        fake_destroyer_state = GridUnitState((0, 0), Unit(0, 0, 0, 0, 0, 0, 0, PlayerFieldTypes.PLAYER.value))
        fake_doof_state = GridUnitState((0, 0), Unit(0, 0, 0, 0, 0, 0, 0, PlayerFieldTypes.PLAYER.value))

        fake_player_state = PlayerState(
            reaper_state=reaper_grid_unit,
            destroyer_state=fake_destroyer_state,
            doof_state=fake_doof_state,
            rage=0,
            score=0,
            prev_rage=None,
            prev_score=None,
        )
        fake_player_state.score_gained = water_gain
        return fake_player_state
