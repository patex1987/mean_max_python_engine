"""
Currently contains q state handling and the reaper decider based on q
learning
"""

import random

import pytest

from python_prototypes.field_types import GridUnitState, GameGridInformation, Entity
from python_prototypes.reaper.exception_types import ImpossibleTarget
from python_prototypes.reaper.goal_possibility_determiner import get_goal_possibility_determiner
from python_prototypes.reaper.q_state_types import (
    ReaperQState,
    get_default_reaper_actions_q_weights,
    ReaperActionsQWeights,
    get_default_water_relations,
    get_default_enemies_relation,
    ReaperActionTypes,
)
from python_prototypes.reaper.target_availability_determiner import get_goal_target_determiner
from python_prototypes.reaper.target_reached_determiner import get_goal_reached_determiner
from python_prototypes.reaper.target_selector import get_target_id_selector, SelectedTargetInformation
from python_prototypes.reaper.target_tracker_determiner import get_target_tracker, BaseTracker


class ReaperGameState:
    """
    this is transferred between game rounds and can be mutated in an individual round
    """

    def __init__(self):
        self.current_goal_type = None
        self._mission_set = False
        self._current_target_info: SelectedTargetInformation | None = None
        self._current_target_entity_type = None
        self._current_mission_steps = []
        self._q_table = {}
        self._target_tracker: BaseTracker | None = None
        self.exploration_rate = 0.2
        self.max_random_actions = 10  # make this configurable from the outside

    def is_on_mission(self):
        return self._mission_set

    def initialize_new_goal_type(self, reaper_q_state: ReaperQState) -> ReaperActionTypes:
        new_goal = self.get_new_goal_type(reaper_q_state)
        self.set_and_initialize_goal_type(new_goal)
        return new_goal

    def update_existing_target_entity(self, target_unit_id, updated_grid_state: GridUnitState = None):
        if target_unit_id != self._current_target_info.id:
            raise ValueError('You are attempting to update a target, there is a different method for that')
        if target_unit_id != updated_grid_state.unit.unit_id:
            raise ValueError('You are attempting to update a target, where the id and the id in the grid_state differs')
        if not updated_grid_state:
            updated_grid_state = find_unit(full_grid_state, target_unit_id)

        self._current_target_entity_type = updated_grid_state.unit.unit_type

    def get_new_goal_type(self, reaper_q_state: ReaperQState) -> ReaperActionTypes:
        q_state_key = reaper_q_state.get_state_tuple_key()
        reaper_q_action_weights = self._q_table.setdefault(
            q_state_key, ReaperActionsQWeights(get_default_reaper_actions_q_weights())
        )

        exploration_rate = random.uniform(0, 1)
        if exploration_rate < self.exploration_rate:
            for _ in range(self.max_random_actions):
                possible_keys = list(reaper_q_action_weights.inner_weigths_dict.keys())
                random_goal_type = random.choice(possible_keys)
                is_available = self.is_goal_possible(reaper_q_state, random_goal_type)
                if not is_available:
                    continue

                return random_goal_type
            return ReaperActionTypes.wait

        sorted_actions = reaper_q_action_weights.get_sorted_weights()
        for goal_type, weight in sorted_actions:
            is_available = self.is_goal_possible(reaper_q_state, goal_type)
            if not is_available:
                continue

            return goal_type

        return ReaperActionTypes.wait

    def set_and_initialize_goal_type(self, new_goal_type: ReaperActionTypes):
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

    def is_goal_possible(self, reaper_q_state: ReaperQState, goal_type: ReaperActionTypes) -> bool:
        """
        TODO: the availability determiner apprach is just one way to achieve this
        """
        goal_possibility_determiner = get_goal_possibility_determiner(goal_type)
        is_possible = goal_possibility_determiner(reaper_q_state)
        return is_possible

    def is_goal_target_available(self, current_target, reaper_q_state) -> bool:
        goal_target_determiner = get_goal_target_determiner(self.current_goal_type)
        is_available = goal_target_determiner(reaper_q_state, current_target.type)
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

    def initialize_new_target(
        self, reaper_goal_type: ReaperActionTypes, reaper_q_state: ReaperQState
    ) -> SelectedTargetInformation | None:
        target_tracker = get_target_tracker(reaper_goal_type)
        self._target_tracker = target_tracker
        target_id_selector = get_target_id_selector(reaper_goal_type)
        selected_target = target_id_selector(reaper_q_state)
        if not selected_target:
            return None
        self._current_target_info = selected_target
        return selected_target


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


def find_target_grid_unit_state(
    game_grid_information: GameGridInformation, target: SelectedTargetInformation
) -> GridUnitState:
    match target.type:
        case Entity.WRECK:
            wreck_grid_coordinate = game_grid_information.wreck_id_to_grid_coord[target.id]
            possible_wrecks = game_grid_information.wreck_grid_state[wreck_grid_coordinate]
            for wreck in possible_wrecks:
                if wreck.unit.unit_id == target.id:
                    return wreck
        case Entity.REAPER:
            reaper_grid_coordinate = game_grid_information.enemy_reaper_id_to_grid_coord[target.id]
            possible_reapers = game_grid_information.enemy_reaper_grid_state[reaper_grid_coordinate]
            for reaper in possible_reapers:
                if reaper.unit.unit_id == target.id:
                    return reaper
        case Entity.OTHER_ENEMY:
            other_grid_coordinate = game_grid_information.enemy_others_id_to_grid_coord[target.id]
            possible_other_enemies = game_grid_information.enemy_others_grid_state[other_grid_coordinate]
            for other_enemy in possible_other_enemies:
                if other_enemy.unit.unit_id == target.id:
                    return other_enemy
        case _:
            raise ValueError(f'Unknown target type: {target.type}')


class TestReaperGameStateInitializeNewTarget:
    def test_initialize_new_target(self):
        """
        this is something like a smoke test. things are wired up, and it
        validates if all the components are working correctly

        Really bad habit with that if statement
        """
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

        if reaper_game_state.current_goal_type != ReaperActionTypes.wait:
            with pytest.raises(ImpossibleTarget):
                reaper_game_state.initialize_new_target(reaper_game_state.current_goal_type, reaper_q_state)
            return

        reaper_game_state.initialize_new_target(reaper_game_state.current_goal_type, reaper_q_state)
        assert reaper_game_state.is_on_mission() is True
        assert reaper_game_state.current_goal_type is not None
        assert isinstance(reaper_game_state.current_goal_type, ReaperActionTypes)
        assert reaper_game_state._target_tracker is not None
        assert reaper_game_state._target_tracker.steps_taken == 0
        assert reaper_game_state._current_target_entity_type is None
