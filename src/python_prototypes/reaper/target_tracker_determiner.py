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


def get_target_tracker(reaper_goal_type: ReaperActionTypes) -> "BaseTracker":
    """
    :param reaper_goal_type:
    :return:

    TODO: use the manhattan distances to speed up lookups, and calculate
            euclidean distance only on demand
    """

    match reaper_goal_type:
        case ReaperActionTypes.harvest_safe:
            return StaticTargetTracker()
        case ReaperActionTypes.harvest_risky:
            return StaticTargetTracker()
        case ReaperActionTypes.harvest_dangerous:
            return StaticTargetTracker()
        case ReaperActionTypes.ram_reaper_close:
            return DynamicTargetTracker()
        case ReaperActionTypes.ram_reaper_medium:
            return DynamicTargetTracker()
        case ReaperActionTypes.ram_reaper_far:
            return DynamicTargetTracker()
        case ReaperActionTypes.ram_other_close:
            return DynamicTargetTracker()
        case ReaperActionTypes.ram_other_medium:
            return DynamicTargetTracker()
        case ReaperActionTypes.ram_other_far:
            return DynamicTargetTracker()
        case ReaperActionTypes.use_super_power:
            return RoundCountTracker()
        case ReaperActionTypes.wait:
            return RoundCountTracker()
        case ReaperActionTypes.move_tanker_safe:
            return DynamicTargetTracker()
        case ReaperActionTypes.move_tanker_risky:
            return DynamicTargetTracker()
        case ReaperActionTypes.move_tanker_dangerous:
            return DynamicTargetTracker()
        case _:
            raise ValueError(f"Invalid goal type: {reaper_goal_type}")


class BaseTracker(ABC):
    @abstractmethod
    def track(self, player_reaper_unit: GridUnitState, target_unit: GridUnitState):
        """
        :param player_reaper_unit:
        :param target_unit:
        :return:

        TODO: change the type of target_unit, it can be None
        """
        pass

    @property
    @abstractmethod
    def steps_taken(self):
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

    @abstractmethod
    def is_player_faster_than_target(self) -> bool:
        pass

    @abstractmethod
    def is_player_higher_energy(self) -> bool:
        """
        TODO: remove it, because most probably it will be never used and will be deprecated
        :return:
        """
        pass

    @abstractmethod
    def is_player_higher_momentum(self) -> bool:
        pass

    @abstractmethod
    def is_moving_towards_target(self) -> bool:
        pass

    @abstractmethod
    def is_within_collision_radius(self) -> bool:
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
            (player_reaper_unit.unit.x, player_reaper_unit.unit.y),
            (target_unit.unit.x, target_unit.unit.y),
        )
        self.euclidean_distances_from_target.append(euclidean_distance)
        if len(self.euclidean_distances_from_target) > 1:
            self.euclidean_distance_changes.append(euclidean_distance - self.euclidean_distances_from_target[-2])

    @property
    def steps_taken(self):
        return len(self.manhattan_distances_from_target)

    def is_distance_growing(self, round_threshold: int) -> bool:
        if round_threshold < 2:
            return False
        if len(self.manhattan_distance_changes) < round_threshold:
            return False
        last_n_changes = self.euclidean_distance_changes[-round_threshold:]
        is_growing = any(
            map(
                lambda pair: pair[0] > pair[1],
                zip(last_n_changes[1:], last_n_changes[:-1]),
            )
        )
        return is_growing

    def total_round_threshold_breached(self, round_threshold: int) -> bool:
        return len(self.manhattan_distance_changes) >= round_threshold

    def actual_distance(self) -> float:
        return self.manhattan_distances_from_target[-1]

    def is_target_within_threshold(self, threshold: float) -> bool:
        return self.manhattan_distances_from_target[-1] <= threshold

    def is_player_faster_than_target(self) -> bool:
        return True

    def is_player_higher_energy(self) -> bool:
        return True

    def is_player_higher_momentum(self) -> bool:
        return True

    def is_moving_towards_target(self) -> bool:
        return True

    def is_within_collision_radius(self) -> bool:
        return True


