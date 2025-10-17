from python_prototypes.tanker_simulation import (
    TankerState,
    get_next_tanker_state,
    is_inside_playfield,
    get_grid_position,
)


class TestTanker:
    def test_main_runner(self):
        """
        Just emulates the movement of the tanker. Moving to the center of
        the playfield, and the turning around, and exiting once it reaches
        the limits of the playfield

        TODO: add actual assertions to the test
        """
        tanker_state = TankerState(
            x=0,
            y=-6000,
            vx=0,
            vy=1,
            radius=30,
            water_capacity=10,
            water_quantity=0,
        )
        for i in range(100):
            tanker_state = get_next_tanker_state(tanker_state)
            inside_playfield = is_inside_playfield(tanker_state.x, tanker_state.y)
            if not inside_playfield:
                print(
                    f"tanker exited the field, it ceased to exist, last state: {tanker_state!r}, grid position: {get_grid_position((tanker_state.x, tanker_state.y))}"
                )
                break
            print(f"[Round {i}] {tanker_state!r}, grid position: {get_grid_position((tanker_state.x, tanker_state.y))}")
