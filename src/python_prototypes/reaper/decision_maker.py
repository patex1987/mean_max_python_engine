from dataclasses import dataclass
from enum import Enum


from python_prototypes.field_types import (
    GameGridInformation,
    PlayerState,
    GridUnitState,
)
from python_prototypes.reaper.q_orchestrator import (
    ReaperGameState,
    find_target_grid_unit_state,
    get_updated_goal_type,
)
from python_prototypes.reaper.q_state_types import (
    ReaperQState,
    ReaperActionTypes,
)
from python_prototypes.reaper.target_availability_determiner import (
    TargetAvailabilityState,
)


class ReaperDecisionType(Enum):
    new_target_on_failure = 0
    new_target_on_undefined = 1
    new_target_on_success = 2
    existing_target = 3
    replan_existing_target = 4


@dataclass
class ReaperDecisionOutput:
    decision_type: ReaperDecisionType
    goal_action_type: ReaperActionTypes
    target_grid_unit: GridUnitState | None


def reaper_decider(
    reaper_game_state: ReaperGameState,
    reaper_q_state: ReaperQState,
    game_grid_information: GameGridInformation,
    player_state: PlayerState,
) -> ReaperDecisionOutput:
    """
    this determines THE what (i.e. what to do), but doesn't determine THE
    how (i.e. doesn't determine what path, steps to take to get there)

    :param reaper_game_state:
    :param reaper_q_state: This object can't change during the round
    :param game_grid_information:
    :param player_state:
    :return: ReaperDecisionOutput

    """
    reaper_game_state.register_q_state(reaper_q_state)
    on_mission = reaper_game_state.is_on_mission()

    if not on_mission:
        decision_output = get_new_decision(
            game_grid_information,
            player_state,
            reaper_game_state,
            reaper_q_state,
            ReaperDecisionType.new_target_on_undefined,
        )
        # registration is not needed, as it is already registered by the above lines
        reaper_game_state.apply_step_penalty(reaper_q_state)
        return decision_output

    current_target = reaper_game_state.current_target_info
    actual_target_grid_unit_state = None
    if current_target:
        actual_target_grid_unit_state = find_target_grid_unit_state(
            game_grid_information=game_grid_information,
            target=current_target,
        )

    if actual_target_grid_unit_state:
        reaper_game_state.target_tracker.track(
            player_reaper_unit=player_state.reaper_state,
            target_unit=actual_target_grid_unit_state,
        )
        reaper_game_state.current_targets_player_id = actual_target_grid_unit_state.unit.player

    target_availability = reaper_game_state.get_goal_target_availability(
        target_grid_unit=actual_target_grid_unit_state,
        game_grid_information=game_grid_information,
        tracker=reaper_game_state.target_tracker,
    )
    current_goal_type = reaper_game_state.current_goal_type
    adjusted_goal_type = get_updated_goal_type(reaper_q_state, current_target, current_goal_type)
    # TODO: the next line can be decided based on the `TargetAvailabilityState.invalid` state
    actual_goal_type = adjusted_goal_type or current_goal_type
    reaper_game_state.add_current_step_to_mission(reaper_q_state, actual_goal_type)
    reaper_game_state.apply_step_penalty(reaper_q_state)

    if target_availability == TargetAvailabilityState.invalid:
        reaper_game_state.propagate_failed_goal()
        new_decision = get_new_decision(
            game_grid_information,
            player_state,
            reaper_game_state,
            reaper_q_state,
            ReaperDecisionType.new_target_on_failure,
        )
        # TODO: see one of the TODOs above, duplicated from there
        reaper_game_state.add_current_step_to_mission(reaper_q_state, new_decision.goal_action_type)
        reaper_game_state.apply_step_penalty(reaper_q_state)
        return new_decision

    if target_availability == TargetAvailabilityState.goal_reached_success:
        reaper_game_state.propagate_successful_goal()
        new_decision = get_new_decision(
            game_grid_information,
            player_state,
            reaper_game_state,
            reaper_q_state,
            ReaperDecisionType.new_target_on_success,
        )
        # TODO: see one of the TODOs above, duplicated from there
        reaper_game_state.add_current_step_to_mission(reaper_q_state, new_decision.goal_action_type)
        reaper_game_state.apply_step_penalty(reaper_q_state)
        return new_decision

    adjusted_goal_type = reaper_game_state.current_goal_type
    decision_type = ReaperDecisionType.existing_target
    if target_availability == TargetAvailabilityState.replan_reach:
        decision_type = ReaperDecisionType.replan_existing_target
    return ReaperDecisionOutput(decision_type, adjusted_goal_type, actual_target_grid_unit_state)


def get_new_decision(
    game_grid_information: GameGridInformation,
    player_state: PlayerState,
    reaper_game_state: ReaperGameState,
    reaper_q_state: ReaperQState,
    output_type: ReaperDecisionType,
) -> ReaperDecisionOutput:
    new_reaper_goal_type = reaper_game_state.initialize_new_goal_type(reaper_q_state)
    new_target = reaper_game_state.initialize_new_target(
        reaper_goal_type=new_reaper_goal_type, reaper_q_state=reaper_q_state
    )
    if not new_target:
        return ReaperDecisionOutput(output_type, new_reaper_goal_type, None)
    target_grid_unit_state = find_target_grid_unit_state(
        game_grid_information=game_grid_information,
        target=new_target,
    )
    # TODO: call to target tracker needs to be encapsulated inside the reaper_game_state
    reaper_game_state.target_tracker.track(
        player_reaper_unit=player_state.reaper_state, target_unit=target_grid_unit_state
    )
    reaper_game_state.current_targets_player_id = target_grid_unit_state.unit.player
    return ReaperDecisionOutput(output_type, new_reaper_goal_type, target_grid_unit_state)
