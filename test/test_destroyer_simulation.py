from python_prototypes.destroyer_simulation import (
    get_optimal_reward_tanker_grid,
    DISTANCE_TANKER_REWARD_WEIGHTS,
    DestroyerState,
    get_next_destroyer_state,
)
from python_prototypes.field_types import Unit, Entity, GridUnitState


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
                GridUnitState(
                    (0, 0),
                    Unit(
                        unit_type=Entity.DESTROYER.value,
                        x=200,
                        y=200,
                        vx=0,
                        vy=0,
                        radius=30,
                    ),
                )
            ],
            (2, 0): [
                GridUnitState(
                    (2, 0),
                    Unit(
                        unit_type=Entity.TANKER.value,
                        x=1400,
                        y=200,
                        vx=-0.98994,
                        vy=-0.141421,
                        radius=30,
                    ),
                )
            ],
            (2, 2): [
                GridUnitState(
                    (2, 2),
                    Unit(
                        unit_type=Entity.DESTROYER.value,
                        x=1400,
                        y=1400,
                        vx=0,
                        vy=0,
                        radius=30,
                    ),
                ),
                GridUnitState(
                    (2, 2),
                    Unit(
                        unit_type=Entity.TANKER.value,
                        x=1300,
                        y=1300,
                        vx=-0.707,
                        vy=-0.707,
                        radius=30,
                    ),
                ),
            ],
            (3, 2): [
                GridUnitState(
                    (3, 2),
                    Unit(
                        unit_type=Entity.DOOF.value,
                        x=1300,
                        y=1300,
                        vx=0,
                        vy=0,
                        radius=30,
                    ),
                )
            ],
            (2, 3): [
                GridUnitState(
                    (2, 3),
                    Unit(
                        unit_type=Entity.DESTROYER.value,
                        x=1400,
                        y=2000,
                        vx=0,
                        vy=0,
                        radius=30,
                    ),
                ),
            ],
        }

        enemy_grid_state = {
            (2, 2): [
                GridUnitState(
                    (2, 2),
                    Unit(
                        unit_type=Entity.DESTROYER.value,
                        x=1400,
                        y=1400,
                        vx=0,
                        vy=0,
                        radius=30,
                    ),
                ),
            ],
            (3, 2): [
                GridUnitState(
                    (3, 2),
                    Unit(
                        unit_type=Entity.DOOF.value,
                        x=1300,
                        y=1300,
                        vx=0,
                        vy=0,
                        radius=30,
                    ),
                )
            ],
            (2, 3): [
                GridUnitState(
                    (2, 3),
                    Unit(
                        unit_type=Entity.DESTROYER.value,
                        x=1400,
                        y=2000,
                        vx=0,
                        vy=0,
                        radius=30,
                    ),
                ),
            ],
        }
        tanker_grid_positions = [
            GridUnitState(
                (2, 0),
                Unit(unit_type=Entity.TANKER.value, x=1400, y=200, vx=0, vy=0, radius=30),
            ),
            GridUnitState(
                (2, 2),
                Unit(unit_type=Entity.TANKER.value, x=1300, y=1300, vx=0, vy=0, radius=30),
            ),
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
