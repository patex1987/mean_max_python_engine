

import math
import random
from enum import Enum
from typing import Optional

from python_prototypes.field_tools import get_grid_position, get_manhattan_distance, get_euclidean_distance
from python_prototypes.field_types import Entity, Unit, GridUnitState
from python_prototypes.throttle_optimization import genetic_algorithm, FITNESS_SCORE_TYPE

GRID_COORD_UNIT_STATE_T = dict[tuple[int, int], list[GridUnitState]]


def get_next_destroyer_state(
    current_destroyer_state: 'DestroyerState',
    rage_state: int,
    full_grid_state: GRID_COORD_UNIT_STATE_T,
    enemy_grid_state: GRID_COORD_UNIT_STATE_T,
    tanker_grid_positions: list[GridUnitState],
    tanker_grid_water_summary: dict[tuple[int, int], int],
) -> str:
    """
    Selects a tanker object to aim for using the selection weights
    if a valid tanker is selected, calculates the throttle sequences
    to reach it. Constructs the movement string for the first step in
    the throttle sequence and returns it as the next step

    :param current_destroyer_state:
    :param rage_state:
    :param full_grid_state:
    :param enemy_grid_state:
    :param tanker_grid_positions:
    :param tanker_grid_water_summary:
    :return:

    TODO: incorporate tar and oil into the logic
    TODO: currently returns a string, but it needs to return the new state as well (try to avoid mutations)
    """
    current_position = Coordinate(current_destroyer_state.x, current_destroyer_state.y)
    current_grid = get_grid_position(coordinate=(current_destroyer_state.x, current_destroyer_state.y))
    in_a_tar_pool = is_in_tar_pool(current_position)
    in_an_oil_spill = is_in_oil_spill(current_position)
    nitro_grenade_available = is_nitro_grenade_available(current_destroyer_state, rage_state)

    target_tanker_type = select_tanker_target_type(PLAYER_TANKER_SELECTION_WEIGHTS)
    target_tanker_grid_position = find_tanker_target(
        current_grid, enemy_grid_state, tanker_grid_water_summary, target_tanker_type
    )

    target_object = get_tanker_object_from_grid(full_grid_state, target_tanker_grid_position)
    fastest_throttles_to_target = None
    best_throttles_to_target = None
    next_step = get_next_step(
        PLAYER_DESTROYER_DECISION_WEIGHTS,
        fastest_path_available=False,
        best_path_available=False,
        skill_available=nitro_grenade_available,
    )
    if not target_object:
        if next_step == DestroyerDecisionResult.SKILL:
            raise ValueError('Skill is not supported without a target object')
        wait_string = 'WAIT'
        return wait_string

    v0 = math.sqrt(current_destroyer_state.vx**2 + current_destroyer_state.vy**2)
    target_distance = get_euclidean_distance(
        (current_destroyer_state.x, current_destroyer_state.y), (target_object.unit.x, target_object.unit.y)
    )

    next_step = get_next_step(
        PLAYER_DESTROYER_DECISION_WEIGHTS,
        fastest_path_available=True,
        best_path_available=True,
        skill_available=nitro_grenade_available,
    )
    throttle_sequence = get_throttle_sequence_for_next_step(
        current_destroyer_state, next_step, target_distance, v0
    )
    next_move_command_string = get_next_move_string(
        next_step, target_object, throttle_sequence
    )
    return next_move_command_string


