from python_prototypes.real_game_mocks.full_grid_state import ExampleBasicScenarioIncomplete


class TestGameInputHandler:

    def test_get_example_full_grid_state(self):
        game_grid_information = ExampleBasicScenarioIncomplete.get_example_full_grid_state()
        full_grid_state = game_grid_information.full_grid_state

        # print(full_grid_state)
        assert len(full_grid_state[(0, 0)]) == 1
        assert len(full_grid_state[(2, 0)]) == 2
        assert len(full_grid_state[(2, 2)]) == 1
        assert len(full_grid_state[(3, 2)]) == 1
        assert len(full_grid_state[(2, 3)]) == 1

        enemy_other_grid_state = game_grid_information.enemy_others_grid_state
        assert len(enemy_other_grid_state[(0, 0)]) == 1
        assert len(enemy_other_grid_state[(2, 0)]) == 1

        tanker_grid_state = game_grid_information.tanker_grid_state
        assert len(tanker_grid_state[(2, 0)]) == 1
        assert len(tanker_grid_state[(2, 2)]) == 1
