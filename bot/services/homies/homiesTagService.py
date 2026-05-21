import discord

class HomiesTagService:
    CHILL_STATION_GUILD_ID = 1356994231918530690

    def __init__(self, bot):
        self.bot = bot

    async def hasChillStationTagByUserId(self, userId: int):
        primaryGuild = await self.resolvePrimaryGuild(userId)

        if primaryGuild is None:
            return False

        identityGuildId = self.getPrimaryGuildId(primaryGuild)

        if identityGuildId is None:
            return False

        return identityGuildId == self.CHILL_STATION_GUILD_ID

    async def resolvePrimaryGuild(self, userId: int):
        try:
            user = await self.bot.fetch_user(userId)
            primaryGuild = getattr(user, "primary_guild", None)

            if primaryGuild is not None:
                return primaryGuild
        except discord.HTTPException:
            return None

        return None

    def getPrimaryGuildId(self, primaryGuild):
        identityGuildId = self.getPrimaryGuildValue(
            primaryGuild=primaryGuild,
            keyList=[
                "identity_guild_id",
                "guild_id",
                "id",
            ],
        )

        if identityGuildId is None:
            return None

        try:
            return int(identityGuildId)
        except (TypeError, ValueError):
            return None

    def getPrimaryGuildValue(
        self,
        primaryGuild,
        keyList: list[str],
    ):
        if isinstance(primaryGuild, dict):
            for key in keyList:
                value = primaryGuild.get(key)

                if value is not None:
                    return value

            return None

        for key in keyList:
            value = getattr(primaryGuild, key, None)

            if value is not None:
                return value

        return None