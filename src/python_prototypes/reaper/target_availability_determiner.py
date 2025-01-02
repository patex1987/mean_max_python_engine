from enum import Enum
from functools import partial
from typing import Callable, Any

from python_prototypes.field_types import GridUnitState, GRID_COORD_UNIT_STATE_T, GameGridInformation, Entity
from python_prototypes.reaper.q_state_types import ReaperActionTypes
from python_prototypes.reaper.target_tracker_determiner import BaseTracker


class TargetAvailabilityState(Enum):
    valid = 1
    invalid = 2
    replan_reach = 3
    goal_reached_success = 4


def get_goal_target_determiner(
    current_goal_type: ReaperActionTypes,
) -> Callable[[GridUnitState | None, GameGridInformation, BaseTracker], TargetAvailabilityState]:
    """

    :param current_goal_type:
    :return:
        TODO: consider changing the signature of the callables,
            [GridUnitState, GameGridInformation, BaseTracker]
            if you add the GridUnitState of the player, then you can
            calculate everything directly in the callables, won't be needed
            to store that much information in the Tracker object
    """
    match current_goal_type:
        case ReaperActionTypes.harvest_safe:
            return water_target_available
        case ReaperActionTypes.harvest_risky:
            return water_target_available
        case ReaperActionTypes.harvest_dangerous:
            return water_target_available
        case ReaperActionTypes.ram_reaper_close:
            return ram_target_obj_available
        case ReaperActionTypes.ram_reaper_mid:
            return ram_target_obj_available
        case ReaperActionTypes.ram_reaper_far:
            return ram_target_obj_available
        case ReaperActionTypes.ram_other_close:
            return ram_target_obj_available
        case ReaperActionTypes.ram_other_mid:
            return ram_target_obj_available
        case ReaperActionTypes.ram_other_far:
            return ram_target_obj_available
        case ReaperActionTypes.use_super_power:
            return super_power_target_available
        case ReaperActionTypes.wait:
            return partial(round_count_target_available, round_limit=1)
        case ReaperActionTypes.move_tanker_safe:
            return tanker_target_available
        case ReaperActionTypes.move_tanker_risky:
            return tanker_target_available
        case ReaperActionTypes.move_tanker_dangerous:
            return tanker_target_available
        case _:
            raise ValueError(f'Invalid goal type: {current_goal_type}')


def water_target_available(
    goal_target_obj: GridUnitState | None, game_grid_information: GameGridInformation, target_tracker: BaseTracker
) -> TargetAvailabilityState:
    """
    :param goal_target_obj:
    :param game_grid_information:
    :param target_tracker:
    :return:

    TODO: water is within wrecks
    """
    if goal_target_obj is None:
        return TargetAvailabilityState.invalid

    wreck_id = goal_target_obj.unit.unit_id
    wreck_coordinate = goal_target_obj.grid_coordinate

    if not game_grid_information.wreck_id_to_grid_coord:
        return TargetAvailabilityState.invalid

    if wreck_id not in game_grid_information.wreck_id_to_grid_coord:
        return TargetAvailabilityState.invalid

    # TODO: move these to some constants, so they are easily configurable
    replan_round_threshold = 3
    total_round_threshold = 10
    target_distance_threshold = 25  # not sure about this, depends on the radius of the wreck

    if target_tracker.total_round_threshold_breached(total_round_threshold):
        return TargetAvailabilityState.invalid

    if target_tracker.is_distance_growing(replan_round_threshold):
        return TargetAvailabilityState.replan_reach

    if not target_tracker.is_target_within_threshold(target_distance_threshold):
        return TargetAvailabilityState.goal_reached_success

    return TargetAvailabilityState.valid


