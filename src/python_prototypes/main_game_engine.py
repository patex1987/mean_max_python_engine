from python_prototypes.field_types import GameGridInformation, PlayerState, GRID_COORD_UNIT_STATE_T, GridUnitState
from python_prototypes.reaper.decision_maker import reaper_decider, ReaperDecisionType
from python_prototypes.reaper.input_to_q_state import calculate_reaper_q_state
from python_prototypes.reaper.q_orchestrator import ReaperGameState


class MainGameEngine:

    def __init__(self, reaper_game_state: ReaperGameState):
        self.reaper_game_state = reaper_game_state

    def run_round_raw(
        self,
        enemy_others_grid_state: GRID_COORD_UNIT_STATE_T,
        enemy_others_id_to_grid_coord: dict[int, tuple[int, int]],
        enemy_reaper_grid_state: GRID_COORD_UNIT_STATE_T,
        enemy_reaper_id_to_grid_coord: dict[int, tuple[int, int]],
        full_grid_state: dict[tuple[int, int], list[GridUnitState]],
        my_rage: int,
        my_score: int,
        player_destroyer_grid_unit: GridUnitState,
        player_doof_grid_unit: GridUnitState,
        player_reaper_grid_unit: GridUnitState,
        tanker_grid_state: GRID_COORD_UNIT_STATE_T,
        tanker_id_to_grid_coord: dict[int, tuple[int, int]],
        wreck_grid_state: GRID_COORD_UNIT_STATE_T,
        wreck_id_to_grid_coord: dict[int, tuple[int, int]],
        enemy_score_1: int,
        enemy_score_2: int,
        enemy_rage_1: int,
        enemy_rage_2: int,
    ):
        """
        Handles the raw data incoming rom every round in the game

        :param enemy_others_grid_state:
        :param enemy_others_id_to_grid_coord:
        :param enemy_reaper_grid_state:
        :param enemy_reaper_id_to_grid_coord:
        :param full_grid_state:
        :param my_rage:
        :param my_score:
        :param player_destroyer_grid_unit:
        :param player_doof_grid_unit:
        :param player_reaper_grid_unit:
        :param tanker_grid_state:
        :param tanker_id_to_grid_coord:
        :param wreck_grid_state:
        :param wreck_id_to_grid_coord:
        :param enemy_score_1:
        :param enemy_score_2:
        :param enemy_rage_1:
        :param enemy_rage_2:
        :return:

        TODO: use the enemy score and rage values similarly to player state
        """
        game_grid_information = GameGridInformation(
            full_grid_state=full_grid_state,
            wreck_grid_state=wreck_grid_state,
            wreck_id_to_grid_coord=wreck_id_to_grid_coord,
            tanker_grid_state=tanker_grid_state,
            tanker_id_to_grid_coord=tanker_id_to_grid_coord,
            enemy_reaper_grid_state=enemy_reaper_grid_state,
            enemy_reaper_id_to_grid_coord=enemy_reaper_id_to_grid_coord,
            enemy_others_grid_state=enemy_others_grid_state,
            enemy_others_id_to_grid_coord=enemy_others_id_to_grid_coord,
        )
        player_state = PlayerState(
            reaper_state=player_reaper_grid_unit,
            destroyer_state=player_destroyer_grid_unit,
            doof_state=player_doof_grid_unit,
            rage=my_rage,
            score=my_score,
        )
        self.run_round(game_grid_information, player_state)

    def run_round(self, game_grid_information: GameGridInformation, player_state: PlayerState):
        reaper_q_state = calculate_reaper_q_state(
            game_grid_information=game_grid_information, player_state=player_state
        )
        original_target = self.reaper_game_state.current_target_info
        original_mission_steps = self.reaper_game_state._mission_steps

        # TODO: make reaper_decider oop based and add it as a class field,
        #   so you can inject a different implementation in your test
        reaper_decision = reaper_decider(
            reaper_game_state=self.reaper_game_state,
            reaper_q_state=reaper_q_state,
            game_grid_information=game_grid_information,
            player_state=player_state,
        )

        match reaper_decision.decision_type:
            case ReaperDecisionType.existing_target:
                strategy_path = self.reaper_game_state._planned_game_output_path
            case ReaperDecisionType.replan_existing_target:
                strategy_path = ReaperPathPlanner.plan(
                    reaper_decision.goal_action_type, reaper_decision.target_grid_unit
                )
            case (
                ReaperDecisionType.new_target_on_failure
                | ReaperDecisionType.new_target_on_success
                | ReaperDecisionType.new_target_on_undefined
            ):
                long_term_tracker = None
                if reaper_decision.decision_type == ReaperDecisionType.new_target_on_success:
                    long_term_tracker = get_success_long_term_tracker(original_mission_steps)
                if reaper_decision.decision_type == ReaperDecisionType.new_target_on_failure:
                    long_term_tracker = get_failure_long_term_tracker(original_mission_steps)
                self.reaper_game_state.register_long_term_tracker(long_term_tracker, original_target)

                strategy_path = ReaperPathPlanner.plan(
                    reaper_decision.goal_action_type, reaper_decision.target_grid_unit
                )
            case _:
                raise ValueError(f"Unknown decision type: {reaper_decision.decision_type}")

        reaper_next_step = strategy_path.get_next_step()
        print(reaper_next_step)
