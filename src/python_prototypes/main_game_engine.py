from python_prototypes.field_types import GameGridInformation, PlayerState, GRID_COORD_UNIT_STATE_T, GridUnitState
from python_prototypes.reaper.decision_maker import reaper_decider
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
        reaper_decision = reaper_decider(
            reaper_game_state=self.reaper_game_state,
            reaper_q_state=reaper_q_state,
            game_grid_information=game_grid_information,
            player_state=player_state,
        )
