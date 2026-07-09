from enum import Enum


class FarmAchievementConditionType(str, Enum):
    COLLECT_ITEM_QUANTITY = "collect_item_quantity"
    CATCH_ALL_ITEM_TYPE = "catch_all_item_type"
    CATCH_ALL_ITEM_TYPE_WITH_MIN_WEIGHT = "catch_all_item_type_with_min_weight"
    HARVEST_ALL_CROPS_BY_LEVEL = "harvest_all_crops_by_level"
    COOK_ALL_RECIPES_BY_LEVEL = "cook_all_recipes_by_level"
    COMPLETE_TRAIN_ORDER_COUNT = "complete_train_order_count"
    EARN_MARKET_CHILL_COIN = "earn_market_chill_coin"
