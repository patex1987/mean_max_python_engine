"""
this module contains classes and functions related to represent and
initialize the q state of the game decision learning
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ReaperQState:
    """
    represents the states based on which the reaper can decide what to
    do next, or to evaluate if the currently selected goal is still valid
    (or achievable)

    TODO: incorporate water gain into this class
    """

    def __init__(
        self,
        # TODO: the Any is actually an integer and it is the id of the object
        water_reaper_relation: dict[tuple[str, str], list[int]],
        water_other_relation: dict[tuple[str, str], list[int]],
        tanker_enemy_relation: dict[tuple[str, str], list[int]],
        player_reaper_relation: dict[tuple[str, str], list[int]],
        player_other_relation: dict[tuple[str, str], list[int]],
        super_power_available: bool,
        reaper_water_relation: dict[int, tuple[str, str]],
        other_water_relation: dict[int, tuple[str, str]],
        tanker_id_enemy_category_relation: dict[int, tuple[str, str]],
        reaper_id_category_relation: dict[int, tuple[str, str]],
        other_id_category_mapping: dict[int, tuple[str, str]],
    ):
        self.water_reaper_relation = water_reaper_relation
        self.water_other_relation = water_other_relation
        self.tanker_enemy_relation = tanker_enemy_relation
        self.player_reaper_relation = player_reaper_relation
        self.player_other_relation = player_other_relation
        self.super_power_available = super_power_available
        self.water_reaper_state = convert_to_state_dict(water_reaper_relation)
        self.water_other_state = convert_to_state_dict(water_other_relation)
        self.tanker_enemy_state = convert_to_state_dict(tanker_enemy_relation)
        self.player_reaper_state = convert_to_state_dict(player_reaper_relation)
        self.player_other_state = convert_to_state_dict(player_other_relation)
        self.reaper_water_relation = reaper_water_relation
        self.other_water_relation = other_water_relation
        self.tanker_id_enemy_category_relation = tanker_id_enemy_category_relation
        self.reaper_id_category_relation = reaper_id_category_relation
        self.other_id_category_mapping = other_id_category_mapping

    def get_state_tuple_key(self) -> tuple[tuple, tuple, tuple, tuple, tuple, int]:
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
        inner_weigths_dict: dict['ReaperActionTypes', float],
    ):
        self.inner_weigths_dict = inner_weigths_dict

    def get_sorted_weights(self):
        """
        TODO: This is freakin' inefficient
        """
        sorted_weights = sorted(self.inner_weigths_dict.items(), key=lambda x: x[1], reverse=True)
        return sorted_weights

    def __repr__(self):
        return 'ReaperActionsQWeights({0})'.format(self.inner_weigths_dict)


def get_default_water_relations() -> dict[tuple[str, str], list[Any]]:
    water_reaper_relation = {
        ('close', 'safe'): [],
        ('close', 'risky'): [],
        ('close', 'dangerous'): [],
        ('medium', 'safe'): [],
        ('medium', 'risky'): [],
        ('medium', 'dangerous'): [],
        ('far', 'safe'): [],
        ('far', 'risky'): [],
        ('far', 'dangerous'): [],
    }
    return water_reaper_relation


def get_default_tanker_enemies_relation() -> dict[tuple[str, str], list[Any]]:
    """
    keyed by the tanker distance category, and that tanker's distance category
    to the enemies

    :return:
    """
    tanker_enemies_relation = {
        ('close', 'safe'): [],
        ('close', 'risky'): [],
        ('close', 'dangerous'): [],
        ('medium', 'safe'): [],
        ('medium', 'risky'): [],
        ('medium', 'dangerous'): [],
        ('far', 'safe'): [],
        ('far', 'risky'): [],
        ('far', 'dangerous'): [],
    }
    return tanker_enemies_relation


def get_default_enemies_relation() -> dict[tuple[str, str], list[Any]]:
    """
    keyed by enemy distance category, and that enemy's distance category
    to wreck or a tanker

    :return:
    """
    enemies_relation = {
        ('close', 'close'): [],
        ('close', 'medium'): [],
        ('medium', 'close'): [],
        ('medium', 'medium'): [],
        ('far', 'close'): [],
        ('far', 'medium'): [],
    }
    return enemies_relation


class ReaperActionTypes(Enum):
    """
    TODO: create multiple use super power categories
    TODO: create a category to move close to tankers (can be useful when no wreck is available)
    """

    harvest_safe = 1
    harvest_risky = 2
    harvest_dangerous = 3
    ram_reaper_close = 4
    ram_reaper_mid = 5
    ram_reaper_far = 6
    ram_other_close = 7
    ram_other_mid = 8
    ram_other_far = 9
    use_super_power = 10
    wait = 11
    move_tanker_safe = 12
    move_tanker_risky = 13
    move_tanker_dangerous = 14


def get_default_reaper_actions_q_weights() -> dict[ReaperActionTypes, float]:
    reaper_actions_q_weights = {
        ReaperActionTypes.harvest_safe: 0.0,
        ReaperActionTypes.harvest_risky: 0.0,
        ReaperActionTypes.harvest_dangerous: 0.0,
        ReaperActionTypes.ram_reaper_close: 0.0,
        ReaperActionTypes.ram_reaper_mid: 0.0,
        ReaperActionTypes.ram_reaper_far: 0.0,
        ReaperActionTypes.ram_other_close: 0.0,
        ReaperActionTypes.ram_other_mid: 0.0,
        ReaperActionTypes.ram_other_far: 0.0,
        ReaperActionTypes.use_super_power: 0.0,
        ReaperActionTypes.wait: 0.0,
        ReaperActionTypes.move_tanker_safe: 0.0,
        ReaperActionTypes.move_tanker_risky: 0.0,
        ReaperActionTypes.move_tanker_dangerous: 0.0,
    }
    return reaper_actions_q_weights


def convert_relation_to_tuple_key(relation: dict[tuple[str, str], list[Any]]) -> tuple:
    tuple_key = tuple((k[0], k[1], 1 if len(v) > 0 else 0) for k, v in relation.items())
    return tuple_key


def convert_to_state_dict(relation: dict[tuple[str, str], list[Any]]) -> dict[tuple[str, str], int]:
    state_dict = {state_key: 1 if len(coordinates) > 0 else 0 for state_key, coordinates in relation.items()}
    return state_dict


@dataclass
class MissionStep:
    q_state_key: tuple
    goal_type: ReaperActionTypes
