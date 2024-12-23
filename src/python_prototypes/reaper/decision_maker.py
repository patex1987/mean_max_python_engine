from typing import Any

from python_prototypes.field_types import GameGridInformation, PlayerState
from python_prototypes.reaper.q_orchestrator import ReaperGameState
from python_prototypes.reaper.q_state_types import ReaperQState, ReaperActionTypes


def reaper_decider(
    reaper_game_state: ReaperGameState,
    reaper_q_state: ReaperQState,
    game_grid_information: GameGridInformation,
    player_state: PlayerState,
) -> tuple[ReaperActionTypes, Any]:
    """

    :param reaper_game_state:
    :param reaper_q_state:
    :return: tuple[ goal_type, target unit ]
    """
    on_mission = reaper_game_state.is_on_mission()

    if not on_mission:
        new_reaper_goal_type = reaper_game_state.initialize_new_goal_type(reaper_q_state)
        new_target = reaper_game_state.initialize_new_target(
            reaper_goal_type=new_reaper_goal_type, game_grid_information=game_grid_information
        )
        reaper_game_state._target_tracker.track_target(new_target)
        return new_reaper_goal_type, new_target

    current_goal_type = reaper_game_state.current_goal_type
    is_target_available = reaper_game_state.is_goal_target_available()
    if not is_target_available:
        reaper_game_state.propagate_failed_goal()
        new_reaper_goal_type = reaper_game_state.initialize_new_goal_type(reaper_q_state)
        new_target = reaper_game_state.initialize_new_target(
            reaper_goal_type=new_reaper_goal_type, game_grid_information=game_grid_information
        )
        reaper_game_state._target_tracker.track_target(new_target)
        return new_reaper_goal_type, new_target

    goal_reached = reaper_game_state.is_goal_reached(current_goal_type)
    if not goal_reached:
        reaper_game_state.propagate_successful_goal(reaper_q_state)
        return current_goal_type

    new_reaper_goal_type = reaper_game_state.initialize_new_goal_type(reaper_q_state)
    reaper_game_state.propagate_successful_goal(current_goal_type)
    return new_reaper_goal_type, target
