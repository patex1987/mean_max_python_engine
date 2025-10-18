from python_prototypes.reaper.long_term_tracker.tracker_units import (
    HarvestSuccessTracker,
    RamReaperSuccessTracker,
)
from python_prototypes.reaper.q_state_types import MissionStep, ReaperActionTypes
from python_prototypes.reaper.target_selector import SelectedTargetInformation


def get_success_long_term_tracker(
    original_target: SelectedTargetInformation,
    original_mission_steps: list[MissionStep],
    latest_goal_type: ReaperActionTypes,
):
    """
        TODO: you can just extract the first part of the action (like harvest
            or ram) and use the corresponding tracker
    o
        :param original_target:
        :param original_mission_steps:
        :param latest_gal_type:
        :return:
    """
    match latest_goal_type:
        case ReaperActionTypes.harvest_safe:
            return HarvestSuccessTracker(original_water_target=original_target)
        case ReaperActionTypes.harvest_risky:
            return HarvestSuccessTracker(original_water_target=original_target)
        case ReaperActionTypes.harvest_dangerous:
            return HarvestSuccessTracker(original_water_target=original_target)

        case ReaperActionTypes.ram_reaper_close:
            return RamReaperSuccessTracker(original_reaper_target=original_target)
        case ReaperActionTypes.ram_reaper_mid:
            return RamReaperSuccessTracker(original_reaper_target=original_target)
        case ReaperActionTypes.ram_reaper_far:
            return RamReaperSuccessTracker(original_reaper_target=original_target)

        case ReaperActionTypes.ram_other_close:
            # ram
            # Note: maybe we can remove this action completely, maybe wont add too much value
            # check for 3 rounds:
            # - doof
            #     - did it run into the players objects
            #     - did it use super powers?
            #     - did it gain rage?
            #         - backpropagate some smaller amount of loss
            #     - did it create an oil pool? did the oil pool affect your reaper?
            #         - How? need to detect appearance of new oil pools. Correlate the new oil pool's position to the enemy's doof. Close means it was created by that doof
            #         - then, check the manhattan distance between that oil pool and your reaper. If their distance is 0, check the real distance. If you detect that its affected, means the long term success tracker failed, and you failed the mission. Most probably you need to backpropagate some failure
            #         - if the oil pool affected some other entity of yours, expire the long term success tracker, and apply a smaller loss then in the case of the reaper
        #   #     - if none of the above happened apply some gain (but this must be smaller than the water reward or the ram reaper reward)
            pass
        case ReaperActionTypes.ram_other_mid:
            pass
        case ReaperActionTypes.ram_other_far:
            pass
        case ReaperActionTypes.use_super_power:
            pass
        case ReaperActionTypes.wait:
            # nothing to do here
            pass
        case ReaperActionTypes.move_tanker_safe:
            # check for 10 rounds if it was able to suck water from these tankers
            pass
        case ReaperActionTypes.move_tanker_risky:
            pass
        case ReaperActionTypes.move_tanker_dangerous:
            pass


def get_failure_long_term_tracker(
    original_target: SelectedTargetInformation,
    original_mission_steps: list[MissionStep],
    latest_goal_type: ReaperActionTypes,
):
    match latest_goal_type:
        case ReaperActionTypes.harvest_safe:
            # harvest - check for 5 rounds
            # - did the enemy gain water?
            #     - if yes, did it gain water from this wreck
            pass
        case ReaperActionTypes.harvest_risky:
            pass
        case ReaperActionTypes.harvest_dangerous:
            pass
        case ReaperActionTypes.ram_reaper_close:
            # ram - check for 5 rounds
            # - did the enemy gain water?
            #     - if yes, did the selected reaper gained some water (the above check should be enough, as only the reaper can gain water)
            pass
        case ReaperActionTypes.ram_reaper_mid:
            pass
        case ReaperActionTypes.ram_reaper_far:
            pass
        case ReaperActionTypes.ram_other_close:
            # ram
            #   - check for 5 rounds
            #       - if the enemy gained water
            #       - if yes, then
            #           - target was doof
            #               - did it run into an enemy
            #               - did it increase rage
            #           - target was destroyer
            #               - did it destroy a tanker
            pass
        case ReaperActionTypes.ram_other_mid:
            pass
        case ReaperActionTypes.ram_other_far:
            pass
        case ReaperActionTypes.use_super_power:
            pass
        case ReaperActionTypes.wait:
            # nothing to do here
            pass
        case ReaperActionTypes.move_tanker_safe:
            # nothing to do here
            pass
        case ReaperActionTypes.move_tanker_risky:
            pass
        case ReaperActionTypes.move_tanker_dangerous:
            pass
