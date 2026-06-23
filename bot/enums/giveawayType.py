from enum import Enum

from bot.config.emoji import CHILL_COIN, COWONCCY, NETFLIX, NITRO, SPOTIFY, VND


class GiveawayType(str, Enum):
    CHILL_COIN = "chill_coin"
    COWONCY = "cowoncy"
    VND = "vnd"
    DISCORD_NITRO = "discord_nitro"
    NETFLIX = "netflix"
    SPOTIFY = "spotify"
    CUSTOM = "custom"

    @property
    def emoji(self):
        return {
            GiveawayType.CHILL_COIN: CHILL_COIN,
            GiveawayType.COWONCY: COWONCCY,
            GiveawayType.VND: VND,
            GiveawayType.DISCORD_NITRO: NITRO,
            GiveawayType.NETFLIX: NETFLIX,
            GiveawayType.SPOTIFY: SPOTIFY,
        }.get(self, "")

    @property
    def unit(self):
        return {
            GiveawayType.CHILL_COIN: "chill coin",
            GiveawayType.COWONCY: "cowoncy",
            GiveawayType.VND: "VND",
            GiveawayType.DISCORD_NITRO: "Discord Nitro",
            GiveawayType.NETFLIX: "Netflix",
            GiveawayType.SPOTIFY: "Spotify",
        }.get(self, "")

    @property
    def isMonetary(self):
        return self in {
            GiveawayType.CHILL_COIN,
            GiveawayType.COWONCY,
            GiveawayType.VND,
        }

    @property
    def isSubscription(self):
        return self in {
            GiveawayType.DISCORD_NITRO,
            GiveawayType.NETFLIX,
            GiveawayType.SPOTIFY,
        }
