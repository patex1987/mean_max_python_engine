import uuid
from typing import Protocol

from python_prototypes.field_tools import get_manhattan_distance
from python_prototypes.field_types import PlayerState, GameGridInformation
from python_prototypes.reaper.target_selector import SelectedTargetInformation


class LongTermTracker(Protocol):

    def is_expired(self) -> bool: ...

    def get_round_gain_loss(
        self,
        player_state: PlayerState,
        enemy_1_state: PlayerState,
        enemy_2_state: PlayerState,
        game_grid_information: GameGridInformation,
    ) -> float | None: ...

    def get_tracker_id(self) -> uuid.uuid4: ...


class LongTermSuccessGains:
    harvest = 10
    harvest_decay = 0.9
    ram = 3
    move = 1


class HarvestSuccessTracker(LongTermTracker):

    def __init__(self, original_water_target: SelectedTargetInformation):
        self.max_rounds = 5
        self.tracked_rounds = 0
        self.original_wreck_target = original_water_target
        self.gain = LongTermSuccessGains.harvest
        self.decay_factor = LongTermSuccessGains.harvest_decay
        self.tracker_id = uuid.uuid4()

    def get_round_gain_loss(
        self,
        player_state: PlayerState,
        enemy_1_state: PlayerState,
        enemy_2_state: PlayerState,
        game_grid_information: GameGridInformation,
    ):
        self.tracked_rounds += 1
        if not player_state.score_gained:
            return None
        wreck_exists = self.original_wreck_target.id in game_grid_information.wreck_id_to_grid_coord
        if not wreck_exists:
            return None
        wreck_coordinate = game_grid_information.wreck_id_to_grid_coord[self.original_wreck_target.id]
        original_wreck_distance = get_manhattan_distance(
            coordinate_a=player_state.reaper_state.grid_coordinate,
            coordinate_b=wreck_coordinate,
        )
        if original_wreck_distance != 0:
            return None
        return self._calculate_gain_loss()

    def is_expired(self) -> bool:
        if self.tracked_rounds >= self.max_rounds:
            return True
        return False

    def get_tracker_id(self) -> uuid.uuid4:
        return self.tracker_id

    def _calculate_gain_loss(self) -> float:
        return self.gain * (self.decay_factor**self.tracked_rounds)
