from python_prototypes.field_tools import calculate_speed_from_vectors, get_euclidean_distance
from python_prototypes.reaper.decision_maker import ReaperDecisionType
from python_prototypes.reaper.long_term_tracker.determiner import (
    get_success_long_term_tracker,
    get_failure_long_term_tracker,
)
from python_prototypes.reaper.path_planner import StrategyPath, get_reaper_planner
from python_prototypes.throttle_optimization import ThrottleCalculationInput
from python_prototypes.unit_parameters import UnitFriction


class DefaultReaperSrategyPathDecider:

    @classmethod
    def reaper_get_strategy_path(
        cls, original_mission_steps, original_target, latest_goal_type, player_state, reaper_decision, reaper_game_state
    ) -> StrategyPath:
        """
        Get the strategy path (throttles) to reach the target

        creates the long term trackers for new targets

        :param original_mission_steps:
        :param original_target:
        :param latest_goal_type:
        :param player_state:
        :param reaper_decision:
        :param reaper_game_state:
        :return:
        """
        match reaper_decision.decision_type:
            case ReaperDecisionType.existing_target:
                strategy_path = reaper_game_state._planned_game_output_path
            case ReaperDecisionType.replan_existing_target:
                planner = get_reaper_planner(reaper_decision.goal_action_type)
                v0 = calculate_speed_from_vectors(
                    vx=player_state.reaper_state.unit.vx,
                    vy=player_state.reaper_state.unit.vy,
                )
                distance_to_target = get_euclidean_distance(
                    coordinate_a=(player_state.reaper_state.unit.x, player_state.reaper_state.unit.y),
                    coordinate_b=(reaper_decision.target_grid_unit.unit.x, reaper_decision.target_grid_unit.unit.y),
                )
                reaper_throttle_calculation_input = ThrottleCalculationInput(
                    v0=v0,
                    mass=player_state.reaper_state.unit.mass,
                    friction=UnitFriction.reaper,
                    d_target=distance_to_target,
                )
                strategy_path = planner.get_path(reaper_throttle_calculation_input)
            case (
                ReaperDecisionType.new_target_on_failure
                | ReaperDecisionType.new_target_on_success
                | ReaperDecisionType.new_target_on_undefined
            ):
                long_term_tracker = None
                if reaper_decision.decision_type == ReaperDecisionType.new_target_on_success:
                    long_term_tracker = get_success_long_term_tracker(
                        original_target, original_mission_steps, latest_goal_type
                    )
                if reaper_decision.decision_type == ReaperDecisionType.new_target_on_failure:
                    long_term_tracker = get_failure_long_term_tracker(
                        original_target, original_mission_steps, latest_goal_type
                    )

                reaper_game_state.register_long_term_tracker(long_term_tracker, original_target)

                planner = get_reaper_planner(reaper_decision.goal_action_type)
                v0 = calculate_speed_from_vectors(
                    vx=player_state.reaper_state.unit.vx,
                    vy=player_state.reaper_state.unit.vy,
                )
                distance_to_target = get_euclidean_distance(
                    coordinate_a=(player_state.reaper_state.unit.x, player_state.reaper_state.unit.y),
                    coordinate_b=(reaper_decision.target_grid_unit.unit.x, reaper_decision.target_grid_unit.unit.y),
                )
                reaper_throttle_calculation_input = ThrottleCalculationInput(
                    v0=v0,
                    mass=player_state.reaper_state.unit.mass,
                    friction=UnitFriction.reaper,
                    d_target=distance_to_target,
                )
                strategy_path = planner.get_path(reaper_throttle_calculation_input)
            case _:
                raise ValueError(f"Unknown decision type: {reaper_decision.decision_type}")
        return strategy_path
