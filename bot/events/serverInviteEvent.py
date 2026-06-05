import discord
from discord.ext import commands

from bot.config.config import CHILL_STATION_GUILD_ID
from bot.services.server.serverInviteSyncService import ServerInviteSyncService


class ServerInviteEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serverInviteSyncService = ServerInviteSyncService()

    def isChillStationInvite(self, invite: discord.Invite):
        guild = getattr(invite, "guild", None)

        if guild is None:
            return False

        return guild.id == CHILL_STATION_GUILD_ID

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        if not self.isChillStationInvite(invite):
            return

        try:
            result = self.serverInviteSyncService.syncCreatedInvite(invite)
            print(
                f"Invite create event synced {invite.code}: "
                f"created={result['created']}, updated={result['updated']}"
            )
        except Exception as e:
            print(f"Invite create event error for {invite.code}: {e}")

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        if not self.isChillStationInvite(invite):
            return

        try:
            result = self.serverInviteSyncService.markDeletedInvite(invite)
            print(
                f"Invite delete event synced {invite.code}: "
                f"created={result['created']}, updated={result['updated']}"
            )
        except Exception as e:
            print(f"Invite delete event error for {invite.code}: {e}")


async def setup(bot):
    await bot.add_cog(ServerInviteEvent(bot))
