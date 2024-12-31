from enum import Enum
from typing import Callable, Any

from python_prototypes.field_types import GridUnitState, GRID_COORD_UNIT_STATE_T, GameGridInformation
from python_prototypes.reaper.q_state_types import ReaperActionTypes
from python_prototypes.reaper.target_tracker_determiner import BaseTracker


class TargetAvailabilityState(Enum):
    valid = 1
    invalid = 2
    replan_reach = 3


def get_goal_target_determiner(
    current_goal_type: ReaperActionTypes,
) -> Callable[[str, Any, Any], TargetAvailabilityState]:
    match current_goal_type:
        case ReaperActionTypes.harvest_safe:
            return water_target_available
        case ReaperActionTypes.harvest_risky:
            return water_target_available
        case ReaperActionTypes.harvest_dangerous:
            return water_target_available
        case ReaperActionTypes.ram_reaper_close:
            return ram_reaper_target_available
        case ReaperActionTypes.ram_reaper_mid:
            return ram_reaper_target_available
        case ReaperActionTypes.ram_reaper_far:
            return ram_reaper_target_available
        case ReaperActionTypes.ram_other_close:
            return ram_other_target_available
        case ReaperActionTypes.ram_other_mid:
            return ram_other_target_available
        case ReaperActionTypes.ram_other_far:
            return ram_other_target_available
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
        return TargetAvailabilityState.valid

    return TargetAvailabilityState.valid


def ram_reaper_target_available(
    goal_target_obj: GridUnitState, game_grid_information: GameGridInformation, target_tracker: BaseTracker
) -> TargetAvailabilityState:
    enemy_reaper_id = goal_target_obj.unit.unit_id
    are_we_getting_closer()
    rounds_limit_reached()
    are_we_faster()


def ram_other_target_available(
    goal_type: str, goal_target_obj: GridUnitState, full_grid_state: GRID_COORD_UNIT_STATE_T
) -> TargetAvailabilityState:
    enemy_obj_id = goal_target_obj.unit.unit_id
    are_we_getting_closer()
    rounds_limit_reached()
    are_we_faster()


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
