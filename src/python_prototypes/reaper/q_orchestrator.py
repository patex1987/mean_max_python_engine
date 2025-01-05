"""
Currently contains q state handling and the reaper decider based on q
learning
"""

import random

import pytest

from python_prototypes.field_types import GridUnitState, GameGridInformation, EntitiesForReaper
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
from python_prototypes.reaper.target_availability_determiner import get_goal_target_determiner, TargetAvailabilityState
from python_prototypes.reaper.target_reached_determiner import get_goal_reached_determiner
from python_prototypes.reaper.target_selector import get_target_id_selector, SelectedTargetInformation
from python_prototypes.reaper.target_tracker_determiner import get_target_tracker, BaseTracker


class ReaperGameState:
    """
    this is transferred between game rounds and can be mutated in an individual round
    """

    def __init__(self):
        self.current_goal_type: ReaperActionTypes | None = None
        self._mission_set = False
        self._current_target_info: SelectedTargetInformation | None = None
        self._current_target_entity_type = None
        # list of q state keys
        # TODO: change this to a set
        self._current_mission_steps: list[tuple] = []
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
        :return:
        """

        # TODO: this is wrong, the current goal type changes every round
        current_goal = self.current_goal_type
        failure_penalty = get_goal_failure_penalty(current_goal)
        for q_state_key in self._current_mission_steps:
            reaper_q_action_weights = self._q_table.setdefault(
                q_state_key, ReaperActionsQWeights(get_default_reaper_actions_q_weights())
            )
            reaper_q_action_weights.inner_weigths_dict[self.current_goal_type] -= failure_penalty

    def propagate_successful_goal(self):
        # TODO: this is wrong, the current goal type changes every round
        current_goal = self.current_goal_type
        success_reward = get_goal_success_reward(current_goal)
        for q_state_key in self._current_mission_steps:
            reaper_q_action_weights = self._q_table.setdefault(
                q_state_key, ReaperActionsQWeights(get_default_reaper_actions_q_weights())
            )
            reaper_q_action_weights.inner_weigths_dict[self.current_goal_type] += success_reward

    def is_goal_possible(self, reaper_q_state: ReaperQState, goal_type: ReaperActionTypes) -> bool:
        """
        TODO: the availability determiner apprach is just one way to achieve this
        """
        goal_possibility_determiner = get_goal_possibility_determiner(goal_type)
        is_possible = goal_possibility_determiner(reaper_q_state)
        return is_possible

    def get_goal_target_availability(
        self,
        target_grid_unit: GridUnitState | None,
        game_grid_information: GameGridInformation,
        tracker: BaseTracker = None,
    ) -> TargetAvailabilityState:
        goal_target_determiner = get_goal_target_determiner(self.current_goal_type)
        is_available = goal_target_determiner(target_grid_unit, game_grid_information, tracker)
        return is_available

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
            self._current_target_info = None
            return None
        self._current_target_info = selected_target
        return selected_target

    def add_current_step_to_mission(self, q_state_key: tuple):
        self._current_mission_steps.append(q_state_key)

    def apply_step_penalty(self, q_state_key: tuple) -> None:
        reaper_q_action_weights = self._q_table.setdefault(
            q_state_key, ReaperActionsQWeights(get_default_reaper_actions_q_weights())
        )
        reaper_q_action_weights.inner_weigths_dict[self.current_goal_type] -= STEP_PENALTY
        return

    def register_q_state(self, q_state_key: tuple) -> None:
        _reaper_q_action_weights = self._q_table.setdefault(
            q_state_key, ReaperActionsQWeights(get_default_reaper_actions_q_weights())
        )
        return


STEP_PENALTY = 0.5


def get_goal_failure_penalty(current_goal: ReaperActionTypes) -> float:
    """
    TODO: add goal specific penalties
    :param current_goal:
    :return:
    """
    return 0.5


def get_goal_success_reward(current_goal: ReaperActionTypes) -> float:
    """
    TODO: add goal specific rewards
    :param current_goal:
    :return:
    """
    return 1.0


def find_target_grid_unit_state(
    game_grid_information: GameGridInformation, target: SelectedTargetInformation
) -> GridUnitState | None:
    match target.type:
        case EntitiesForReaper.WRECK:
            if target.id not in game_grid_information.wreck_id_to_grid_coord:
                return None
            wreck_grid_coordinate = game_grid_information.wreck_id_to_grid_coord[target.id]
            possible_wrecks = game_grid_information.wreck_grid_state[wreck_grid_coordinate]
            for wreck in possible_wrecks:
                if wreck.unit.unit_id == target.id:
                    return wreck
        case EntitiesForReaper.REAPER:
            if target.id not in game_grid_information.enemy_reaper_id_to_grid_coord:
                return None
            reaper_grid_coordinate = game_grid_information.enemy_reaper_id_to_grid_coord[target.id]
            possible_reapers = game_grid_information.enemy_reaper_grid_state[reaper_grid_coordinate]
            for reaper in possible_reapers:
                if reaper.unit.unit_id == target.id:
                    return reaper
            return None
        case EntitiesForReaper.OTHER_ENEMY:
            if target.id not in game_grid_information.enemy_others_id_to_grid_coord:
                return None
            other_grid_coordinate = game_grid_information.enemy_others_id_to_grid_coord[target.id]
            possible_other_enemies = game_grid_information.enemy_others_grid_state[other_grid_coordinate]
            for other_enemy in possible_other_enemies:
                if other_enemy.unit.unit_id == target.id:
                    return other_enemy
            return None
        case EntitiesForReaper.TANKER:
            if target.id not in game_grid_information.tanker_id_to_grid_coord:
                return None
            tanker_grid_coordinate = game_grid_information.tanker_id_to_grid_coord[target.id]
            possible_tankers = game_grid_information.tanker_grid_state[tanker_grid_coordinate]
            for tanker in possible_tankers:
                if tanker.unit.unit_id == target.id:
                    return tanker
            return None
        case _:
            raise ValueError(f'Unknown target type: {target.type}')


def get_updated_goal_type(
    reaper_q_state: ReaperQState, current_target: SelectedTargetInformation, current_goal_type: ReaperActionTypes
) -> ReaperActionTypes:
    """
    while you are moving every round a far risky wreck can become a close
    safe wreck. This function returns the updated state, so the q table
    is filled with up-to-date state

    :param reaper_q_state:
    :param current_target:
    :param current_goal_type:
    :return:
    """
    target_id = current_target.id
    match current_goal_type:
        case ReaperActionTypes.harvest_safe | ReaperActionTypes.harvest_risky | ReaperActionTypes.harvest_dangerous:
            # TODO: remember `goal_possibility_determiner.safe_water_possible` - only reapers are considered yet
            updated_reaper_water_category = reaper_q_state.reaper_water_relation[target_id]
            distance, risk = updated_reaper_water_category
            # TODO: we already have another TODO to this differently, especially don't rely on stupid strings
            harvest_category_name = f'harvest_{risk}'
            harvest_category = ReaperActionTypes[harvest_category_name]
            return harvest_category

        case ReaperActionTypes.ram_reaper_close | ReaperActionTypes.ram_reaper_mid | ReaperActionTypes.ram_reaper_far:
            updated_enemy_other_category = reaper_q_state.reaper_id_category_relation[target_id]
            reaper_distance, water_distance = updated_enemy_other_category
            ram_reaper_category_name = f'ram_reaper_{reaper_distance}'
            ram_category = ReaperActionTypes[ram_reaper_category_name]
            return ram_category

        case ReaperActionTypes.ram_other_close | ReaperActionTypes.ram_other_mid | ReaperActionTypes.ram_other_far:
            updated_enemy_other_category = reaper_q_state.other_id_category_mapping[target_id]
            other_distance, water_distance = updated_enemy_other_category
            ram_other_category_name = f'ram_other_{other_distance}'
            ram_category = ReaperActionTypes[ram_other_category_name]
            return ram_category

        case ReaperActionTypes.use_super_power:
            # TODO: validate and update the target once we have multiple super power types
            return ReaperActionTypes.use_super_power

        case ReaperActionTypes.wait:
            return ReaperActionTypes.wait

        case (
            ReaperActionTypes.move_tanker_safe
            | ReaperActionTypes.move_tanker_risky
            | ReaperActionTypes.move_tanker_dangerous
        ):
            updated_tanker_category = reaper_q_state.tanker_id_enemy_category_relation[target_id]
            distance, risk = updated_tanker_category
            move_tanker_category_name = f'move_tanker_{risk}'
            move_tanker_category = ReaperActionTypes[move_tanker_category_name]
            return move_tanker_category


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
            reaper_water_relation={},
            other_water_relation={},
            tanker_id_enemy_category_relation={},
            reaper_id_category_relation={},
            other_id_category_mapping={},
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
