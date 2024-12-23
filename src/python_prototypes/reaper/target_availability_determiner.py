from enum import Enum
from typing import Callable, Any

from python_prototypes.field_types import GridUnitState, GRID_COORD_UNIT_STATE_T
from python_prototypes.reaper.q_state_types import ReaperActionTypes


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
        case _:
            raise ValueError(f'Invalid goal type: {current_goal_type}')


def water_target_available(
    goal_type: str, goal_target_obj: GridUnitState, full_grid_state: GRID_COORD_UNIT_STATE_T
) -> TargetAvailabilityState:
    """
    :param goal_type:
    :param goal_target_obj:
    :return:

    TODO: water is within wrecks
    """
    wreck_id = goal_target_obj.unit.unit_id
    wreck_coordinate = goal_target_obj.grid_coordinate
    grid_states = full_grid_state.get(wreck_coordinate, None)
    if not grid_states:
        return TargetAvailabilityState.invalid

    wreck_still_valid = any((grid_state.unit.unit_id == wreck_id for grid_state in grid_states))
    if not wreck_still_valid:
        return TargetAvailabilityState.invalid

    are_we_getting_closer()
    rounds_limit_reached()

    return TargetAvailabilityState.valid


def ram_reaper_target_available(
    goal_type: str, goal_target_obj: GridUnitState, full_grid_state: GRID_COORD_UNIT_STATE_T
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


def no_op_target_available(
    goal_type: str, goal_target_obj: GridUnitState, full_grid_state: GRID_COORD_UNIT_STATE_T
) -> TargetAvailabilityState:
    return TargetAvailabilityState.valid
