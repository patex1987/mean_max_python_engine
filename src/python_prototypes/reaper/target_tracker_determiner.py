"""
Trackers are the object that track the effect of a strategy
i.e. the tracks the changes between rounds, and decision about the
effectiveness / result of the strategy can be decided based on that
information
"""

from abc import ABC, abstractmethod

from python_prototypes.field_tools import get_manhattan_distance, get_euclidean_distance
from python_prototypes.field_types import GridUnitState
from python_prototypes.reaper.q_state_types import ReaperActionTypes


def get_target_tracker(reaper_goal_type: ReaperActionTypes) -> 'BaseTracker':
    match reaper_goal_type:
        case ReaperActionTypes.harvest_safe:
            return StaticTargetTracker()
        case ReaperActionTypes.harvest_risky:
            return StaticTargetTracker()
        case ReaperActionTypes.harvest_dangerous:
            return StaticTargetTracker()
        case ReaperActionTypes.ram_reaper_close:
            return DynamicTargetTracker()
        case ReaperActionTypes.ram_reaper_mid:
            return DynamicTargetTracker()
        case ReaperActionTypes.ram_reaper_far:
            return DynamicTargetTracker()
        case ReaperActionTypes.ram_other_close:
            return DynamicTargetTracker()
        case ReaperActionTypes.ram_other_mid:
            return DynamicTargetTracker()
        case ReaperActionTypes.ram_other_far:
            return DynamicTargetTracker()
        case ReaperActionTypes.use_super_power:
            return NoOpTracker()
        case ReaperActionTypes.wait:
            return NoOpTracker()
        case ReaperActionTypes.move_tanker_safe:
            return DynamicTargetTracker()
        case ReaperActionTypes.move_tanker_risky:
            return DynamicTargetTracker()
        case ReaperActionTypes.move_tanker_dangerous:
            return DynamicTargetTracker()
        case _:
            raise ValueError(f'Invalid goal type: {reaper_goal_type}')


class BaseTracker(ABC):

    @abstractmethod
    def track(self, player_reaper_unit: GridUnitState, target_unit: GridUnitState):
        pass

    @abstractmethod
    def total_round_threshold_breached(self, round_threshold: int) -> bool:
        pass

    @abstractmethod
    def is_distance_growing(self, round_threshold: int) -> bool:
        pass

    @abstractmethod
    def actual_distance(self) -> float:
        pass

    @abstractmethod
    def is_target_within_threshold(self, threshold: float) -> bool:
        pass


class StaticTargetTracker(BaseTracker):

    def __init__(self):
        self.manhattan_distances_from_target = []
        self.manhattan_distance_changes = []
        self.euclidean_distances_from_target = []
        self.euclidean_distance_changes = []

    def track(self, player_reaper_unit: GridUnitState, target_unit: GridUnitState):
        manhattan_distance = get_manhattan_distance(player_reaper_unit.grid_coordinate, target_unit.grid_coordinate)
        self.manhattan_distances_from_target.append(manhattan_distance)
        if len(self.manhattan_distances_from_target) > 1:
            self.manhattan_distance_changes.append(manhattan_distance - self.manhattan_distances_from_target[-2])

        euclidean_distance = get_euclidean_distance(
            (player_reaper_unit.unit.x, player_reaper_unit.unit.y), (target_unit.unit.x, target_unit.unit.y)
        )
        self.euclidean_distances_from_target.append(euclidean_distance)
        if len(self.euclidean_distances_from_target) > 1:
            self.euclidean_distance_changes.append(euclidean_distance - self.euclidean_distances_from_target[-2])

    @property
    def steps_taken(self):
        return len(self.manhattan_distances_from_target)

    def is_distance_growing(self, round_threshold: int) -> bool:
        if len(self.manhattan_distance_changes) < round_threshold:
            return False
        last_n_changes = self.euclidean_distance_changes[:-round_threshold]
        is_growing = all(x >= 0 for x in last_n_changes)
        return is_growing

    def total_round_threshold_breached(self, round_threshold: int) -> bool:
        return len(self.manhattan_distance_changes) >= round_threshold

    def actual_distance(self) -> float:
        return self.manhattan_distances_from_target[-1]

    def is_target_within_threshold(self, threshold: float) -> bool:
        return self.manhattan_distances_from_target[-1] <= threshold


class DynamicTargetTracker(BaseTracker):
    """
    TODO: right now this is the same as the static one, we will change it later
    """

    def __init__(self):
        self.manhattan_distances_from_target = []
        self.manhattan_distance_changes = []
        self.euclidean_distances_from_target = []
        self.euclidean_distance_changes = []

    def track(self, player_reaper_unit: GridUnitState, target_unit: GridUnitState):
        manhattan_distance = get_manhattan_distance(player_reaper_unit.grid_coordinate, target_unit.grid_coordinate)
        self.manhattan_distances_from_target.append(manhattan_distance)
        if len(self.manhattan_distances_from_target) > 1:
            self.manhattan_distance_changes.append(manhattan_distance - self.manhattan_distances_from_target[-2])

        euclidean_distance = get_euclidean_distance(
            (player_reaper_unit.unit.x, player_reaper_unit.unit.y), (target_unit.unit.x, target_unit.unit.y)
        )
        self.euclidean_distances_from_target.append(euclidean_distance)
        if len(self.euclidean_distances_from_target) > 1:
            self.euclidean_distance_changes.append(euclidean_distance - self.euclidean_distances_from_target[-2])

    @property
    def steps_taken(self):
        return len(self.manhattan_distances_from_target)

    def is_distance_growing(self, round_threshold: int) -> bool:
        if len(self.manhattan_distance_changes) < round_threshold:
            return False
        last_n_changes = self.euclidean_distance_changes[:-round_threshold]
        is_growing = all(x >= 0 for x in last_n_changes)
        return is_growing

    def total_round_threshold_breached(self, round_threshold: int) -> bool:
        return len(self.manhattan_distance_changes) >= round_threshold

    def actual_distance(self) -> float:
        return self.manhattan_distances_from_target[-1]

    def is_target_within_threshold(self, threshold: float) -> bool:
        return self.manhattan_distances_from_target[-1] <= threshold


class NoOpTracker(BaseTracker):
    def track(self, player_reaper_unit: GridUnitState, target_unit: GridUnitState):
        pass

    @property
    def steps_taken(self):
        return 0

    def is_distance_growing(self, round_threshold: int) -> bool:
        return True

    def total_round_threshold_breached(self, round_threshold: int) -> bool:
        return True

    def actual_distance(self) -> float:
        return 0.0

    def is_target_within_threshold(self, threshold: float) -> bool:
        return True
