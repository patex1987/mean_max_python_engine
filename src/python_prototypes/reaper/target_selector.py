from typing import Any, Callable

from mypy.plugins.default import partial

from python_prototypes.reaper.exception_types import ImpossibleTarget
from python_prototypes.reaper.q_state_types import ReaperQState, ReaperActionTypes


def get_target_selector(reaper_goal_type: ReaperActionTypes) -> Callable[[ReaperQState], int | None]:
    match reaper_goal_type:
        case ReaperActionTypes.harvest_safe:
            return partial(select_water_target_by_risk_level, risk_level='safe')
        case ReaperActionTypes.harvest_risky:
            return partial(select_water_target_by_risk_level, risk_level='risky')
        case ReaperActionTypes.harvest_dangerous:
            return partial(select_water_target_by_risk_level, risk_level='dangerous')
        case ReaperActionTypes.ram_reaper_close:
            return partial(select_enemy_reaper_by_distance, distance_level='close')
        case ReaperActionTypes.ram_reaper_mid:
            return partial(select_enemy_reaper_by_distance, distance_level='medium')
        case ReaperActionTypes.ram_reaper_far:
            return partial(select_enemy_reaper_by_distance, distance_level='far')
        case ReaperActionTypes.ram_other_close:
            return partial(select_enemy_other_by_distance, distance_level='close')
        case ReaperActionTypes.ram_other_mid:
            return partial(select_enemy_other_by_distance, distance_level='medium')
        case ReaperActionTypes.ram_other_far:
            return partial(select_enemy_other_by_distance, distance_level='far')
        case ReaperActionTypes.use_super_power:
            # TODO: currently we consider only wrecks for super powers, add new super power categories in the future
            return partial(select_water_target_by_risk_level, risk_level='safe')
        case ReaperActionTypes.wait:
            return no_op_target_selector
        case _:
            raise ValueError(f'Invalid goal type: {reaper_goal_type}')


def select_water_target_by_risk_level(reaper_q_state: ReaperQState, risk_level: str) -> int:
    if relation := reaper_q_state.water_reaper_relation[('close', risk_level)]:
        return relation[0]
    if relation := reaper_q_state.water_reaper_relation[('medium', risk_level)]:
        return relation[0]
    if relation := reaper_q_state.water_reaper_relation[('far', risk_level)]:
        return relation[0]
    raise ImpossibleTarget(f'No water target found for risk level: {risk_level}')


def select_enemy_reaper_by_distance(reaper_q_state: ReaperQState, distance_level: str) -> int:
    if relation := reaper_q_state.player_reaper_relation[(distance_level, 'close')]:
        return relation[0]
    if relation := reaper_q_state.player_reaper_relation[(distance_level, 'medium')]:
        return relation[0]
    raise ImpossibleTarget(f'No enemy reaper found for distance level: {distance_level}')


def select_enemy_other_by_distance(reaper_q_state: ReaperQState, distance_level: str) -> int:
    if relation := reaper_q_state.player_other_relation[(distance_level, 'close')]:
        return relation[0]
    if relation := reaper_q_state.player_other_relation[(distance_level, 'medium')]:
        return relation[0]
    raise ImpossibleTarget(f'No other enemy found for distance level: {distance_level}')


def no_op_target_selector(reaper_q_state: ReaperQState) -> None:
    return
