from enum import Enum
from typing import Callable, Any

from python_prototypes.field_types import GridUnitState, GRID_COORD_UNIT_STATE_T, GameGridInformation
from python_prototypes.reaper.q_state_types import ReaperActionTypes
from python_prototypes.reaper.target_tracker_determiner import BaseTracker


class TargetAvailabilityState(Enum):
    valid = 1
    invalid = 2
    replan_reach = 3
    goal_reached_success = 4


def get_goal_target_determiner(
    current_goal_type: ReaperActionTypes,
) -> Callable[[GridUnitState, GameGridInformation, BaseTracker], TargetAvailabilityState]:
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
            return no_op_target_available
        case ReaperActionTypes.move_tanker_safe:
            return tanker_target_available
        case ReaperActionTypes.move_tanker_risky:
            return tanker_target_available
        case ReaperActionTypes.move_tanker_dangerous:
            return tanker_target_available
        case _:
            raise ValueError(f'Invalid goal type: {current_goal_type}')


def water_target_available(
    goal_target_obj: GridUnitState, game_grid_information: GameGridInformation, target_tracker: BaseTracker
) -> TargetAvailabilityState:
    """
    :param goal_target_obj:
    :param game_grid_information:
    :param target_tracker:
    :return:

    TODO: water is within wrecks
    """
    wreck_id = goal_target_obj.unit.unit_id
    _wreck_coordinate = goal_target_obj.grid_coordinate

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
    goal_target_obj: GridUnitState, game_grid_information: GameGridInformation, target_tracker: BaseTracker
) -> TargetAvailabilityState:
    """

    :param goal_target_obj:
    :param game_grid_information:
    :param target_tracker:
    :return:
    """
    enemy_target_id = goal_target_obj.unit.unit_id
    enemy_target_coordinate = goal_target_obj.grid_coordinate

    if not game_grid_information.enemy_reaper_id_to_grid_coord:
        return TargetAvailabilityState.invalid

    if enemy_target_id not in game_grid_information.enemy_reaper_id_to_grid_coord:
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
        if target_tracker.is_moving_towards_target():
            return TargetAvailabilityState.replan_reach
        return TargetAvailabilityState.valid

    moving_towards_target = target_tracker.is_moving_towards_target()
    if not moving_towards_target:
        return TargetAvailabilityState.invalid

    player_higher_momentum = target_tracker.is_player_higher_momentum()
    if not player_higher_momentum:
        return TargetAvailabilityState.invalid

    return TargetAvailabilityState.goal_reached_success


def super_power_target_available(
    goal_type: str, goal_target_obj: GridUnitState, full_grid_state: GRID_COORD_UNIT_STATE_T
) -> TargetAvailabilityState:
    pass


def tanker_target_available(
    goal_type: str, goal_target_obj: GridUnitState, full_grid_state: GRID_COORD_UNIT_STATE_T
) -> TargetAvailabilityState:
    """
    :param goal_type:
    :param goal_target_obj:
    :return:

    TODO: water is within wrecks
    """
    does_it_still_exist()
    are_we_getting_closer()
    rounds_limit_reached()

    return TargetAvailabilityState.valid


def no_op_target_available(
    goal_type: str, goal_target_obj: GridUnitState, full_grid_state: GRID_COORD_UNIT_STATE_T
) -> TargetAvailabilityState:
    return TargetAvailabilityState.valid
