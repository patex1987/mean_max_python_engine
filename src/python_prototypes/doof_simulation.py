import math
from enum import Enum

import random

from python_prototypes.field_tools import get_euclidean_distance
from python_prototypes.field_types import GridUnitState
from python_prototypes.throttle_optimization import find_optimal_throttle_sequence


class DoofDecisionResults(Enum):
    CHASE_OPPONENT = 1
    SKILL = 3
    WAIT = 4


class DoofDecisionWeights:
    def __init__(self, chase_opponent, skill, wait):
        self.chase_opponent = chase_opponent
        self.skill = skill
        self.wait = wait


PLAYER_DOOF_DECISION_WEIGHTS = DoofDecisionWeights(chase_opponent=0.7, skill=0.2, wait=0.1)


def select_doof_target_type(doof_selection_weights) -> DoofDecisionResults:
    target_type = random.choices(
        population=[
            DoofDecisionResults.CHASE_OPPONENT,
            DoofDecisionResults.SKILL,
            DoofDecisionResults.WAIT,
        ],
        weights=[
            doof_selection_weights.chase_opponent,
            doof_selection_weights.skill,
            doof_selection_weights.wait,
        ],
    )[0]
    return target_type


def get_next_doof_state(
    current_doof_state, enemy_grid_state: dict[tuple[int, int], list[GridUnitState]], doof_decision_weights
):
    target_type = select_doof_target_type(doof_decision_weights)
    match target_type:
        case DoofDecisionResults.CHASE_OPPONENT:
            selected_enemy_grid_position = select_opponent(
                doof_grid_position, enemy_grid_state, enemy_selection_weights
            )
            target_object = select_enemy_from_grid_position(selected_enemy_grid_position, enemy_grid_state)
            v0 = math.sqrt(current_doof_state.vx**2 + current_doof_state.vy**2)
            target_distance = get_euclidean_distance(
                (current_doof_state.x, current_doof_state.y), (target_object.unit.x, target_object.unit.y)
            )
            throttles_to_target = find_optimal_throttle_sequence()
            next_throttle = throttles_to_target[0]
        case DoofDecisionResults.SKILL:
            current_doof_state = DoofDecisionResults.SKILL
        case DoofDecisionResults.WAIT:
            current_doof_state = DoofDecisionResults.WAIT
