from enum import Enum

from bot.config.emoji import (
    CHILL_COIN,
    CONGRATULATIONS,
    FLOWER,
    GIFT,
    HELLO,
    REPORT,
    SUN,
)


class TicketType(str, Enum):
    REPORT = "report"
    GIVEAWAY_REWARD = "giveaway_reward"
    PARTNER = "partner"
    CREATE_GIVEAWAY = "create_giveaway"
    FARM_GAME_CHILL_COIN = "farm_game_chill_coin"
    STAFF_APPLICATION = "staff_application"
    OTHER = "other"

    @property
    def label(self):
        labels = {
            TicketType.REPORT: "Report",
            TicketType.GIVEAWAY_REWARD: "Nhận Thưởng GA",
            TicketType.PARTNER: "Partner",
            TicketType.CREATE_GIVEAWAY: "Tạo Giveaway",
            TicketType.FARM_GAME_CHILL_COIN: "Vấn đề Farm game và chill coin",
            TicketType.STAFF_APPLICATION: "Ứng tuyển chức vụ",
            TicketType.OTHER: "Các vấn đề khác",
        }

        return labels[self]

    @property
    def emoji(self):
        emojis = {
            TicketType.REPORT: REPORT,
            TicketType.GIVEAWAY_REWARD: GIFT,
            TicketType.PARTNER: HELLO,
            TicketType.CREATE_GIVEAWAY: CONGRATULATIONS,
            TicketType.FARM_GAME_CHILL_COIN: CHILL_COIN,
            TicketType.STAFF_APPLICATION: SUN,
            TicketType.OTHER: FLOWER,
        }

        return emojis[self]

    @property
    def description(self):
        descriptions = {
            TicketType.REPORT: "report các hành vi vi phạm nội quy server",
            TicketType.GIVEAWAY_REWARD: "Nhận thưởng nếu bạn trúng GA",
            TicketType.PARTNER: "Các vấn đề liên quan đến tạo pn hay cập nhật link PN",
            TicketType.CREATE_GIVEAWAY: "Tạo giveaway trong chill station",
            TicketType.FARM_GAME_CHILL_COIN: "trao đổi về farm game hoặc đổi tiền chill coin",
            TicketType.STAFF_APPLICATION: "ứng tuyển staff, mod, admin hay owner tại đây",
            TicketType.OTHER: "muốn trao đổi về các vấn đề cá nhân khác tại đây.",
        }

        return descriptions[self]