def get_throttle_sequence_for_next_step(
    current_destroyer_state, next_step, target_distance, v0
) -> Optional[tuple[Optional[list[int]], Optional[FITNESS_SCORE_TYPE]]]:
    if next_step == DestroyerDecisionResult.FASTEST_PATH:
        # this is counting with a straight line to the goal
        # TODO: move the genetic algorithm configs to a dedicated class
        throttle_sequence = genetic_algorithm(
            v0,
            current_destroyer_state.mass,
            current_destroyer_state.friction,
            target_distance,
            v_threshold=5,
            max_t=50,
            throttle_range=(0, 300),
            pop_size=1000,
            num_generations=100,
            mutation_rate=0.1,
            num_best_parents=20,
            num_worst_parents=10,
            distance_weigth=1,
            speed_weight=0.001,
            length_weight=0.001,
            nonzero_weight=0.001,
            timeout_ms=300,
        )
        return throttle_sequence
    if next_step == DestroyerDecisionResult.BEST_PATH:
        throttle_sequence = genetic_algorithm(
            v0,
            current_destroyer_state.mass,
            current_destroyer_state.friction,
            target_distance,
            v_threshold=3,
            max_t=50,
            throttle_range=(0, 300),
            pop_size=100,
            num_generations=100,
            mutation_rate=0.1,
            num_best_parents=20,
            num_worst_parents=10,
            distance_weigth=0.5,
            speed_weight=0.6,
            length_weight=0.3,
            nonzero_weight=0.3,
            timeout_ms=300,
        )
        return throttle_sequence
    return None


def find_tanker_target(
    current_grid, enemy_grid_state, tanker_grid_water_summary, target_tanker_type
) -> tuple[int, int]:
    """
    finds the grid position of the target tanker

    :param current_grid:
    :param enemy_grid_state:
    :param tanker_grid_water_summary:
    :param target_tanker_type:
    :return:
    """
    match target_tanker_type:
        case TankerTargetType.HIGH_REWARD:
            target_tanker_grid_position = get_high_reward_tanker_grid(tanker_grid_water_summary)
        case TankerTargetType.OPTIMAL_REWARD:
            target_tanker_grid_position = get_optimal_reward_tanker_grid(
                current_grid, tanker_grid_water_summary, enemy_grid_state, PLAYER_OPTIMAL_TANKER_REWARD_WEIGHTS
            )
        case TankerTargetType.CLOSEST:
            target_tanker_grid_position = get_optimal_reward_tanker_grid(
                current_grid, tanker_grid_water_summary, enemy_grid_state, DISTANCE_TANKER_REWARD_WEIGHTS
            )
        case _:
            raise ValueError('Invalid target tanker type')

    return target_tanker_grid_position


def get_next_move_string(
    next_step: 'DestroyerDecisionResult',
    target_object: GridUnitState,
    throttle_sequence
) -> str:
    match next_step:
        case DestroyerDecisionResult.FASTEST_PATH:
            move_string = '{} {} {} Destroyer'.format(
                target_object.unit.x, target_object.unit.y, throttle_sequence[0][0]
            )
            return move_string
        case DestroyerDecisionResult.BEST_PATH:
            move_string = '{} {} {} Destroyer'.format(
                target_object.unit.x, target_object.unit.y, throttle_sequence[0][0]
            )
            return move_string
        case DestroyerDecisionResult.SKILL:
            skill_string = 'SKILL {} {} Destroyer'.format(target_object.unit.x, target_object.unit.y)
            return skill_string
        case DestroyerDecisionResult.WAIT:
            wait_string = 'WAIT'
            return wait_string
        case _:
            raise ValueError("Invalid decision result")


class TankerSelectionWeights:
    def __init__(self, high_reward, optimal_reward, closest):
        self.high_reward = high_reward
        self.optimal_reward = optimal_reward
        self.closest = closest


class DestroyerDecisionResult(Enum):

    FASTEST_PATH = 1
    BEST_PATH = 2
    SKILL = 3
    WAIT = 4


class DestroyerDecisionWeights:
    def __init__(self, fastest_path, best_path, skill, wait):
        self.fastest_path = fastest_path
        self.best_path = best_path
        self.skill = skill
        self.wait = wait


PLAYER_TANKER_SELECTION_WEIGHTS = TankerSelectionWeights(high_reward=0.1, optimal_reward=0.6, closest=0.3)
PLAYER_DESTROYER_DECISION_WEIGHTS = DestroyerDecisionWeights(fastest_path=0.2, best_path=0.4, skill=0.3, wait=0.1)


