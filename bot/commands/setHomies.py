import discord
from discord import app_commands
from discord.ext import commands

from bot.config.channel import HOMIES_ROLE_CHANNEL_ID
from bot.config.roles import HOMIES_ROLE_ID
from bot.config.emoji import LOGO
from bot.validation.guildValidation import guildOnly
from bot.validation.isOwnerValidation import isOwner
from bot.views.homiesRoleButtonView import HomiesRoleButtonView


class SetHomiesCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sethomies", description="Tạo tin nhắn nhận role Homies")
    @app_commands.default_permissions(administrator=True)
    @guildOnly()
    @isOwner()
    async def setHomies(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        homiesRoleChannel = self.bot.get_channel(HOMIES_ROLE_CHANNEL_ID)
        role = interaction.guild.get_role(HOMIES_ROLE_ID)

        if homiesRoleChannel is None:
            try:
                homiesRoleChannel = await self.bot.fetch_channel(HOMIES_ROLE_CHANNEL_ID)
            except discord.NotFound:
                await interaction.followup.send(
                    f"{LOGO} Không tìm thấy kênh nhận role Homies.",
                    ephemeral=True,
                )
                return
            except discord.Forbidden:
                await interaction.followup.send(
                    f"{LOGO} Bot không có quyền xem kênh nhận role Homies.",
                    ephemeral=True,
                )
                return
            except discord.HTTPException:
                await interaction.followup.send(
                    f"{LOGO} Không thể lấy thông tin kênh nhận role Homies.",
                    ephemeral=True,
                )
                return

        if not isinstance(homiesRoleChannel, discord.TextChannel):
            await interaction.followup.send(
                f"{LOGO} HOMIES_ROLE_CHANNEL_ID không phải là text channel.",
                ephemeral=True,
            )
            return

        await homiesRoleChannel.send(
            embed=self.buildHomiesRoleMessageEmbed(),
            view=HomiesRoleButtonView(),
            allowed_mentions=discord.AllowedMentions.none(),
        )

        await interaction.followup.send(
            f"{LOGO} Đã tạo tin nhắn nhận role Homies tại {homiesRoleChannel.mention}.",
            ephemeral=True,
        )

    def buildHomiesRoleMessageEmbed(self):
        embed = discord.Embed(
            title="<a:CS_blueblink:1507030291640881203> Nhận role ⋆｡‧˚ʚ 𝐡𝐨𝐦𝐢𝐞𝐬 ɞ˚‧｡⋆ <a:CS_pink6:1507030280932687966>",
            description=(
                "Bấm nút bên dưới để nhận role <@&1506931736058134538>."
            ),
            color=discord.Color.blue(),
        )

        return embed


async def setup(bot):
    bot.add_view(HomiesRoleButtonView())
    await bot.add_cog(SetHomiesCommand(bot))