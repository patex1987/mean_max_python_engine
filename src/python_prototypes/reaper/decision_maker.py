from python_prototypes.reaper.q_orchestrator import ReaperGameState
from python_prototypes.reaper.q_state_types import ReaperQState


def reaper_decider(reaper_game_state: ReaperGameState, reaper_q_state: ReaperQState) -> tuple[str, Any]:
    """

    :param reaper_game_state:
    :param reaper_q_state:
    :return: tuple[ goal_type, target unit ]
        returns the goal type as string currently.
        - See
        `python_prototypes.reaper.q_state_types.get_default_reaper_actions_q_weights`
        for the possible values
        - TODO: change it to an enum
    """
    on_mission = reaper_game_state.is_on_mission()

    if not on_mission:
        new_reaper_goal_type = reaper_game_state.initialize_new_goal_type()
        new_target = reaper_game_state.initialize_new_target(new_reaper_goal_type)
        return new_reaper_goal_type, new_target

    current_goal_type = reaper_game_state.current_goal_type
    is_target_available = reaper_game_state.is_goal_target_available()
    if not is_target_available:
        reaper_game_state.propagate_failed_goal()
        new_reaper_goal_type = reaper_game_state.initialize_new_goal_type()
        new_target = reaper_game_state.initialize_new_target(new_reaper_goal_type)

        return new_reaper_goal_type, new_target

    goal_reached = reaper_game_state.is_goal_reached(current_goal_type)
    if not goal_reached:
        reaper_game_state.propagate_successful_goal(reaper_q_state)
        return current_goal_type

    new_reaper_goal_type = reaper_game_state.initialize_new_goal_type(reaper_q_state)
    reaper_game_state.propagate_successful_goal(current_goal_type)
    return new_reaper_goal_type