class TankerTargetType(Enum):
    HIGH_REWARD = 1
    OPTIMAL_REWARD = 2
    CLOSEST = 3


def select_tanker_target_type(tanker_selection_weights) -> TankerTargetType:
    target_type = random.choices(
        population=[
            TankerTargetType.HIGH_REWARD,
            TankerTargetType.OPTIMAL_REWARD,
            TankerTargetType.CLOSEST,
        ],
        weights=[
            tanker_selection_weights.high_reward,
            tanker_selection_weights.optimal_reward,
            tanker_selection_weights.closest,
        ],
        k=1,
    )[0]
    return target_type


def select_target_tanker(
    high_reward_tanker_grid_position,
    low_reward_tanker_grid_position,
    closest_tanker_grid_position,
    tanker_selection_weights,
):
    target = random.choices(
        population=[high_reward_tanker_grid_position, low_reward_tanker_grid_position, closest_tanker_grid_position],
        weights=[
            tanker_selection_weights.high_reward,
            tanker_selection_weights.optimal_reward,
            tanker_selection_weights.closest,
        ],
        k=1,
    )[0]
    return target


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def is_in_tar_pool(current_position):
    return False


def is_in_oil_spill(current_position):
    return False


class DestroyerState:
    def __init__(self, x, y, vx, vy, radius):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.friction = 0.3
        self.max_throttle = 300
        self.mass = 1.0

    def __repr__(self):
        return (
            f"DestroyerState("
            f"x={self.x:.02f}, "
            f"y={self.y:.02f}, "
            f"vx={self.vx:.02f}, "
            f"vy={self.vy:.02f}, "
            f"radius={self.radius}, "
            f"mass={self.mass})"
        )


def is_nitro_grenade_available(current_destroyer_state, rage_state):
    if rage_state >= 60:
        return True
    return False


def get_high_reward_tanker_grid(tanker_grid_water_summary: dict[tuple[int, int], int]):
    """ """
    return max(tanker_grid_water_summary, key=lambda x: tanker_grid_water_summary[x])


class OptimalTankerRewardWeights:
    def __init__(self, water_gain, destroyer_0, destroyer_1, destroyer_2, distance):
        self.water_gain = water_gain
        self.destroyer_0 = destroyer_0
        self.destroyer_1 = destroyer_1
        self.destroyer_2 = destroyer_2
        self.distance = distance


PLAYER_OPTIMAL_TANKER_REWARD_WEIGHTS = OptimalTankerRewardWeights(
    water_gain=0.2, destroyer_0=0.5, destroyer_1=0.4, destroyer_2=0.3, distance=0.2
)
DISTANCE_TANKER_REWARD_WEIGHTS = OptimalTankerRewardWeights(
    water_gain=0.0, destroyer_0=0.0, destroyer_1=0.0, destroyer_2=0.0, distance=1.0
)


def get_neighboring_enemies(explored_grid, enemy_grid_state, enemy_types, depth):
    if depth == 0:
        enemies = enemy_grid_state.get(explored_grid, [])
        selected_enemies = [enemy for enemy in enemies if enemy.unit.unit_type in enemy_types]
        return len(selected_enemies)

    enemy_count = 0

    # Add neighboring cells around each destroyer to check for threats
    for dx in range(-depth, depth + 1):
        for dy in range(-depth, depth + 1):
            distance = abs(dx) + abs(dy)
            if distance != depth:
                continue
            cell = (explored_grid[0] + dx, explored_grid[1] + dy)
            enemies = enemy_grid_state.get(cell, [])
            selected_enemies = [enemy for enemy in enemies if enemy.unit.unit_type in enemy_types]
            enemy_count += len(selected_enemies)
    return enemy_count


