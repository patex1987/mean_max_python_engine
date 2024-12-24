from python_prototypes.reaper.q_state_types import ReaperActionTypes


def get_goal_reached_determiner(current_goal: ReaperActionTypes):
    match current_goal:
        case ReaperActionTypes.harvest_safe:
            return
        case ReaperActionTypes.harvest_risky:
            return
        case ReaperActionTypes.harvest_dangerous:
            return
        case ReaperActionTypes.ram_reaper_close:
            return
        case ReaperActionTypes.ram_reaper_mid:
            return
        case ReaperActionTypes.ram_reaper_far:
            return
        case ReaperActionTypes.ram_other_close:
            return
        case ReaperActionTypes.ram_other_mid:
            return
        case ReaperActionTypes.ram_other_far:
            return
        case ReaperActionTypes.use_super_power:
            return
        case ReaperActionTypes.wait:
            return
        case ReaperActionTypes.move_tanker_safe:
            return
        case ReaperActionTypes.move_tanker_risky:
            return
        case ReaperActionTypes.move_tanker_dangerous:
            return
        case _:
            raise ValueError(f'Invalid goal type: {current_goal}')