class DynamicTargetTracker(BaseTracker):
    def __init__(self):
        self.manhattan_distances_from_target = []
        self.manhattan_distance_changes = []
        self.euclidean_distances_from_target = []
        self.euclidean_distance_changes = []
        self.dx_vectors = []
        self.dy_vectors = []
        self.player_speed_vectors: list[tuple[int, int]] = []
        self.player_speed_changes = []
        self.target_speed_vectors: list[tuple[int, int]] = []
        self.target_speed_changes = []
        self.player_mass = None
        self.target_mass = None
        self.player_radius = None
        self.target_radius = None

    def track(self, player_reaper_unit: GridUnitState, target_unit: GridUnitState):
        manhattan_distance = get_manhattan_distance(player_reaper_unit.grid_coordinate, target_unit.grid_coordinate)
        self.manhattan_distances_from_target.append(manhattan_distance)
        if len(self.manhattan_distances_from_target) > 1:
            self.manhattan_distance_changes.append(manhattan_distance - self.manhattan_distances_from_target[-2])

        euclidean_distance = get_euclidean_distance(
            (player_reaper_unit.unit.x, player_reaper_unit.unit.y),
            (target_unit.unit.x, target_unit.unit.y),
        )
        self.euclidean_distances_from_target.append(euclidean_distance)
        if len(self.euclidean_distances_from_target) > 1:
            self.euclidean_distance_changes.append(euclidean_distance - self.euclidean_distances_from_target[-2])

        self.dx_vectors.append(target_unit.unit.x - player_reaper_unit.unit.x)
        self.dy_vectors.append(target_unit.unit.y - player_reaper_unit.unit.y)

        self.player_speed_vectors.append((player_reaper_unit.unit.vx, player_reaper_unit.unit.vy))
        if len(self.euclidean_distances_from_target) > 1:
            self.player_speed_changes.append(
                (
                    player_reaper_unit.unit.vx - self.player_speed_vectors[-2][0],
                    player_reaper_unit.unit.vy - self.player_speed_vectors[-2][1],
                )
            )

        self.target_speed_vectors.append((target_unit.unit.vx, target_unit.unit.vy))
        if len(self.euclidean_distances_from_target) > 1:
            self.target_speed_changes.append(
                (
                    target_unit.unit.vx - self.target_speed_vectors[-2][0],
                    target_unit.unit.vx - self.target_speed_vectors[-2][0],
                )
            )

        self.player_mass = player_reaper_unit.unit.mass
        self.target_mass = target_unit.unit.mass
        self.player_radius = player_reaper_unit.unit.radius
        self.target_radius = target_unit.unit.radius

    @property
    def steps_taken(self):
        return len(self.manhattan_distances_from_target)

    def is_distance_growing(self, round_threshold: int) -> bool:
        if round_threshold < 2:
            return False
        if len(self.manhattan_distance_changes) < round_threshold:
            return False
        last_n_changes = self.euclidean_distance_changes[-round_threshold:]
        is_growing = any(
            map(
                lambda pair: pair[0] > pair[1],
                zip(last_n_changes[1:], last_n_changes[:-1]),
            )
        )
        return is_growing

    def total_round_threshold_breached(self, round_threshold: int) -> bool:
        return len(self.manhattan_distance_changes) >= round_threshold

    def actual_distance(self) -> float:
        return self.euclidean_distances_from_target[-1]

    def is_target_within_threshold(self, threshold: float) -> bool:
        return self.euclidean_distances_from_target[-1] <= threshold

    def is_player_faster_than_target(self) -> bool:
        player_latest_speed = self.player_speed_vectors[-1]
        target_latest_speed = self.target_speed_vectors[-1]
        magnitude_player = (player_latest_speed[0] ** 2 + player_latest_speed[1] ** 2) ** 0.5
        magnitude_target = (target_latest_speed[0] ** 2 + target_latest_speed[1] ** 2) ** 0.5

        return magnitude_player > magnitude_target

    def is_player_higher_energy(self) -> bool:
        player_latest_speed = self.player_speed_vectors[-1]
        target_latest_speed = self.target_speed_vectors[-1]
        magnitude_player = (player_latest_speed[0] ** 2 + player_latest_speed[1] ** 2) ** 0.5
        magnitude_target = (target_latest_speed[0] ** 2 + target_latest_speed[1] ** 2) ** 0.5

        player_energy = 0.5 * self.player_mass * magnitude_player**2
        target_energy = 0.5 * self.target_mass * magnitude_target**2

        return player_energy > target_energy

    def is_player_higher_momentum(self) -> bool:
        """
        :return:

        TODO: create functions for these functionalities, as they can
            be potentially reused elsewhere
        """
        player_latest_speed = self.player_speed_vectors[-1]
        target_latest_speed = self.target_speed_vectors[-1]
        magnitude_player = (player_latest_speed[0] ** 2 + player_latest_speed[1] ** 2) ** 0.5
        magnitude_target = (target_latest_speed[0] ** 2 + target_latest_speed[1] ** 2) ** 0.5

        player_momentum = self.player_mass * magnitude_player
        target_momentum = self.target_mass * magnitude_target

        return player_momentum > target_momentum

    def is_moving_towards_target(self) -> bool:
        actual_dx = self.dx_vectors[-1]
        actual_dy = self.dy_vectors[-1]
        player_latest_speed = self.player_speed_vectors[-1]
        target_latest_speed = self.target_speed_vectors[-1]

        relative_velocity = (
            target_latest_speed[0] - player_latest_speed[0],
            target_latest_speed[1] - player_latest_speed[1],
        )

        dot_product = (relative_velocity[0] * actual_dx) + (relative_velocity[1] * actual_dy)
        if dot_product >= 0:
            return False

        return True

    def is_within_collision_radius(self) -> bool:
        collision_radius = self.player_radius + self.target_radius
        return self.is_target_within_threshold(collision_radius)


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

    def is_player_faster_than_target(self) -> bool:
        return True

    def is_player_higher_energy(self) -> bool:
        return True

    def is_player_higher_momentum(self) -> bool:
        return True

    def is_moving_towards_target(self) -> bool:
        return True

    def is_within_collision_radius(self) -> bool:
        return True


class RoundCountTracker(BaseTracker):
    def __init__(self):
        self._round_count = 0

    def track(self, player_reaper_unit: GridUnitState, target_unit: GridUnitState):
        self._round_count += 1

    @property
    def steps_taken(self):
        return self._round_count

    def is_distance_growing(self, round_threshold: int) -> bool:
        return True

    def total_round_threshold_breached(self, round_threshold: int) -> bool:
        return True

    def actual_distance(self) -> float:
        return 0.0

    def is_target_within_threshold(self, threshold: float) -> bool:
        return True

    def is_player_faster_than_target(self) -> bool:
        return True

    def is_player_higher_energy(self) -> bool:
        return True

    def is_player_higher_momentum(self) -> bool:
        return True

    def is_moving_towards_target(self) -> bool:
        return True

    def is_within_collision_radius(self) -> bool:
        return True