def get_optimal_reward_tanker_grid(
    player_current_grid,
    tanker_grid_water_summary: dict[tuple[int, int], int],
    enemy_grid_state,
    tanker_reward_weights: OptimalTankerRewardWeights,
) -> Optional[tuple[int, int]]:
    optimal_reward_tanker_position = None
    best_score = None
    for explored_grid, water_content in tanker_grid_water_summary.items():
        neighboring_destroyers_level_0 = get_neighboring_enemies(
            explored_grid, enemy_grid_state, enemy_types=[Entity.DESTROYER.value], depth=0
        )
        neighboring_destroyers_level_1 = get_neighboring_enemies(
            explored_grid, enemy_grid_state, enemy_types=[Entity.DESTROYER.value], depth=1
        )
        grid_distance = get_manhattan_distance(player_current_grid, explored_grid)

        coordinate_score = (
            tanker_reward_weights.water_gain * water_content
            - tanker_reward_weights.destroyer_0 * neighboring_destroyers_level_0
            - tanker_reward_weights.destroyer_1 * neighboring_destroyers_level_1
            - tanker_reward_weights.distance * grid_distance
        )
        if best_score is None:
            best_score = coordinate_score
            optimal_reward_tanker_position = explored_grid
            continue

        if coordinate_score > best_score:
            best_score = coordinate_score
            optimal_reward_tanker_position = explored_grid

    if optimal_reward_tanker_position is None:
        return None
    return optimal_reward_tanker_position


def get_tanker_object_from_grid(full_grid_state, target_tanker_grid) -> Optional[GridUnitState]:
    entitites = full_grid_state.get(target_tanker_grid, [])
    tankers = [entity for entity in entitites if entity.unit.unit_type == Entity.TANKER.value]
    if not tankers:
        return None
    return random.choice(tankers)


def get_next_step(
    destroyer_decision_weights: DestroyerDecisionWeights, fastest_path_available, best_path_available, skill_available
) -> DestroyerDecisionResult:

    if not fastest_path_available and not best_path_available:
        choice = random.choices(
            population=[
                DestroyerDecisionResult.SKILL,
                DestroyerDecisionResult.WAIT,
            ],
            weights=[
                destroyer_decision_weights.skill,
                destroyer_decision_weights.wait,
            ],
            k=1,
        )[0]
        if choice == DestroyerDecisionResult.SKILL and not skill_available:
            choice = DestroyerDecisionResult.WAIT

        return choice

    choice = random.choices(
        population=[
            DestroyerDecisionResult.FASTEST_PATH,
            DestroyerDecisionResult.BEST_PATH,
            DestroyerDecisionResult.SKILL,
            DestroyerDecisionResult.WAIT,
        ],
        weights=[
            destroyer_decision_weights.fastest_path,
            destroyer_decision_weights.best_path,
            destroyer_decision_weights.skill,
            destroyer_decision_weights.wait,
        ],
        k=1,
    )[0]
    if choice == DestroyerDecisionResult.SKILL and not skill_available:
        choice = DestroyerDecisionResult.WAIT
    return choice


