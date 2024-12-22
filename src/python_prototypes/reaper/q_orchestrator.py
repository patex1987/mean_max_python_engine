"""
Currently contains q state handling and the reaper decider based on q
learning
"""

import random

from python_prototypes.field_types import GridUnitState
from python_prototypes.reaper.q_state_types import (
    ReaperQState,
)
from python_prototypes.reaper.target_determiner import get_goal_target_determiner


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
        self._reaper_q_state = None
        self._reaper_q_actions = None
        self.exploration_rate = 0.2

    def is_on_mission(self):
        return self._mission_set

    def initialize_new_goal_type(self) -> str:
        new_goal = self.get_new_goal_type()
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

    def get_new_goal_type(self) -> str:
        exploration_rate = random.uniform(0, 1)
        if exploration_rate < self.exploration_rate:
            return random.choice(self._reaper_q_actions.inner_weigths_dict.keys())

        sorted_actions = self._reaper_q_actions.get_sorted_weights()
        for goal, weight in sorted_actions:
            is_available = self.is_goal_possible(goal)
            if not is_available:
                continue

            return goal

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

    def is_goal_possible(self, goal_type) -> bool:
        """
        TODO: the availability determiner apprach is just one way to achieve this
        """
        goal_possibility_determiner = get_goal_possibility_determiner(goal_type)
        is_possible = goal_possibility_determiner(self._reaper_q_state)
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


def safe_water_possible(reaper_q_state: ReaperQState) -> bool:
    """
    TODO: missing the water other enemy relation
    TODO: these availability checks should be made simpler (and most
        probably should be delegated to the relations level (but they
        are currently dictionaries))
    :param reaper_q_state:
    :return:
    """
    available = (
        reaper_q_state.water_reaper_relation.get(('close', 'safe'), 0) > 0
        or reaper_q_state.water_reaper_relation.get(('medium', 'safe'), 0) > 0
        or reaper_q_state.water_reaper_relation.get(('far', 'safe'), 0) > 0
    )
    return available


def risky_water_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.water_reaper_relation.get(('close', 'risky'), 0) > 0
        or reaper_q_state.water_reaper_relation.get(('medium', 'risky'), 0) > 0
        or reaper_q_state.water_reaper_relation.get(('far', 'risky'), 0) > 0
    )
    return available


def dangerous_water_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.water_reaper_relation.get(('close', 'dangerous'), 0) > 0
        or reaper_q_state.water_reaper_relation.get(('medium', 'dangerous'), 0) > 0
        or reaper_q_state.water_reaper_relation.get(('far', 'dangerous'), 0) > 0
    )
    return available


def close_reaper_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.player_reaper_relation.get(('close', 'close'), 0) > 0
        or reaper_q_state.player_reaper_relation.get(('close', 'medium'), 0) > 0
    )
    return available


def mid_reaper_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.player_reaper_relation.get(('mid', 'close'), 0) > 0
        or reaper_q_state.player_reaper_relation.get(('mid', 'medium'), 0) > 0
    )
    return available


def far_reaper_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.player_reaper_relation.get(('far', 'close'), 0) > 0
        or reaper_q_state.player_reaper_relation.get(('far', 'medium'), 0) > 0
    )
    return available


def close_other_enemy_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.player_other_relation.get(('close', 'close'), 0) > 0
        or reaper_q_state.player_other_relation.get(('close', 'medium'), 0) > 0
    )
    return available


def mid_other_enemy_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.player_other_relation.get(('mid', 'close'), 0) > 0
        or reaper_q_state.player_other_relation.get(('mid', 'medium'), 0) > 0
    )
    return available


def far_other_enemy_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.player_other_relation.get(('far', 'close'), 0) > 0
        or reaper_q_state.player_other_relation.get(('far', 'medium'), 0) > 0
    )
    return available


def super_power_possible(reaper_q_state: ReaperQState) -> bool:
    available = reaper_q_state.super_power_available
    return available


def no_op_possible(reaper_q_state: ReaperQState) -> bool:
    return True


def get_goal_possibility_determiner(current_goal):

    match current_goal:
        case 'harvest_safe':
            return safe_water_possible
        case 'harvest_risky':
            return risky_water_possible
        case 'harvest_dangerous':
            return dangerous_water_possible
        case 'ram_reaper_close':
            return close_reaper_possible
        case 'ram_reaper_mid':
            return mid_reaper_possible
        case 'ram_reaper_far':
            return far_reaper_possible
        case 'ram_other_close':
            return close_other_enemy_possible
        case 'ram_other_mid':
            return mid_other_enemy_possible
        case 'ram_other_far':
            return far_other_enemy_possible
        case 'use_super_power':
            return super_power_possible
        case 'wait':
            return no_op_possible
        case _:
            raise ValueError(f'Invalid goal type: {current_goal}')


def get_goal_reached_determiner(current_goal):
    match current_goal:
        case 'harvest_safe':
            return
        case 'harvest_risky':
            return
        case 'harvest_dangerous':
            return
        case 'ram_reaper_close':
            return
        case 'ram_reaper_mid':
            return
        case 'ram_reaper_far':
            return
        case 'ram_other_close':
            return
        case 'ram_other_mid':
            return
        case 'ram_other_far':
            return
        case 'use_super_power':
            return
        case 'wait':
            return
        case _:
            raise ValueError(f'Invalid goal type: {current_goal}')
