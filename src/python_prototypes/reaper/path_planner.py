from abc import ABC
from typing import Optional

from python_prototypes.reaper.q_state_types import ReaperActionTypes
from python_prototypes.throttle_optimization import (
    find_optimal_throttle_sequence,
    ThrottleCalculationInput,
    GeneticConfiguration,
)

REAPER_GOAL_ROUND_LIMIT = 12
REAPER_FAST_PATH_CONFIGURATION = GeneticConfiguration(
    speed_threshold=5,
    max_sequence_length=REAPER_GOAL_ROUND_LIMIT,
    throttle_range=(0, 300),
    population_size=1000,
    num_generations=100,
    mutation_rate=0.1,
    num_best_parents=20,
    num_worst_parents=10,
    distance_weight=1,
    speed_weight=0.001,
    length_weight=0.001,
    nonzero_weight=0.001,
    timeout_ms=300,
)
REAPER_BEST_PATH_CONFIGURATION = GeneticConfiguration(
    speed_threshold=3,
    max_sequence_length=50,
    throttle_range=(0, 300),
    population_size=100,
    num_generations=100,
    mutation_rate=0.1,
    num_best_parents=20,
    num_worst_parents=10,
    distance_weight=0.5,
    speed_weight=0.6,
    length_weight=0.3,
    nonzero_weight=0.3,
    timeout_ms=300,
)


class StrategyPath:
    """
    Throttle sequence to get from point A to point B.
    """

    def __init__(self, sequence: list[int]):
        self.sequence = sequence

    def get_next_step(self) -> Optional[int]:
        if not self.sequence:
            return None
        return self.sequence.pop(0)


def get_reaper_planner(goal_action_type: ReaperActionTypes) -> "BaseReaperPathPlanner":
    match goal_action_type:
        case ReaperActionTypes.harvest_safe:
            return GeneticStraightPathPlanner(REAPER_BEST_PATH_CONFIGURATION)
        case ReaperActionTypes.harvest_risky:
            return GeneticStraightPathPlanner(REAPER_BEST_PATH_CONFIGURATION)
        case ReaperActionTypes.harvest_dangerous:
            return GeneticStraightPathPlanner(REAPER_BEST_PATH_CONFIGURATION)
        case ReaperActionTypes.ram_reaper_close:
            return GeneticStraightPathPlanner(REAPER_FAST_PATH_CONFIGURATION)
        case ReaperActionTypes.ram_reaper_mid:
            return GeneticStraightPathPlanner(REAPER_FAST_PATH_CONFIGURATION)
        case ReaperActionTypes.ram_reaper_far:
            return GeneticStraightPathPlanner(REAPER_FAST_PATH_CONFIGURATION)
        case ReaperActionTypes.ram_other_close:
            return GeneticStraightPathPlanner(REAPER_FAST_PATH_CONFIGURATION)
        case ReaperActionTypes.ram_other_mid:
            return GeneticStraightPathPlanner(REAPER_FAST_PATH_CONFIGURATION)
        case ReaperActionTypes.ram_other_far:
            return GeneticStraightPathPlanner(REAPER_FAST_PATH_CONFIGURATION)
        case ReaperActionTypes.use_super_power:
            return StrategyPath([0])
        case ReaperActionTypes.wait:
            return StrategyPath([0])
        case ReaperActionTypes.move_tanker_safe:
            return GeneticStraightPathPlanner(REAPER_FAST_PATH_CONFIGURATION)
        case ReaperActionTypes.move_tanker_risky:
            return GeneticStraightPathPlanner(REAPER_FAST_PATH_CONFIGURATION)
        case ReaperActionTypes.move_tanker_dangerous:
            return GeneticStraightPathPlanner(REAPER_FAST_PATH_CONFIGURATION)
        case _:
            raise ValueError(f"Unknown goal action type: {goal_action_type}")


class BaseReaperPathPlanner(ABC):
    def get_path(self, throttle_game_input) -> StrategyPath:
        pass


class GeneticStraightPathPlanner(BaseReaperPathPlanner):
    def __init__(self, genetic_configuration: GeneticConfiguration):
        self.genetic_configuration = genetic_configuration

    def get_path(self, throttle_game_input: ThrottleCalculationInput) -> StrategyPath:
        sequence_result = find_optimal_throttle_sequence(throttle_calculation_input=throttle_game_input)
        return StrategyPath(sequence_result.sequence)
