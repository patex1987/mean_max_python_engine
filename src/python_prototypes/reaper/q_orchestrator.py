"""
Currently contains q state handling and the reaper decider based on q
learning
"""

import random

from python_prototypes.field_types import GridUnitState
from python_prototypes.reaper.goal_possibility_determiner import get_goal_possibility_determiner
from python_prototypes.reaper.q_state_types import (
    ReaperQState,
    get_default_reaper_actions_q_weights,
    ReaperActionsQWeights,
    get_default_water_relations,
    get_default_enemies_relation,
)
from python_prototypes.reaper.target_availability_determiner import get_goal_target_determiner
from python_prototypes.reaper.target_reached_determiner import get_goal_reached_determiner
from python_prototypes.reaper.target_selector import get_target_selector
from python_prototypes.reaper.target_tracker_determiner import get_target_tracker


class ReaperGameState:
    """
    this is transferred between game rounds and can be mutated in an individual round
    """

    def __init__(self):
        self.current_goal_type = None
        self._mission_set = False
        self._current_target_entity = None
        self._current_target_unit_id = None
        self._current_mission_steps = []
        self._q_table = {}
        self._target_tracker = None
        self.exploration_rate = 0.2

    def is_on_mission(self):
        return self._mission_set

    def initialize_new_goal_type(self, reaper_q_state: ReaperQState) -> str:
        new_goal = self.get_new_goal_type(reaper_q_state)
        self.set_and_initialize_goal_type(new_goal)
        return new_goal

    def update_existing_target_entity(self, target_unit_id, updated_grid_state: GridUnitState = None):
        if target_unit_id != self._current_target_unit_id:
            raise ValueError('You are attempting to update a target, there is a different method for that')
        if target_unit_id != updated_grid_state.unit.unit_id:
            raise ValueError('You are attempting to update a target, where the id and the id in the grid_state differs')
        if not updated_grid_state:
            updated_grid_state = find_unit(full_grid_state, target_unit_id)

        self._current_target_entity = updated_grid_state.unit.unit_type

    def get_new_goal_type(self, reaper_q_state: ReaperQState) -> str:
        q_state_key = reaper_q_state.get_state_tuple_key()
        reaper_q_action_weights = self._q_table.setdefault(
            q_state_key, ReaperActionsQWeights(get_default_reaper_actions_q_weights())
        )

        exploration_rate = random.uniform(0, 1)
        if exploration_rate < self.exploration_rate:
            possible_keys = list(reaper_q_action_weights.inner_weigths_dict.keys())
            return random.choice(possible_keys)

        sorted_actions = reaper_q_action_weights.get_sorted_weights()
        for goal_type, weight in sorted_actions:
            is_available = self.is_goal_possible(reaper_q_state, goal_type)
            if not is_available:
                continue

            return goal_type

        return 'wait'

    def set_and_initialize_goal_type(self, new_goal_type: str):
        self._mission_set = True
        self._current_mission_steps = []
        self.current_goal_type = new_goal_type

    def propagate_failed_goal(self):
        """
        applies a failure penalty after a failed goal to every single step
        in the current mission
        :param current_goal:
        :return:
        """
        current_goal = self.current_goal_type
        failure_penalty = get_goal_failure_penalty(current_goal)
        for state_step in self._current_mission_steps:
            self._reaper_q_actions.inner_weigths_dict[state_step] -= failure_penalty

    def is_goal_possible(self, reaper_q_state: ReaperQState, goal_type: str) -> bool:
        """
        TODO: the availability determiner apprach is just one way to achieve this
        """
        goal_possibility_determiner = get_goal_possibility_determiner(goal_type)
        is_possible = goal_possibility_determiner(reaper_q_state)
        return is_possible

    def is_goal_target_available(self) -> bool:
        goal_target_determiner = get_goal_target_determiner(self.current_goal_type)
        is_available = goal_target_determiner(self._reaper_q_state, self._current_target_entity)
        return is_available

    def propagate_successful_goal(self):
        current_goal = self.current_goal_type
        success_reward = get_goal_success_reward(current_goal)
        for state_step in self._current_mission_steps:
            self._reaper_q_actions.inner_weigths_dict[state_step] += success_reward

    def is_goal_reached(self, current_goal):
        reachability_determiner = get_goal_reached_determiner(current_goal)
        is_reached = reachability_determiner(self._reaper_q_state)
        return is_reached

    def initialize_new_target(self, reaper_goal_type: str, reaper_q_state: ReaperQState):
        target_tracker = get_target_tracker(reaper_goal_type)
        self._target_tracker = target_tracker
        target_selector = get_target_selector(reaper_goal_type, reaper_q_state)
        target = target_selector.select(reaper_goal_type)
        self._current_target_entity = target
        self._target_tracker.track(player_reaper_unit=player_reaper_unit, target_entity=target)
        return target


def get_goal_failure_penalty(current_goal: str) -> float:
    """
    TODO: add goal specific penalties
    :param current_goal:
    :return:
    """
    return -0.5


def get_goal_success_reward(current_goal: str) -> float:
    """
    TODO: add goal specific rewards
    :param current_goal:
    :return:
    """
    return -1.0


class TestReaperGameStateInitializeNewTarget:
    def test_initialize_new_target(self):
        reaper_q_state = ReaperQState(
            water_reaper_relation=get_default_water_relations(),
            water_other_relation=get_default_water_relations(),
            tanker_enemy_relation=get_default_enemies_relation(),
            player_reaper_relation=get_default_enemies_relation(),
            player_other_relation=get_default_enemies_relation(),
            super_power_available=False,
        )
        reaper_game_state = ReaperGameState()
        reaper_game_state.initialize_new_goal_type(reaper_q_state)
        reaper_game_state.initialize_new_target(reaper_game_state.current_goal_type, reaper_q_state)
        assert reaper_game_state._current_target_entity is not None
        assert reaper_game_state._target_tracker is not None
        assert reaper_game_state._target_tracker.steps_taken == 0
