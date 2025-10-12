import copy

from python_prototypes.field_types import PlayerState, GameGridInformation
from python_prototypes.reaper.long_term_tracker.tracker_units import LongTermTracker
from python_prototypes.reaper.q_state_types import (
    ReaperQState,
    MissionStep,
    ReaperActionsQWeights,
    get_default_reaper_actions_q_weights,
)


class LongTermRewardTrackingOrchestrator:
    """
    Register, deregister and orchestrate long term reward trackers.
    """

    def __init__(self):
        self.success_trackers = {}
        self.failure_trackers = {}

    def register_success_tracker(self, tracker: LongTermTracker):
        self.success_trackers[tracker.get_tracker_id()] = tracker

    def register_failure_tracker(self, tracker: LongTermTracker):
        self.failure_trackers[tracker.get_tracker_id()] = tracker

    def orchestrate(
        self,
        original_mission_steps: list[MissionStep],
        player_state: PlayerState,
        enemy_1_state: PlayerState,
        enemy_2_state: PlayerState,
        game_grid_information: GameGridInformation,
    ):
        """
        return only the adjustments to the q table, but don't mutate the q table

        dict[q_state_key][goal_type] = +/- gain / loss
        TODO: if possible send something simpler instead of game_grid_information
        """
        q_table_change = {}
        success_tracker_keys = list(self.success_trackers.keys())
        for tracker_id in success_tracker_keys:
            tracker = self.success_trackers[tracker_id]
            gain = tracker.get_round_gain_loss(
                player_state=player_state,
                enemy_1_state=enemy_1_state,
                enemy_2_state=enemy_2_state,
                game_grid_information=game_grid_information,
            )
            if gain:
                # TODO: move to a common propagate method
                for mission_step in original_mission_steps:
                    q_table_change.setdefault(
                        mission_step.q_state_key, ReaperActionsQWeights(get_default_reaper_actions_q_weights())
                    )
                    q_table_change[mission_step.q_state_key].inner_weigths_dict[mission_step.goal_type] += gain

            if tracker.is_expired():
                self.success_trackers.pop(tracker_id)

        failure_tracker_keys = list(self.failure_trackers.keys())
        for tracker_id in failure_tracker_keys:
            tracker = self.failure_trackers[tracker_id]
            loss = tracker.get_round_gain_loss(
                player_state=player_state,
                enemy_1_state=enemy_1_state,
                enemy_2_state=enemy_2_state,
                game_grid_information=game_grid_information,
            )
            if loss:
                # TODO: move to a common propagate method
                for mission_step in original_mission_steps:
                    q_table_change.setdefault(
                        mission_step.q_state_key, ReaperActionsQWeights(get_default_reaper_actions_q_weights())
                    )
                    q_table_change[mission_step.q_state_key].inner_weigths_dict[mission_step.goal_type] += loss

            if tracker.is_expired():
                self.failure_trackers.pop(tracker_id)

        return q_table_change