def ram_target_obj_available(
    goal_target_obj: GridUnitState | None, game_grid_information: GameGridInformation, target_tracker: BaseTracker
) -> TargetAvailabilityState:
    """

    :param goal_target_obj:
    :param game_grid_information:
    :param target_tracker:
    :return:
    """
    if goal_target_obj is None:
        return TargetAvailabilityState.invalid
    enemy_target_id = goal_target_obj.unit.unit_id
    enemy_target_coordinate = goal_target_obj.grid_coordinate

    match Entity(goal_target_obj.unit.unit_type):
        case Entity.REAPER:
            if enemy_target_id not in game_grid_information.enemy_reaper_id_to_grid_coord:
                return TargetAvailabilityState.invalid
        case Entity.DESTROYER:
            if enemy_target_id not in game_grid_information.enemy_others_id_to_grid_coord:
                return TargetAvailabilityState.invalid
        case Entity.DOOF:
            if enemy_target_id not in game_grid_information.enemy_others_id_to_grid_coord:
                return TargetAvailabilityState.invalid
        case _:
            return TargetAvailabilityState.invalid

    # TODO: move this to a dedicated configuration
    # need to replan on every round, as the target object is moving
    replan_round_threshold = 1
    total_round_threshold = 10
    target_ram_distance_threshold = 25  # not sure about this, depends on the radius of the enemy reaper
    target_speed_check_threshold = 30 * target_ram_distance_threshold

    if target_tracker.total_round_threshold_breached(total_round_threshold):
        return TargetAvailabilityState.invalid

    if target_tracker.is_distance_growing(replan_round_threshold):
        return TargetAvailabilityState.replan_reach

    within_collision_threshold = target_tracker.is_within_collision_radius()
    if not within_collision_threshold:
        if not target_tracker.is_moving_towards_target():
            return TargetAvailabilityState.valid
        return TargetAvailabilityState.replan_reach

    moving_towards_target = target_tracker.is_moving_towards_target()
    if not moving_towards_target:
        return TargetAvailabilityState.invalid

    player_higher_momentum = target_tracker.is_player_higher_momentum()
    if not player_higher_momentum:
        return TargetAvailabilityState.invalid

    return TargetAvailabilityState.goal_reached_success


def super_power_target_available(
    goal_target_obj: GridUnitState | None, game_grid_information: GameGridInformation, target_tracker: BaseTracker
) -> TargetAvailabilityState:
    if goal_target_obj is None:
        return TargetAvailabilityState.invalid
    target_obj_id = goal_target_obj.unit.unit_id
    enemy_target_coordinate = goal_target_obj.grid_coordinate

    target_obj_type_raw = goal_target_obj.unit.unit_type
    target_obj_type = Entity[target_obj_type_raw]

    match target_obj_type:
        case Entity.REAPER:
            if target_obj_id not in game_grid_information.enemy_reaper_id_to_grid_coord:
                return TargetAvailabilityState.invalid
            return TargetAvailabilityState.goal_reached_success
        case Entity.OTHER_ENEMY:
            if target_obj_id not in game_grid_information.enemy_others_id_to_grid_coord:
                return TargetAvailabilityState.invalid
            return TargetAvailabilityState.goal_reached_success
        case _:
            return TargetAvailabilityState.invalid


def tanker_target_available(
    goal_target_obj: GridUnitState | None, game_grid_information: GameGridInformation, target_tracker: BaseTracker
) -> TargetAvailabilityState:
    """
    :param goal_target_obj:
    :param game_grid_information:
    :param target_tracker:
    :return:

    TODO: we need somehow detect when a tanker turned into a wreck
    """
    if goal_target_obj is None:
        return TargetAvailabilityState.invalid
    tanker_id = goal_target_obj.unit.unit_id
    tanker_coordinate = goal_target_obj.grid_coordinate

    if not game_grid_information.tanker_id_to_grid_coord:
        return TargetAvailabilityState.invalid

    if tanker_id not in game_grid_information.tanker_id_to_grid_coord:
        return TargetAvailabilityState.invalid

    # TODO: move these to some constants, so they are easily configurable
    replan_round_threshold = 3
    total_round_threshold = 15
    target_distance_threshold = 50  # not sure about this, depends on the radius of the tanker

    if target_tracker.total_round_threshold_breached(total_round_threshold):
        return TargetAvailabilityState.invalid

    if target_tracker.is_distance_growing(replan_round_threshold):
        return TargetAvailabilityState.replan_reach

    # TODO: see the TODO above in the docstring, we need to find a way if
    #  a tanker turned into a wreck
    if target_tracker.is_target_within_threshold(target_distance_threshold):
        return TargetAvailabilityState.goal_reached_success

    return TargetAvailabilityState.valid


def no_op_target_available(
    goal_target_obj: GridUnitState | None, game_grid_information: GameGridInformation, target_tracker: BaseTracker
) -> TargetAvailabilityState:
    """

    :param goal_target_obj:
    :param game_grid_information:
    :param target_tracker:
    :return:
    """
    return TargetAvailabilityState.valid


def round_count_target_available(
    goal_target_obj: GridUnitState,
    game_grid_information: GameGridInformation,
    target_tracker: BaseTracker,
    round_limit: int,
) -> TargetAvailabilityState:
    """

    :param goal_target_obj:
    :param game_grid_information:
    :param target_tracker:
    :param round_limit:
    :return:
    """
    current_rounds = target_tracker.steps_taken
    if current_rounds >= round_limit:
        return TargetAvailabilityState.goal_reached_success
    return TargetAvailabilityState.valid
