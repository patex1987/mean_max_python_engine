from dataclasses import dataclass
from functools import partial
from typing import Callable

from python_prototypes.field_types import EntitiesForReaper
from python_prototypes.reaper.exception_types import ImpossibleTarget
from python_prototypes.reaper.q_state_types import ReaperQState, ReaperActionTypes


@dataclass
class SelectedTargetInformation:
    id: int
    type: EntitiesForReaper
    player_id: int | None = None  # player the target belongs to, this field is set later


def get_target_id_selector(
    reaper_goal_type: ReaperActionTypes,
) -> Callable[[ReaperQState], SelectedTargetInformation | None]:
    """

    :param reaper_goal_type:
    :return: the callable returns the id of the target object (if available) and its SimplifiedEntitiesForReaper type
    """
    match reaper_goal_type:
        case ReaperActionTypes.harvest_safe:
            return partial(select_water_target_by_risk_level, risk_level="safe")
        case ReaperActionTypes.harvest_risky:
            return partial(select_water_target_by_risk_level, risk_level="risky")
        case ReaperActionTypes.harvest_dangerous:
            return partial(select_water_target_by_risk_level, risk_level="dangerous")
        case ReaperActionTypes.ram_reaper_close:
            return partial(select_enemy_reaper_by_distance, distance_level="close")
        case ReaperActionTypes.ram_reaper_medium:
            return partial(select_enemy_reaper_by_distance, distance_level="medium")
        case ReaperActionTypes.ram_reaper_far:
            return partial(select_enemy_reaper_by_distance, distance_level="far")
        case ReaperActionTypes.ram_other_close:
            return partial(select_enemy_other_by_distance, distance_level="close")
        case ReaperActionTypes.ram_other_medium:
            return partial(select_enemy_other_by_distance, distance_level="medium")
        case ReaperActionTypes.ram_other_far:
            return partial(select_enemy_other_by_distance, distance_level="far")
        case ReaperActionTypes.use_super_power:
            # TODO: currently we consider only wrecks for super powers, add new super power categories in the future
            return partial(select_water_target_by_risk_level, risk_level="safe")
        case ReaperActionTypes.wait:
            return no_op_target_selector
        case ReaperActionTypes.move_tanker_safe:
            return partial(select_tanker_target_by_risk_level, risk_level="safe")
        case ReaperActionTypes.move_tanker_risky:
            return partial(select_tanker_target_by_risk_level, risk_level="risky")
        case ReaperActionTypes.move_tanker_dangerous:
            return partial(select_tanker_target_by_risk_level, risk_level="dangerous")
        case _:
            raise ValueError(f"Invalid goal type: {reaper_goal_type}")


def select_water_target_by_risk_level(reaper_q_state: ReaperQState, risk_level: str) -> SelectedTargetInformation:
    if relation := reaper_q_state.water_reaper_relation[("close", risk_level)]:
        return SelectedTargetInformation(relation[0], EntitiesForReaper.WRECK)
    if relation := reaper_q_state.water_reaper_relation[("medium", risk_level)]:
        return SelectedTargetInformation(relation[0], EntitiesForReaper.WRECK)
    if relation := reaper_q_state.water_reaper_relation[("far", risk_level)]:
        return SelectedTargetInformation(relation[0], EntitiesForReaper.WRECK)
    raise ImpossibleTarget(f"No water target found for risk level: {risk_level}")


def select_enemy_reaper_by_distance(reaper_q_state: ReaperQState, distance_level: str) -> SelectedTargetInformation:
    if relation := reaper_q_state.player_reaper_relation[(distance_level, "close")]:
        return SelectedTargetInformation(relation[0], EntitiesForReaper.REAPER)
    if relation := reaper_q_state.player_reaper_relation[(distance_level, "medium")]:
        return SelectedTargetInformation(relation[0], EntitiesForReaper.REAPER)
    raise ImpossibleTarget(f"No enemy reaper found for distance level: {distance_level}")


def select_enemy_other_by_distance(reaper_q_state: ReaperQState, distance_level: str) -> SelectedTargetInformation:
    if relation := reaper_q_state.player_other_relation[(distance_level, "close")]:
        return SelectedTargetInformation(relation[0], EntitiesForReaper.OTHER_ENEMY)
    if relation := reaper_q_state.player_other_relation[(distance_level, "medium")]:
        return SelectedTargetInformation(relation[0], EntitiesForReaper.OTHER_ENEMY)
    raise ImpossibleTarget(f"No other enemy found for distance level: {distance_level}")


def select_tanker_target_by_risk_level(reaper_q_state: ReaperQState, risk_level: str) -> SelectedTargetInformation:
    if relation := reaper_q_state.tanker_enemy_relation[("close", risk_level)]:
        return SelectedTargetInformation(relation[0], EntitiesForReaper.TANKER)
    if relation := reaper_q_state.tanker_enemy_relation[("medium", risk_level)]:
        return SelectedTargetInformation(relation[0], EntitiesForReaper.TANKER)
    if relation := reaper_q_state.tanker_enemy_relation[("far", risk_level)]:
        return SelectedTargetInformation(relation[0], EntitiesForReaper.TANKER)
    raise ImpossibleTarget(f"No tanker target found for risk level: {risk_level}")


def no_op_target_selector(reaper_q_state: ReaperQState) -> None:
    return
