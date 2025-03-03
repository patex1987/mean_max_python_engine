import pytest

from python_prototypes.reaper.exception_types import ImpossibleTarget
from python_prototypes.reaper.q_orchestrator import ReaperGameState
from python_prototypes.reaper.q_state_types import (
    ReaperQState,
    get_default_water_relations,
    get_default_enemies_relation,
    ReaperActionTypes,
)


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
        assert reaper_game_state.target_tracker is not None
        assert reaper_game_state.target_tracker.steps_taken == 0
