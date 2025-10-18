import uuid
from typing import Protocol

from python_prototypes.field_tools import get_manhattan_distance
from python_prototypes.field_types import PlayerState, GameGridInformation, PlayerFieldTypes
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
    ram = 5
    ram_decay = 0.9
    move = 1


class HarvestSuccessTracker(LongTermTracker):
    """
    Get a decayed reward every time the player's score increased (water sucked)
    from the originally targeted water wreck

    Tracked for 5 rounds
    """

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
    ) -> float | None:
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


class RamReaperSuccessTracker(LongTermTracker):
    """
    If the rammed enemy reaper (the target) is not able to suck water (i.e.
    gain water score) for max_rounds (5), then it gets rewarded for the full
    amount of points. Otherwise, it gets decayed
    """

    def __init__(self, original_reaper_target: SelectedTargetInformation):
        self.max_rounds = 5
        self.tracked_rounds = 0
        self.original_reaper_target = original_reaper_target
        self.gain = LongTermSuccessGains.ram
        self.decay = LongTermSuccessGains.ram_decay
        self.tracker_id = uuid.uuid4()
        self._should_expire = False

    def get_round_gain_loss(
        self,
        player_state: PlayerState,
        enemy_1_state: PlayerState,
        enemy_2_state: PlayerState,
        game_grid_information: GameGridInformation,
    ) -> float | None:
        if self.original_reaper_target.player_id == PlayerFieldTypes.ENEMY_1.value:
            enemy_state = enemy_1_state
        elif self.original_reaper_target.player_id == PlayerFieldTypes.ENEMY_2.value:
            enemy_state = enemy_2_state
        else:
            self._should_expire = True
            return None

        if enemy_state.reaper_state.unit.unit_id != self.original_reaper_target.id:
            raise ValueError("Tracking the wrong item here")

        if enemy_state.score_gained >= 0:
            self._should_expire = True
            if self.tracked_rounds == 0:
                return None
            score = self._calculate_gain_loss()
            return float(score)

        if self.tracked_rounds == self.max_rounds - 1:
            return self.gain

        self.tracked_rounds += 1
        return self._calculate_gain_loss()

    def is_expired(self) -> bool:
        if self._should_expire:
            return True
        if self.tracked_rounds >= self.max_rounds:
            return True
        return False

    def get_tracker_id(self) -> uuid.uuid4:
        return self.tracker_id

    def _calculate_gain_loss(self) -> float:
        if self.tracked_rounds == 0:
            return 0.0
        return self.gain * self.decay ** (self.max_rounds - self.tracked_rounds)
