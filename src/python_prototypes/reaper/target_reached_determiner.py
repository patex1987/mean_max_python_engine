def get_goal_reached_determiner(current_goal):
    match current_goal:
        case 'harvest_safe':
            return
        case 'harvest_risky':
            return
        case 'harvest_dangerous':
            return
        case 'ram_reaper_close':
            return
        case 'ram_reaper_mid':
            return
        case 'ram_reaper_far':
            return
        case 'ram_other_close':
            return
        case 'ram_other_mid':
            return
        case 'ram_other_far':
            return
        case 'use_super_power':
            return
        case 'wait':
            return
        case _:
            raise ValueError(f'Invalid goal type: {current_goal}')
