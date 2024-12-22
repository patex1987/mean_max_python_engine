"""
this module contains classes and functions related to represent and
initialize the q state of the game decision learning
"""

def get_default_water_relations() -> dict[tuple[str, str], int]:
    water_reaper_relation = {
        ('close', 'safe'): 0,
        ('close', 'risky'): 0,
        ('close', 'dangerous'): 0,
        ('medium', 'safe'): 0,
        ('medium', 'risky'): 0,
        ('medium', 'dangerous'): 0,
        ('far', 'safe'): 0,
        ('far', 'risky'): 0,
        ('far', 'dangerous'): 0,
    }
    return water_reaper_relation


def get_default_tanker_enemies_relation():
    tanker_enemies_relation = {
        ('close', 'safe'): 0,
        ('close', 'risky'): 0,
        ('close', 'dangerous'): 0,
        ('medium', 'safe'): 0,
        ('medium', 'risky'): 0,
        ('medium', 'dangerous'): 0,
        ('far', 'safe'): 0,
        ('far', 'risky'): 0,
        ('far', 'dangerous'): 0,
    }
    return tanker_enemies_relation


def get_default_enemies_relation() -> dict[tuple[str, str], int]:
    enemies_relation = {
        ('close', 'close'): 0,
        ('close', 'medium'): 0,
        ('medium', 'close'): 0,
        ('medium', 'medium'): 0,
        ('far', 'close'): 0,
        ('far', 'medium'): 0,
    }
    return enemies_relation


def convert_relation_to_tuple_key(relation: dict[tuple[str, str], int]) -> tuple:
    tuple_key = tuple((k[0], k[1], v) for k, v in relation.items())
    return tuple_key


class ReaperQState:
    """
    represents the states based on which the reaper can decide what to
    do next, or to evaluate if the currently selected goal is still valid
    (or achievable)

    TODO: incorporate water gain into this class
    """

    def __init__(
        self,
        water_reaper_relation: dict[tuple[str, str], int],
        water_other_relation: dict[tuple[str, str], int],
        tanker_enemy_relation: dict[tuple[str, str], int],
        player_reaper_relation: dict[tuple[str, str], int],
        player_other_relation: dict[tuple[str, str], int],
        super_power_available: bool,
    ):
        self.water_reaper_relation = water_reaper_relation
        self.water_other_relation = water_other_relation
        self.tanker_enemy_relation = tanker_enemy_relation
        self.player_reaper_relation = player_reaper_relation
        self.player_other_relation = player_other_relation
        self.super_power_available = super_power_available

    def get_state_tuple_key(self):
        """
        TODO: user numbered categories (or enums) in the dict keys instead of strings
        """
        composite_tuple_key = (
            convert_relation_to_tuple_key(self.water_reaper_relation),
            convert_relation_to_tuple_key(self.water_other_relation),
            convert_relation_to_tuple_key(self.tanker_enemy_relation),
            convert_relation_to_tuple_key(self.player_reaper_relation),
            convert_relation_to_tuple_key(self.player_other_relation),
            int(self.super_power_available),
        )
        return composite_tuple_key


class ReaperActionsQWeights:

    def __init__(
        self,
        inner_weigths_dict: dict[str, float],
    ):
        self.inner_weigths_dict = inner_weigths_dict

    def get_sorted_weights(self):
        """
        TODO: This is freakin' inefficient
        """
        sorted_weights = sorted(self.inner_weigths_dict.items(), key=lambda x: x[1], reverse=True)
        return sorted_weights


def get_default_reaper_actions_q_weights():
    reaper_actions_q_weights = {
        'harvest_safe': 0.0,
        'harvest_risky': 0.0,
        'harvest_dangerous': 0.0,
        'ram_reaper_close': 0.0,
        'ram_reaper_mid': 0.0,
        'ram_reaper_far': 0.0,
        'ram_other_close': 0.0,
        'ram_other_mid': 0.0,
        'ram_other_far': 0.0,
        'use_super_power': 0.0,
        'wait': 0.0,
    }
    return reaper_actions_q_weights
