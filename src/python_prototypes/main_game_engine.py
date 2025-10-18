import sys
from dataclasses import dataclass
from typing import Type

from python_prototypes.field_types import (
    GameGridInformation,
    PlayerState,
    GRID_COORD_UNIT_STATE_T,
    GridUnitState,
    Entity,
    PlayerFieldTypes,
)
from python_prototypes.reaper.decision_maker import MainReaperDecider
from python_prototypes.reaper.input_to_q_state import calculate_reaper_q_state
from python_prototypes.reaper.q_orchestrator import ReaperGameState
from python_prototypes.reaper.strategy_path_decider import (
    DefaultReaperSrategyPathDecider,
)


class MainGameEngine:
    def __init__(
        self,
        reaper_game_state: ReaperGameState,
        reaper_strategy_path_decider: Type[DefaultReaperSrategyPathDecider] = DefaultReaperSrategyPathDecider,
    ):
        self._round_nr = 0
        self._q_table_reported = False
        self.reaper_game_state = reaper_game_state
        self.reaper_strategy_path_decider = reaper_strategy_path_decider
        self.player_prev_score = None
        self.player_prev_rage = None
        self.enemy_1_prev_score = None
        self.enemy_1_prev_rage = None
        self.enemy_2_prev_score = None
        self.enemy_2_prev_rage = None

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
        enemy_id_to_entities: dict[int, dict[Entity, GridUnitState]],
        enemy_1_score: int,
        enemy_2_score: int,
        enemy_1_rage: int,
        enemy_2_rage: int,
    ) -> 'GameRoundCommand':
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
        :param enemy_id_to_entities:
        :param enemy_1_score:
        :param enemy_2_score:
        :param enemy_1_rage:
        :param enemy_2_rage:
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
            prev_score=self.player_prev_score,
            prev_rage=self.player_prev_rage,
        )
        enemy_1_raw_info = enemy_id_to_entities[PlayerFieldTypes.ENEMY_1.value]
        enemy_1_state = PlayerState(
            reaper_state=enemy_1_raw_info[Entity.REAPER],
            destroyer_state=enemy_1_raw_info[Entity.DESTROYER],
            doof_state=enemy_1_raw_info[Entity.DOOF],
            rage=enemy_1_score,
            score=enemy_1_rage,
            prev_score=self.enemy_1_prev_score,
            prev_rage=self.enemy_1_prev_rage,
        )
        enemy_2_raw_info = enemy_id_to_entities[PlayerFieldTypes.ENEMY_2.value]
        enemy_2_state = PlayerState(
            reaper_state=enemy_2_raw_info[Entity.REAPER],
            destroyer_state=enemy_2_raw_info[Entity.DESTROYER],
            doof_state=enemy_2_raw_info[Entity.DOOF],
            rage=enemy_2_score,
            score=enemy_2_rage,
            prev_score=self.enemy_2_prev_score,
            prev_rage=self.enemy_2_prev_rage,
        )
        round_command = self.run_round(game_grid_information, player_state, enemy_1_state, enemy_2_state)

        self.player_prev_score = my_score
        self.player_prev_rage = my_rage
        self.enemy_1_prev_score = enemy_1_score
        self.enemy_1_prev_rage = enemy_1_rage
        self.enemy_2_prev_score = enemy_2_score
        self.enemy_2_prev_rage = enemy_2_rage

        # TODO: takes too much time
        # if not self._q_table_reported and (self._round_nr == 190 or enemy_1_score > 40 or my_score > 40 or enemy_2_score > 40):
        #     self._q_table_reported = True
        #     for q_state, weights in self.reaper_game_state._q_table.items():
        #         print(f"Q table elem: {q_state}\n\t{weights}", file=sys.stderr, flush=True)
        #

        self._round_nr += 1
        return round_command

    def run_round(
        self,
        game_grid_information: GameGridInformation,
        player_state: PlayerState,
        enemy_1_state: PlayerState,
        enemy_2_state: PlayerState,
    ) -> 'GameRoundCommand':
        reaper_q_state = calculate_reaper_q_state(
            game_grid_information=game_grid_information, player_state=player_state
        )
        original_target = self.reaper_game_state.current_target_info
        original_mission_steps = self.reaper_game_state._mission_steps
        latest_goal_type = self.reaper_game_state.current_goal_type

        reaper_decider = MainReaperDecider()
        reaper_decision = reaper_decider.decide(
            reaper_game_state=self.reaper_game_state,
            reaper_q_state=reaper_q_state,
            game_grid_information=game_grid_information,
            player_state=player_state,
        )

        print(
            f"[MAIN] reaper decision: {reaper_decision.decision_type}, {reaper_decision.goal_action_type}, {reaper_decision.target_grid_unit.unit.unit_id}",
            file=sys.stderr,
            flush=True,
        )

        strategy_path = self.reaper_strategy_path_decider.reaper_get_strategy_path(
            original_mission_steps=original_mission_steps,
            original_target=original_target,
            latest_goal_type=latest_goal_type,
            player_state=player_state,
            reaper_decision=reaper_decision,
            reaper_game_state=self.reaper_game_state,
        )

        orchestrator = self.reaper_game_state.long_term_reward_tracking_orchestrator
        q_table_changes = orchestrator.orchestrate(
            original_mission_steps,
            player_state,
            enemy_1_state,
            enemy_2_state,
            game_grid_information,
        )
        self.reaper_game_state._q_table.update(q_table_changes)

        reaper_command = "WAIT"
        reaper_next_throttle = strategy_path.get_next_step()
        # TODO: we need a bit more advanced storage and we need to store the full commands not just the throttles
        self.reaper_game_state._planned_game_output_path = strategy_path

        if reaper_next_throttle:
            x, y = reaper_decision.target_grid_unit.unit.x, reaper_decision.target_grid_unit.unit.y
            reaper_command = f"{x} {y} {reaper_next_throttle}"
        return GameRoundCommand(
            reaper_command=reaper_command,
        )


@dataclass
class GameRoundCommand:
    reaper_command: str = "WAIT"
    destroyer_command: str = "WAIT"
    doof_command: str = "WAIT"
