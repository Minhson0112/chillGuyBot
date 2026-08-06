import discord
from discord import app_commands
from discord.ext import commands

from bot.services.member.memberSyncService import MemberSyncService
from bot.validation.guildValidation import chillStationOnly


class LoadMember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberSyncService = MemberSyncService()

    @app_commands.command(name="loadmember", description="Load all current guild members into database")
    @chillStationOnly()
    async def loadMember(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        syncedCount = await self.memberSyncService.syncGuildMembers(interaction.guild)

        await interaction.followup.send(
            f"Đã lưu hoặc cập nhật {syncedCount} member vào database.",
            ephemeral=True
        )

    @commands.command(name="loadmember")
    @commands.has_permissions(administrator=True)
    async def loadMemberText(self, ctx):
        msg = await ctx.send("Đang đồng bộ danh sách thành viên...")
        syncedCount = await self.memberSyncService.syncGuildMembers(ctx.guild)
        await msg.edit(content=f"Đã lưu hoặc cập nhật {syncedCount} member vào database.")

    @loadMemberText.error
    async def loadMemberTextError(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("Bạn không có quyền sử dụng lệnh này. Chỉ admin mới được dùng.")


async def setup(bot):
    await bot.add_cog(LoadMember(bot))
