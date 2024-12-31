from dataclasses import dataclass
from enum import Enum


from python_prototypes.field_types import GameGridInformation, PlayerState, GridUnitState, Unit, Entity
from python_prototypes.real_game_mocks.full_grid_state import ExampleBasicScenarioIncomplete
from python_prototypes.reaper.input_to_q_state import calculate_reaper_q_state
from python_prototypes.reaper.q_orchestrator import ReaperGameState, find_target_grid_unit_state
from python_prototypes.reaper.q_state_types import (
    ReaperQState,
    ReaperActionTypes,
    get_default_water_relations,
    get_default_enemies_relation,
)
from python_prototypes.reaper.target_selector import SelectedTargetInformation


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
    this determines the what (i.e. what to do), but doesn't determine the
    how (i.e. doesn't determine what path, steps to take to get there)

    :param reaper_game_state:
    :param reaper_q_state:
    :param game_grid_information:
    :param player_state:
    :return: tuple[ goal_type, target unit ]
    # TODO: add the actualized grid unit state of the target to the resulting object
    """
    on_mission = reaper_game_state.is_on_mission()

    if not on_mission:
        new_reaper_goal_type = reaper_game_state.initialize_new_goal_type(reaper_q_state)
        new_target = reaper_game_state.initialize_new_target(
            reaper_goal_type=new_reaper_goal_type, reaper_q_state=reaper_q_state
        )

        if not new_target:
            return ReaperDecisionOutput(ReaperDecisionType.new_target, new_reaper_goal_type, None)
        target_grid_unit_state = find_target_grid_unit_state(
            game_grid_information=game_grid_information,
            target=new_target,
        )
        # TODO: call to target tracker needs to be encapsulated inside the reaper_game_state
        reaper_game_state._target_tracker.track(
            player_reaper_unit=player_state.reaper_state, target_unit=target_grid_unit_state
        )
        return ReaperDecisionOutput(
            ReaperDecisionType.new_target_on_undefined, new_reaper_goal_type, target_grid_unit_state
        )

    current_goal_type = reaper_game_state.current_goal_type
    current_target = reaper_game_state._current_target_info
    actual_target_grid_unit_state = find_target_grid_unit_state(
        game_grid_information=game_grid_information,
        target=current_target,
    )
    is_target_available = reaper_game_state.is_goal_target_available()
    if not is_target_available:
        reaper_game_state.propagate_failed_goal()
        new_reaper_goal_type = reaper_game_state.initialize_new_goal_type(reaper_q_state)
        new_target = reaper_game_state.initialize_new_target(
            reaper_goal_type=new_reaper_goal_type, reaper_q_state=reaper_q_state
        )
        reaper_game_state._target_tracker.track(player_reaper_unit=player_state.reaper_state, target_unit=new_target)
        return ReaperDecisionOutput(ReaperDecisionType.new_target_on_failure, new_reaper_goal_type, new_target)

    goal_reached = reaper_game_state.is_goal_reached(current_goal_type)
    if goal_reached:
        reaper_game_state.propagate_successful_goal()
        new_reaper_goal_type = reaper_game_state.initialize_new_goal_type(reaper_q_state)
        new_target = reaper_game_state.initialize_new_target(
            reaper_goal_type=new_reaper_goal_type, reaper_q_state=reaper_q_state
        )
        reaper_game_state._target_tracker.track(player_reaper_unit=player_state.reaper_state, target_unit=new_target)
        return ReaperDecisionOutput(ReaperDecisionType.new_target_on_success, new_reaper_goal_type, new_target)

    curent_target = reaper_game_state._current_target_info
    reaper_game_state._target_tracker.track(player_reaper_unit=player_state.reaper_state, target_unit=new_target)
    reaper_game_state.apply_step_penalty()
    reaper_game_state.add_current_step_to_mission()

    return ReaperDecisionOutput(ReaperDecisionType.existing_target, current_goal_type, actual_target_grid_unit_state)


class TestReaperDecider:
    def test_not_on_a_mission_wait_selected(self):
        """
        This is again just a sort of smoke test (the reaper_q_state and
        game_grid_information are not related to each other)
        exploration rate is set to 0.0, so it always selects wait as the goal type
        """
        reaper_q_state = ReaperQState(
            water_reaper_relation=get_default_water_relations(),
            water_other_relation=get_default_water_relations(),
            tanker_enemy_relation=get_default_enemies_relation(),
            player_reaper_relation=get_default_enemies_relation(),
            player_other_relation=get_default_enemies_relation(),
            super_power_available=False,
        )
        game_grid_information = ExampleBasicScenarioIncomplete.get_example_full_grid_state()
        player_state = PlayerState(
            reaper_state=GridUnitState(grid_coordinate=(0, 0), unit=Unit(0, 0, 10, 0, 300, Entity.REAPER.value)),
            destroyer_state=GridUnitState(grid_coordinate=(0, 0), unit=Unit(0, 0, 10, 0, 300, Entity.DESTROYER.value)),
            doof_state=GridUnitState(grid_coordinate=(0, 0), unit=Unit(0, 0, 10, 0, 300, Entity.DOOF.value)),
            rage=0,
            score=0,
        )
        reaper_game_state = ReaperGameState()
        reaper_game_state.exploration_rate = 0.0
        decision_output = reaper_decider(
            reaper_game_state=reaper_game_state,
            reaper_q_state=reaper_q_state,
            game_grid_information=game_grid_information,
            player_state=player_state,
        )
        assert decision_output.goal_action_type == ReaperActionTypes.wait
        assert decision_output.target_grid_unit is None
        assert decision_output.decision_type == ReaperDecisionType.new_target

    def test_not_on_a_mission_random_goal_selected(self):
        """
        closer to a real game state
        exploration rate is set to 0.0, so it always selects a valid goal type
        """
        game_grid_information = ExampleBasicScenarioIncomplete.get_example_full_grid_state()
        player_state = ExampleBasicScenarioIncomplete.get_example_player_state()
        reaper_q_state = calculate_reaper_q_state(
            game_grid_information=game_grid_information,
            player_state=player_state,
        )

        reaper_game_state = ReaperGameState()
        reaper_game_state.exploration_rate = 0.0
        decision_output = reaper_decider(
            reaper_game_state=reaper_game_state,
            reaper_q_state=reaper_q_state,
            game_grid_information=game_grid_information,
            player_state=player_state,
        )

        assert reaper_game_state.is_on_mission() is True
        if decision_output.goal_action_type == ReaperActionTypes.wait:
            assert decision_output.target_grid_unit is None
            return

        assert decision_output.goal_action_type != ReaperActionTypes.wait
        assert decision_output.target_grid_unit is not None
        assert isinstance(decision_output.target_grid_unit, GridUnitState)
        assert decision_output.decision_type == ReaperDecisionType.new_target

    def test_target_does_not_exist_anymore(self):
        pass
