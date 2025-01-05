import math
from dataclasses import dataclass
from enum import Enum


from python_prototypes.field_types import (
    GameGridInformation,
    PlayerState,
    GridUnitState,
    Unit,
    Entity,
    EntitiesForReaper,
)
from python_prototypes.real_game_mocks.full_grid_state import ExampleBasicScenarioIncomplete
from python_prototypes.reaper.input_to_q_state import calculate_reaper_q_state
from python_prototypes.reaper.q_orchestrator import ReaperGameState, find_target_grid_unit_state, get_updated_goal_type
from python_prototypes.reaper.q_state_types import (
    ReaperQState,
    ReaperActionTypes,
    get_default_water_relations,
    get_default_enemies_relation,
)
from python_prototypes.reaper.target_availability_determiner import TargetAvailabilityState
from python_prototypes.reaper.target_selector import SelectedTargetInformation
from python_prototypes.reaper.target_tracker_determiner import get_target_tracker


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

    # TODO: store the original goal type and the actualized goal type for every round
    """
    on_mission = reaper_game_state.is_on_mission()

    if not on_mission:
        new_reaper_goal_type = reaper_game_state.initialize_new_goal_type(reaper_q_state)
        new_target = reaper_game_state.initialize_new_target(
            reaper_goal_type=new_reaper_goal_type, reaper_q_state=reaper_q_state
        )
        # registration is not needed, as it is already registered by the above lines
        # reaper_game_state.register_q_state(q_state_key)
        # TODO: move the next 3 lines to a dedicated method if possible
        q_state_key = reaper_q_state.get_state_tuple_key()
        reaper_game_state.add_current_step_to_mission(q_state_key, new_reaper_goal_type)
        reaper_game_state.apply_step_penalty(q_state_key)

        if not new_target:
            return ReaperDecisionOutput(ReaperDecisionType.new_target_on_undefined, new_reaper_goal_type, None)

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

    current_target = reaper_game_state.current_target_info
    actual_target_grid_unit_state = None
    if current_target:
        actual_target_grid_unit_state = find_target_grid_unit_state(
            game_grid_information=game_grid_information,
            target=current_target,
        )

    # TODO: change is_goal_target_available's return `TargetAvailabilityState` to tell if the goal was reached
    target_availability = reaper_game_state.get_goal_target_availability(
        target_grid_unit=actual_target_grid_unit_state,
        game_grid_information=game_grid_information,
        tracker=reaper_game_state._target_tracker,
    )
    if target_availability == TargetAvailabilityState.invalid:
        reaper_game_state.propagate_failed_goal()
        new_reaper_goal_type = reaper_game_state.initialize_new_goal_type(reaper_q_state)
        new_target = reaper_game_state.initialize_new_target(
            reaper_goal_type=new_reaper_goal_type, reaper_q_state=reaper_q_state
        )

        # TODO: see one of the TODOs above, duplicated from there
        q_state_key = reaper_q_state.get_state_tuple_key()
        reaper_game_state.add_current_step_to_mission(q_state_key, new_reaper_goal_type)
        reaper_game_state.apply_step_penalty(q_state_key)

        if not new_target:
            return ReaperDecisionOutput(ReaperDecisionType.new_target_on_failure, new_reaper_goal_type, None)

        target_grid_unit_state = find_target_grid_unit_state(
            game_grid_information=game_grid_information,
            target=new_target,
        )
        reaper_game_state._target_tracker.track(
            player_reaper_unit=player_state.reaper_state, target_unit=target_grid_unit_state
        )

        return ReaperDecisionOutput(
            ReaperDecisionType.new_target_on_failure, new_reaper_goal_type, target_grid_unit_state
        )

    if target_availability == TargetAvailabilityState.goal_reached_success:
        reaper_game_state.propagate_successful_goal()
        new_reaper_goal_type = reaper_game_state.initialize_new_goal_type(reaper_q_state)
        new_target = reaper_game_state.initialize_new_target(
            reaper_goal_type=new_reaper_goal_type, reaper_q_state=reaper_q_state
        )

        # TODO: see one of the TODOs above, duplicated from there
        q_state_key = reaper_q_state.get_state_tuple_key()
        reaper_game_state.add_current_step_to_mission(q_state_key, new_reaper_goal_type)
        reaper_game_state.apply_step_penalty(q_state_key)

        if not new_target:
            return ReaperDecisionOutput(ReaperDecisionType.new_target_on_success, new_reaper_goal_type, None)

        target_grid_unit_state = find_target_grid_unit_state(
            game_grid_information=game_grid_information,
            target=new_target,
        )
        reaper_game_state._target_tracker.track(
            player_reaper_unit=player_state.reaper_state, target_unit=target_grid_unit_state
        )

        return ReaperDecisionOutput(
            ReaperDecisionType.new_target_on_success, new_reaper_goal_type, target_grid_unit_state
        )

    reaper_game_state._target_tracker.track(
        player_reaper_unit=player_state.reaper_state, target_unit=actual_target_grid_unit_state
    )

    # TODO: move the next 3 lines to a dedicated method
    current_goal_type = reaper_game_state.current_goal_type
    adjusted_goal_type = get_updated_goal_type(reaper_q_state, current_target, current_goal_type)

    q_state_key = reaper_q_state.get_state_tuple_key()
    reaper_game_state.register_q_state(q_state_key)
    reaper_game_state.add_current_step_to_mission(q_state_key, adjusted_goal_type)
    reaper_game_state.apply_step_penalty(q_state_key)

    return ReaperDecisionOutput(ReaperDecisionType.existing_target, adjusted_goal_type, actual_target_grid_unit_state)


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
            reaper_water_relation={},
            other_water_relation={},
            tanker_id_enemy_category_relation={},
            reaper_id_category_relation={},
            other_id_category_mapping={},
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
        assert decision_output.decision_type == ReaperDecisionType.new_target_on_undefined

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
        assert decision_output.decision_type == ReaperDecisionType.new_target_on_undefined

    def test_target_does_not_exist_anymore(self):
        """
        the selected target doesn't exist anymore, so it should be marked
        as invalid in the result
        """
        game_grid_information = ExampleBasicScenarioIncomplete.get_example_full_grid_state()
        player_state = ExampleBasicScenarioIncomplete.get_example_player_state()
        reaper_q_state = calculate_reaper_q_state(
            game_grid_information=game_grid_information,
            player_state=player_state,
        )

        reaper_game_state = ReaperGameState()
        reaper_game_state._is_mission_set = True

        reaper_game_state.current_target_info = SelectedTargetInformation(id=12345, type=EntitiesForReaper.WRECK)
        q_state_key = reaper_q_state.get_state_tuple_key()
        reaper_game_state.add_current_step_to_mission(q_state_key=q_state_key, goal_type=ReaperActionTypes.harvest_safe)
        assert reaper_game_state.current_goal_type == ReaperActionTypes.harvest_safe

        decision_output = reaper_decider(
            reaper_game_state=reaper_game_state,
            reaper_q_state=reaper_q_state,
            game_grid_information=game_grid_information,
            player_state=player_state,
        )

        assert decision_output.decision_type == ReaperDecisionType.new_target_on_failure
        assert decision_output.goal_action_type is not None

        assert len(reaper_game_state._q_table) == 1
        harvest_failure_penalty = 0.5
        q_weights = reaper_game_state._q_table[q_state_key]
        assert q_weights.inner_weigths_dict[ReaperActionTypes.harvest_safe] == -harvest_failure_penalty

    def test_wait_goal_target_availability_checking(self):
        """
        the selected goal is wait, and it should be valid only for one
        round i.e. in one round the user does wait, and then it should
        be invalidated in the next round

        NOTE: this is again not a full-blown test, see how the tracker
            is injected and used
        TODO: create an actual test that runs both rounds (you need to
            manually adjust the weights so that wait is selected in the
            first round, and invalidated in the second round)
        """
        game_grid_information = ExampleBasicScenarioIncomplete.get_example_full_grid_state()
        player_state = ExampleBasicScenarioIncomplete.get_example_player_state()
        reaper_q_state = calculate_reaper_q_state(
            game_grid_information=game_grid_information,
            player_state=player_state,
        )

        reaper_game_state = ReaperGameState()
        reaper_game_state._is_mission_set = True
        reaper_game_state.add_current_step_to_mission(reaper_q_state.get_state_tuple_key(), ReaperActionTypes.wait)
        tracker = get_target_tracker(reaper_game_state.current_goal_type)
        reaper_game_state._target_tracker = tracker
        reaper_game_state._target_tracker.track(player_state.reaper_state, None)

        decision_output = reaper_decider(
            reaper_game_state=reaper_game_state,
            reaper_q_state=reaper_q_state,
            game_grid_information=game_grid_information,
            player_state=player_state,
        )

        assert decision_output.decision_type == ReaperDecisionType.new_target_on_success
        assert decision_output.goal_action_type is not None

    def test_valid_goal_progressing_to_next_round(self):
        """
        the selected target's availability is determined as valid, so the
        target should propagate to the next round

        player's reaper is at (3, 3)
        enemy other object is at (2, 0) (object id is 2, type is destroyer)
            - and the closest water or tanker is at (2,0)

        i.e. the enemy other object is categorized as close, close
        the player's speed needs to point towards the target. the player
        is not within the collision radius, but as it points towards the
        target its considered valid, and no replan is needed
        """
        game_grid_information = ExampleBasicScenarioIncomplete.get_example_full_grid_state()
        player_state = ExampleBasicScenarioIncomplete.get_example_player_state()

        reaper_q_state = calculate_reaper_q_state(
            game_grid_information=game_grid_information,
            player_state=player_state,
        )

        target_unit = find_target_grid_unit_state(
            game_grid_information=game_grid_information,
            target=SelectedTargetInformation(id=2, type=EntitiesForReaper.OTHER_ENEMY),
        )

        reaper_game_state = ReaperGameState()
        reaper_game_state._is_mission_set = True
        # there is a close, close reaper available in the grid
        reaper_game_state.add_current_step_to_mission(reaper_q_state.get_state_tuple_key(), ReaperActionTypes.ram_other_close)
        reaper_game_state.current_target_info = SelectedTargetInformation(
            id=target_unit.unit.unit_id, type=EntitiesForReaper.OTHER_ENEMY
        )

        enemy_position = target_unit.unit.x, target_unit.unit.y
        player_position = player_state.reaper_state.unit.x, player_state.reaper_state.unit.y
        dx = enemy_position[0] - player_position[0]
        dy = enemy_position[1] - player_position[1]
        magnitude = math.sqrt(dx**2 + dy**2)
        normalized_speed_vector = (dx / magnitude, dy / magnitude)
        player_state.reaper_state.unit.vx = normalized_speed_vector[0] * 100
        player_state.reaper_state.unit.vy = normalized_speed_vector[1] * 100

        player_state.reaper_state.unit.mass = 10
        target_unit.unit.mass = 1

        tracker = get_target_tracker(reaper_game_state.current_goal_type)
        reaper_game_state._target_tracker = tracker
        reaper_game_state._target_tracker.track(player_state.reaper_state, target_unit)

        decision_output = reaper_decider(
            reaper_game_state=reaper_game_state,
            reaper_q_state=reaper_q_state,
            game_grid_information=game_grid_information,
            player_state=player_state,
        )

        assert decision_output.decision_type == ReaperDecisionType.existing_target

        # this should be the same as before
        selected_target_unit = decision_output.target_grid_unit
        assert selected_target_unit.grid_coordinate == target_unit.grid_coordinate
        assert selected_target_unit.unit.unit_id == target_unit.unit.unit_id

    def test_target_reached_successful(self):
        """
        TODO: do this next and validate the propagation into the q state
        """
        pass

    def test_target_reached_failed(self):
        """
        TODO: do this next and validate the propagation into the q state
        """
        pass
