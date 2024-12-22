"""
Categorization for distance and risk categories
Can grow into a package in the future
"""


from enum import Enum

from python_prototypes.field_tools import SQUARE_COUNT


class DistanceCategories(Enum):
    close = 1
    medium = 2
    far = 3

class DistanceCategoriesRetriever:

    def __init__(self, square_count):
        grid_squares = square_count**2
        self.close_limit = grid_squares // 20
        self.medium_limit = grid_squares // 15
        self.far = grid_squares

    def get_category(self, manhattan_distance: int) -> DistanceCategories:
        if manhattan_distance <= self.close_limit:
            return DistanceCategories.close
        if manhattan_distance <= self.medium_limit:
            return DistanceCategories.medium

        return DistanceCategories.far


class WaterRiskCategories(Enum):
    dangerous = 1
    risky = 2
    safe = 3

class WaterRiskCategoriesRetriever:

    def __init__(self, square_count: int):
        grid_squares = square_count**2
        self.dangerous_limit = grid_squares // 90
        self.risk_limit = grid_squares // 25
        self.safe_limit = grid_squares

    def get_category(self, enemy_manhattan_distance: int) -> WaterRiskCategories:
        if enemy_manhattan_distance <= self.dangerous_limit:
            return WaterRiskCategories.dangerous
        if enemy_manhattan_distance <= self.risk_limit:
            return WaterRiskCategories.risky

        return WaterRiskCategories.safe


DISTANCE_CATEGORY_RETRIEVER = DistanceCategoriesRetriever(SQUARE_COUNT)
WATER_RISK_CATEGORY_RETRIEVER = WaterRiskCategoriesRetriever(SQUARE_COUNT)