### test ideas
class TestGetOptimalRewardTankerGrid:

    def test_closest_distance(self):
        current_grid = (3, 4)
        tanker_grid_water_summary = {(3, 4): 10, (2, 1): 4}
        enemy_destroyer_1 = Unit(
            unit_type=Entity.DESTROYER.value,
            x=3,
            y=4,
            vx=0,
            vy=0,
            radius=1,
        )
        enemy_destroyer_2 = Unit(
            unit_type=Entity.DESTROYER.value,
            x=4,
            y=2,
            vx=0,
            vy=0,
            radius=1,
        )
        enemy_grid_state = {
            (3, 4): [GridUnitState((3, 4), enemy_destroyer_1)],
            (3, 3): [GridUnitState((3, 3), enemy_destroyer_2)],
        }
        optimal_tanker_position = get_optimal_reward_tanker_grid(
            current_grid,
            tanker_grid_water_summary,
            enemy_grid_state,
            tanker_reward_weights=DISTANCE_TANKER_REWARD_WEIGHTS,
        )
        assert optimal_tanker_position == (3, 4)

    def test_safe_decision(self):
        current_grid = (0, 0)
        tanker_grid_water_summary = {(3, 4): 10, (2, 1): 4}
        enemy_destroyer_1 = Unit(
            unit_type=Entity.DESTROYER.value,
            x=3,
            y=4,
            vx=0,
            vy=0,
            radius=1,
        )
        enemy_destroyer_2 = Unit(
            unit_type=Entity.DESTROYER.value,
            x=4,
            y=2,
            vx=0,
            vy=0,
            radius=1,
        )
        enemy_grid_state = {
            (3, 4): [GridUnitState((3, 4), enemy_destroyer_1)],
            (3, 3): [GridUnitState((3, 3), enemy_destroyer_2)],
        }
        optimal_tanker_position = get_optimal_reward_tanker_grid(
            current_grid,
            tanker_grid_water_summary,
            enemy_grid_state,
            tanker_reward_weights=DISTANCE_TANKER_REWARD_WEIGHTS,
        )
        assert optimal_tanker_position == (2, 1)


class TestGetNextDestroyerState:

    def test_happy_path(self):
        current_destroyer_state = DestroyerState(
            x=200,
            y=200,
            vx=0,
            vy=0,
            radius=30,
        )
        rage_state = 0
        full_grid_state = {
            (0, 0): [
                GridUnitState((0, 0), Unit(unit_type=Entity.DESTROYER.value, x=200, y=200, vx=0, vy=0, radius=30))
            ],
            (2, 0): [
                GridUnitState(
                    (2, 0), Unit(unit_type=Entity.TANKER.value, x=1400, y=200, vx=-0.98994, vy=-0.141421, radius=30)
                )
            ],
            (2, 2): [
                GridUnitState((2, 2), Unit(unit_type=Entity.DESTROYER.value, x=1400, y=1400, vx=0, vy=0, radius=30)),
                GridUnitState(
                    (2, 2), Unit(unit_type=Entity.TANKER.value, x=1300, y=1300, vx=-0.707, vy=-0.707, radius=30)
                ),
            ],
            (3, 2): [GridUnitState((3, 2), Unit(unit_type=Entity.DOOF.value, x=1300, y=1300, vx=0, vy=0, radius=30))],
            (2, 3): [
                GridUnitState((2, 3), Unit(unit_type=Entity.DESTROYER.value, x=1400, y=2000, vx=0, vy=0, radius=30)),
            ],
        }

        enemy_grid_state = {
            (2, 2): [
                GridUnitState((2, 2), Unit(unit_type=Entity.DESTROYER.value, x=1400, y=1400, vx=0, vy=0, radius=30)),
            ],
            (3, 2): [GridUnitState((3, 2), Unit(unit_type=Entity.DOOF.value, x=1300, y=1300, vx=0, vy=0, radius=30))],
            (2, 3): [
                GridUnitState((2, 3), Unit(unit_type=Entity.DESTROYER.value, x=1400, y=2000, vx=0, vy=0, radius=30)),
            ],
        }
        tanker_grid_positions = [
            GridUnitState((2, 0), Unit(unit_type=Entity.TANKER.value, x=1400, y=200, vx=0, vy=0, radius=30)),
            GridUnitState((2, 2), Unit(unit_type=Entity.TANKER.value, x=1300, y=1300, vx=0, vy=0, radius=30)),
        ]
        tanker_grid_water_summary = {(2, 0): 10, (2, 2): 20}
        next_step = get_next_destroyer_state(
            current_destroyer_state=current_destroyer_state,
            rage_state=rage_state,
            full_grid_state=full_grid_state,
            enemy_grid_state=enemy_grid_state,
            tanker_grid_positions=tanker_grid_positions,
            tanker_grid_water_summary=tanker_grid_water_summary,
        )

        print(next_step)
        assert next_step is not None
