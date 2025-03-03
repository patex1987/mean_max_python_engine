import copy
import math

from python_prototypes.field_types import PlayerState, GridUnitState, Unit, Entity, EntitiesForReaper
from python_prototypes.real_game_mocks.full_grid_state import ExampleBasicScenarioIncomplete
from python_prototypes.reaper.decision_maker import reaper_decider, ReaperDecisionType
from python_prototypes.reaper.input_to_q_state import calculate_reaper_q_state
from python_prototypes.reaper.q_orchestrator import ReaperGameState, find_target_grid_unit_state
from python_prototypes.reaper.q_state_types import (
    ReaperQState,
    get_default_water_relations,
    get_default_enemies_relation,
    ReaperActionTypes,
)
from python_prototypes.reaper.target_selector import SelectedTargetInformation
from python_prototypes.reaper.target_tracker_determiner import get_target_tracker


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
        tracker = get_target_tracker(reaper_game_state.current_goal_type)
        reaper_game_state.target_tracker = tracker
        assert reaper_game_state.current_goal_type == ReaperActionTypes.harvest_safe

        decision_output = reaper_decider(
            reaper_game_state=reaper_game_state,
            reaper_q_state=reaper_q_state,
            game_grid_information=game_grid_information,
            player_state=player_state,
        )

        assert decision_output.decision_type == ReaperDecisionType.new_target_on_failure
        assert decision_output.goal_action_type is not None

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
        reaper_game_state.target_tracker = tracker
        reaper_game_state.target_tracker.track(player_state.reaper_state, None)

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
        reaper_game_state.add_current_step_to_mission(
            reaper_q_state.get_state_tuple_key(), ReaperActionTypes.ram_other_close
        )
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
        reaper_game_state.target_tracker = tracker
        reaper_game_state.target_tracker.track(player_state.reaper_state, target_unit)

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
        This is emulating a full-blown reaper decision consisting of 2
        rounds. There is only one other enemy marked as close (close,
        close), we are using a test double for reaper game state that
        selects ram_other_close. So after the first round that enemy
        is selected. For the second round we are faking the move to
        actually reach the target and fake higher energy so that the
        strategy successfully ends and rams into the enemy

        there should be only 2 keys in the q table after the 2 rounds
        - the score of the first q state should be 9.5 (10 for the successful
            goal) and -0.5 for the step penalty
        - the score of the second q state should be 9.0 (10 for the successful
            goal) and (2 * -0.5) for the step penalty.
                - -0.5 for the initial goal
                - -0.5 for the newly selected goal
        """

        class FakeReaperGameState(ReaperGameState):
            def get_new_goal_type(self, reaper_q_state: ReaperQState) -> ReaperActionTypes:
                return ReaperActionTypes.ram_other_close

        game_grid_information = ExampleBasicScenarioIncomplete.get_example_full_grid_state()
        player_state = ExampleBasicScenarioIncomplete.get_example_player_state()
        original_player_reaper_coordinate = player_state.reaper_state.grid_coordinate

        reaper_q_state_round_1 = calculate_reaper_q_state(
            game_grid_information=game_grid_information,
            player_state=player_state,
        )

        expected_target_unit = find_target_grid_unit_state(
            game_grid_information=game_grid_information,
            target=SelectedTargetInformation(id=2, type=EntitiesForReaper.OTHER_ENEMY),
        )
        reaper_game_state = FakeReaperGameState()

        # first round
        decision_output = reaper_decider(
            reaper_game_state=reaper_game_state,
            reaper_q_state=reaper_q_state_round_1,
            game_grid_information=game_grid_information,
            player_state=player_state,
        )
        assert decision_output.decision_type == ReaperDecisionType.new_target_on_undefined
        assert decision_output.target_grid_unit.unit.unit_id == expected_target_unit.unit.unit_id
        assert decision_output.goal_action_type == ReaperActionTypes.ram_other_close
        assert len(reaper_game_state._mission_steps) == 1
        assert reaper_game_state._mission_steps[0].q_state_key == reaper_q_state_round_1.get_state_tuple_key()
        assert reaper_game_state._mission_steps[0].goal_type == ReaperActionTypes.ram_other_close

        # second round

        # move player's reaper to the goal
        updated_player_reaper_state = copy.deepcopy(player_state.reaper_state)

        updated_player_reaper_state.grid_coordinate = expected_target_unit.grid_coordinate
        updated_player_reaper_state.unit.x = expected_target_unit.unit.x - 1
        updated_player_reaper_state.unit.y = expected_target_unit.unit.y - 1
        updated_player_reaper_state.unit.mass = 1000
        updated_player_reaper_state.unit.vx = expected_target_unit.unit.x
        updated_player_reaper_state.unit.vy = expected_target_unit.unit.y

        player_state.reaper_state = updated_player_reaper_state
        # this is dangerous, but works for the current test setup
        del game_grid_information.full_grid_state[original_player_reaper_coordinate]
        game_grid_information.full_grid_state[expected_target_unit.grid_coordinate].append(updated_player_reaper_state)

        reaper_q_state_round_2 = calculate_reaper_q_state(
            game_grid_information=game_grid_information,
            player_state=player_state,
        )

        decision_output = reaper_decider(
            reaper_game_state=reaper_game_state,
            reaper_q_state=reaper_q_state_round_2,
            game_grid_information=game_grid_information,
            player_state=player_state,
        )
        assert decision_output.decision_type == ReaperDecisionType.new_target_on_success

        q_table = reaper_game_state._q_table
        assert len(q_table) == 2
        assert reaper_q_state_round_1.get_state_tuple_key() in q_table
        assert reaper_q_state_round_2.get_state_tuple_key() in q_table
        assert (
            q_table[reaper_q_state_round_1.get_state_tuple_key()].inner_weigths_dict[ReaperActionTypes.ram_other_close]
            == 9.5
        )
        assert (
            q_table[reaper_q_state_round_2.get_state_tuple_key()].inner_weigths_dict[ReaperActionTypes.ram_other_close]
            == 9.0
        )

    def test_target_reached_failed(self):
        """
        This is emulating a full-blown reaper decision consisting of multiple
        rounds. There is only one other enemy marked as close (close,
        close), we are using a test double that selects ram_other_close.
        So after the first round that enemy is selected. For the second
        round we are faking the move to actually reach the target, but the
        energy of the player's reaper is not moving towards the target. So
        the target should be marked as invalid and a new target should be
        selected.

        there should be only 2 keys in the q table after the 2 rounds
        - the score of the first q state should be -10.5 (-10 for the failed
            goal) and -0.5 for the step penalty
        - the score of the second q state should be -11.0 (-10 for the failed
            goal) and (2 * -0.5) for the step penalty.
                - -0.5 for the initial goal
                - -0.5 for the newly selected goal
        """

        class FakeReaperGameState(ReaperGameState):
            def get_new_goal_type(self, reaper_q_state: ReaperQState) -> ReaperActionTypes:
                return ReaperActionTypes.ram_other_close

        game_grid_information = ExampleBasicScenarioIncomplete.get_example_full_grid_state()
        player_state = ExampleBasicScenarioIncomplete.get_example_player_state()
        original_player_reaper_coordinate = player_state.reaper_state.grid_coordinate

        reaper_q_state_round_1 = calculate_reaper_q_state(
            game_grid_information=game_grid_information,
            player_state=player_state,
        )

        expected_target_unit = find_target_grid_unit_state(
            game_grid_information=game_grid_information,
            target=SelectedTargetInformation(id=2, type=EntitiesForReaper.OTHER_ENEMY),
        )
        reaper_game_state = FakeReaperGameState()

        # first round
        decision_output = reaper_decider(
            reaper_game_state=reaper_game_state,
            reaper_q_state=reaper_q_state_round_1,
            game_grid_information=game_grid_information,
            player_state=player_state,
        )
        assert decision_output.decision_type == ReaperDecisionType.new_target_on_undefined
        assert decision_output.target_grid_unit.unit.unit_id == expected_target_unit.unit.unit_id
        assert decision_output.goal_action_type == ReaperActionTypes.ram_other_close
        assert len(reaper_game_state._mission_steps) == 1
        assert reaper_game_state._mission_steps[0].q_state_key == reaper_q_state_round_1.get_state_tuple_key()
        assert reaper_game_state._mission_steps[0].goal_type == ReaperActionTypes.ram_other_close

        # second round

        # move player's reaper to the goal
        updated_player_reaper_state = copy.deepcopy(player_state.reaper_state)

        updated_player_reaper_state.grid_coordinate = expected_target_unit.grid_coordinate
        updated_player_reaper_state.unit.x = expected_target_unit.unit.x - 1
        updated_player_reaper_state.unit.y = expected_target_unit.unit.y - 1
        updated_player_reaper_state.unit.mass = 10
        updated_player_reaper_state.unit.vx = expected_target_unit.unit.x
        updated_player_reaper_state.unit.vy = expected_target_unit.unit.y

        player_state.reaper_state = updated_player_reaper_state
        # this is dangerous, but works for the current test setup
        del game_grid_information.full_grid_state[original_player_reaper_coordinate]

        enemy_target_unit_state = copy.deepcopy(expected_target_unit)
        enemy_target_unit_state.unit.vx = updated_player_reaper_state.unit.vx + 1000
        enemy_target_unit_state.unit.vy = 0
        del game_grid_information.full_grid_state[expected_target_unit.grid_coordinate]
        game_grid_information.full_grid_state[expected_target_unit.grid_coordinate].extend(
            [enemy_target_unit_state, updated_player_reaper_state]
        )
        game_grid_information.enemy_others_grid_state[enemy_target_unit_state.grid_coordinate] = [
            enemy_target_unit_state
        ]

        reaper_q_state_round_2 = calculate_reaper_q_state(
            game_grid_information=game_grid_information,
            player_state=player_state,
        )

        decision_output = reaper_decider(
            reaper_game_state=reaper_game_state,
            reaper_q_state=reaper_q_state_round_2,
            game_grid_information=game_grid_information,
            player_state=player_state,
        )
        assert decision_output.decision_type == ReaperDecisionType.new_target_on_failure

        q_table = reaper_game_state._q_table
        assert len(q_table) == 2
        q_state_key_round_1 = reaper_q_state_round_1.get_state_tuple_key()
        q_state_key_round_2 = reaper_q_state_round_2.get_state_tuple_key()
        assert q_state_key_round_1 in q_table
        assert q_state_key_round_2 in q_table
        assert q_table[q_state_key_round_1].inner_weigths_dict[ReaperActionTypes.ram_other_close] == -10.5
        assert q_table[q_state_key_round_2].inner_weigths_dict[ReaperActionTypes.ram_other_close] == -11.0
