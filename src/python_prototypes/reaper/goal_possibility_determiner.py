from python_prototypes.reaper.q_state_types import ReaperQState, ReaperActionTypes


def get_goal_possibility_determiner(current_goal: ReaperActionTypes):
    match current_goal:
        case ReaperActionTypes.harvest_safe:
            return safe_water_possible
        case ReaperActionTypes.harvest_risky:
            return risky_water_possible
        case ReaperActionTypes.harvest_dangerous:
            return dangerous_water_possible
        case ReaperActionTypes.ram_reaper_close:
            return close_reaper_possible
        case ReaperActionTypes.ram_reaper_mid:
            return mid_reaper_possible
        case ReaperActionTypes.ram_reaper_far:
            return far_reaper_possible
        case ReaperActionTypes.ram_other_close:
            return close_other_enemy_possible
        case ReaperActionTypes.ram_other_mid:
            return mid_other_enemy_possible
        case ReaperActionTypes.ram_other_far:
            return far_other_enemy_possible
        case ReaperActionTypes.use_super_power:
            return super_power_possible
        case ReaperActionTypes.wait:
            return no_op_possible
        case ReaperActionTypes.move_tanker_safe:
            return safe_tanker_possible
        case ReaperActionTypes.move_tanker_risky:
            return risky_tanker_possible
        case ReaperActionTypes.move_tanker_dangerous:
            return dangerous_tanker_possible
        case _:
            raise ValueError(f"Invalid goal type: {current_goal}")


def safe_water_possible(reaper_q_state: ReaperQState) -> bool:
    """
    TODO: missing the water other enemy relation
    TODO: these availability checks should be made simpler (and most
        probably should be delegated to the relations level (but they
        are currently dictionaries))
    :param reaper_q_state:
    :return:
    """
    available = (
        reaper_q_state.water_reaper_state.get(("close", "safe"), 0) > 0
        or reaper_q_state.water_reaper_state.get(("medium", "safe"), 0) > 0
        or reaper_q_state.water_reaper_state.get(("far", "safe"), 0) > 0
    )
    return available


def risky_water_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.water_reaper_state.get(("close", "risky"), 0) > 0
        or reaper_q_state.water_reaper_state.get(("medium", "risky"), 0) > 0
        or reaper_q_state.water_reaper_state.get(("far", "risky"), 0) > 0
    )
    return available


def dangerous_water_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.water_reaper_state.get(("close", "dangerous"), 0) > 0
        or reaper_q_state.water_reaper_state.get(("medium", "dangerous"), 0) > 0
        or reaper_q_state.water_reaper_state.get(("far", "dangerous"), 0) > 0
    )
    return available


def close_reaper_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.player_reaper_state.get(("close", "close"), 0) > 0
        or reaper_q_state.player_reaper_state.get(("close", "medium"), 0) > 0
    )
    return available


def mid_reaper_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.player_reaper_state.get(("mid", "close"), 0) > 0
        or reaper_q_state.player_reaper_state.get(("mid", "medium"), 0) > 0
    )
    return available


def far_reaper_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.player_reaper_state.get(("far", "close"), 0) > 0
        or reaper_q_state.player_reaper_state.get(("far", "medium"), 0) > 0
    )
    return available


def close_other_enemy_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.player_other_state.get(("close", "close"), 0) > 0
        or reaper_q_state.player_other_state.get(("close", "medium"), 0) > 0
    )
    return available


def mid_other_enemy_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.player_other_state.get(("mid", "close"), 0) > 0
        or reaper_q_state.player_other_state.get(("mid", "medium"), 0) > 0
    )
    return available


def far_other_enemy_possible(reaper_q_state: ReaperQState) -> bool:
    available = (
        reaper_q_state.player_other_state.get(("far", "close"), 0) > 0
        or reaper_q_state.player_other_state.get(("far", "medium"), 0) > 0
    )
    return available


def super_power_possible(reaper_q_state: ReaperQState) -> bool:
    available = reaper_q_state.super_power_available
    return available


def safe_tanker_possible(reaper_q_state: ReaperQState) -> bool:
    """
    :param reaper_q_state:
    :return:
    """
    available = (
        reaper_q_state.tanker_enemy_state.get(("close", "safe"), 0) > 0
        or reaper_q_state.tanker_enemy_state.get(("medium", "safe"), 0) > 0
        or reaper_q_state.tanker_enemy_state.get(("far", "safe"), 0) > 0
    )
    return available


def risky_tanker_possible(reaper_q_state: ReaperQState) -> bool:
    """
    :param reaper_q_state:
    :return:
    """
    available = (
        reaper_q_state.tanker_enemy_state.get(("close", "risky"), 0) > 0
        or reaper_q_state.tanker_enemy_state.get(("medium", "risky"), 0) > 0
        or reaper_q_state.tanker_enemy_state.get(("far", "risky"), 0) > 0
    )
    return available


def dangerous_tanker_possible(reaper_q_state: ReaperQState) -> bool:
    """
    :param reaper_q_state:
    :return:
    """
    available = (
        reaper_q_state.tanker_enemy_state.get(("close", "dangerous"), 0) > 0
        or reaper_q_state.tanker_enemy_state.get(("medium", "dangerous"), 0) > 0
        or reaper_q_state.tanker_enemy_state.get(("far", "dangerous"), 0) > 0
    )
    return available


def no_op_possible(reaper_q_state: ReaperQState) -> bool:
    return True
