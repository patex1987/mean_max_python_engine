from python_prototypes.destroyer_simulation import Coordinate
from python_prototypes.field_types import EntitiesForReaper, PlayerState
from python_prototypes.real_game_mocks.player_and_wrecks_only import (
    ReaperAndWreckOnlyScenario,
)
from python_prototypes.reaper.input_to_q_state import calculate_reaper_q_state
from python_prototypes.reaper.long_term_tracker.orchestrator import (
    LongTermRewardTrackingOrchestrator,
)
from python_prototypes.reaper.long_term_tracker.tracker_units import (
    HarvestSuccessTracker,
)
from python_prototypes.reaper.q_state_types import MissionStep, ReaperActionTypes
from python_prototypes.reaper.target_selector import SelectedTargetInformation


def execute_rounds(orchestrator, reaper_movement_sequence_water_gain, wreck_coordinate) -> dict:
    """
    Execute the game rounds based on the provided reaper movement.

    Returns the water gain/loss q table changes
    :param orchestrator:
    :param reaper_movement_sequence_water_gain:
    :param wreck_coordinate:
    :return:
    """
    reaper_start_scenario = ReaperAndWreckOnlyScenario.create_with_coordinates(wreck_coordinate, Coordinate(0, 0))
    full_grid_state = reaper_start_scenario.get_full_grid_state()
    player_state = reaper_start_scenario.get_player_state()
    reaper_q_state = calculate_reaper_q_state(full_grid_state, player_state)
    original_mission_steps = [MissionStep(q_state=reaper_q_state, goal_type=ReaperActionTypes.harvest_safe)]
    observed_gains_losses = []
    for reaper_position, water_gain in reaper_movement_sequence_water_gain:
        game_scenario = ReaperAndWreckOnlyScenario.create_with_coordinates(wreck_coordinate, reaper_position)
        full_grid_state = game_scenario.get_full_grid_state()
        player_state = game_scenario.get_player_state(water_gain)
        # reaper_q_state = calculate_reaper_q_state(full_grid_state, player_state)

        q_state_gains_losses = orchestrator.orchestrate(
            original_mission_steps=original_mission_steps,
            player_state=player_state,
            enemy_1_state=PlayerState(
                reaper_state=None,
                destroyer_state=None,
                doof_state=None,
                rage=0,
                score=0,
                prev_rage=0,
                prev_score=0,
            ),
            enemy_2_state=PlayerState(
                reaper_state=None,
                destroyer_state=None,
                doof_state=None,
                rage=0,
                score=0,
                prev_rage=0,
                prev_score=0,
            ),
            game_grid_information=full_grid_state,
        )
        observed_gains_losses.append(q_state_gains_losses)
    return observed_gains_losses


class TestLongTermRewardTrackingOrchestrator:
    def test_harvest_success_hit_twice(self):
        """
        There are 2 steps where the player's team gained score and the reaper is
        within the same grid coordinate as the water wreck (most probably sucked
        the water from the same wreck)

        SO there should be gain backpropagation only in those 2 steps.
        """
        harvest_success_tracker = HarvestSuccessTracker(
            original_water_target=SelectedTargetInformation(
                id=1,
                type=EntitiesForReaper.WRECK,
            )
        )
        orchestrator = LongTermRewardTrackingOrchestrator()
        orchestrator.register_success_tracker(harvest_success_tracker)

        wreck_coordinate = Coordinate(x=1400, y=1400)
        # TODO: change the types, currently tuple of coordinate and water gain
        reaper_movement_sequence_water_gain = [
            (Coordinate(x=500, y=1400), 0),
            (Coordinate(x=1400, y=1400), 1),
            (Coordinate(x=1400, y=2800), 0),
            (Coordinate(x=1400, y=1400), 1),
            (Coordinate(x=500, y=1400), 0),
        ]
        observed_gains_losses = execute_rounds(orchestrator, reaper_movement_sequence_water_gain, wreck_coordinate)

        expected_gain_loss_lengths = [0, 1, 0, 1, 0]
        for idx, observed_gain_loss in enumerate(observed_gains_losses):
            assert len(observed_gain_loss) == expected_gain_loss_lengths[idx]

    def test_no_harvest_success(self):
        """
        Although there are water gains in multiple rounds, it's not related
        to the originally targeted wreck. I.e. they are gained from
        elsewhere.
        """
        harvest_success_tracker = HarvestSuccessTracker(
            original_water_target=SelectedTargetInformation(
                id=1,
                type=EntitiesForReaper.WRECK,
            )
        )
        orchestrator = LongTermRewardTrackingOrchestrator()
        orchestrator.register_success_tracker(harvest_success_tracker)

        wreck_coordinate = Coordinate(x=1400, y=1400)
        # TODO: change the types, currently tuple of coordinate and water gain
        reaper_movement_sequence_water_gain = [
            (Coordinate(x=500, y=1400), 1),
            (Coordinate(x=500, y=1400), 1),
            (Coordinate(x=3600, y=3600), 1),
            (Coordinate(x=500, y=1400), 1),
            (Coordinate(x=3600, y=3600), 0),
        ]
        observed_gains_losses = execute_rounds(orchestrator, reaper_movement_sequence_water_gain, wreck_coordinate)

        expected_gain_loss_lengths = [0, 0, 0, 0, 0]
        for idx, observed_gain_loss in enumerate(observed_gains_losses):
            assert len(observed_gain_loss) == expected_gain_loss_lengths[idx]

    def test_harvest_success_deregistered_after_expiration(self):
        """
        Validates if the tracker is deregistered after the n rounds
        :return:
        """

        harvest_success_tracker = HarvestSuccessTracker(
            original_water_target=SelectedTargetInformation(
                id=1,
                type=EntitiesForReaper.WRECK,
            )
        )
        orchestrator = LongTermRewardTrackingOrchestrator()
        orchestrator.register_success_tracker(harvest_success_tracker)

        wreck_coordinate = Coordinate(x=1400, y=1400)
        # TODO: change the types, currently tuple of coordinate and water gain
        reaper_movement_sequence_water_gain = [
            (Coordinate(x=500, y=1400), 1),
            (Coordinate(x=500, y=1400), 1),
            (Coordinate(x=3600, y=3600), 1),
            (Coordinate(x=500, y=1400), 1),
            (Coordinate(x=3600, y=3600), 0),
        ]
        _ = execute_rounds(orchestrator, reaper_movement_sequence_water_gain, wreck_coordinate)

        assert harvest_success_tracker.tracker_id not in orchestrator.success_trackers
