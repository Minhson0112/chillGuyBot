import discord
from discord import app_commands
from discord.ext import commands

from bot.config.channel import TICKET_CHANNEL_ID
from bot.config.decoration import TICKET_DECORATION_IMG_URL
from bot.config.emoji import LOGO, SATURN, TYM_ARROW
from bot.validation.guildValidation import chillStationOnly
from bot.validation.isOwnerValidation import isOwner
from bot.views.ticketCloseButtonView import TicketCloseButtonView
from bot.views.ticketCreateButtonView import TicketCreateButtonView


class CreateTicketCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="createticket", description="Tạo tin nhắn mở ticket")
    @app_commands.default_permissions(administrator=True)
    @chillStationOnly()
    @isOwner()
    async def createTicket(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        ticketChannel = self.bot.get_channel(TICKET_CHANNEL_ID)

        if ticketChannel is None:
            try:
                ticketChannel = await self.bot.fetch_channel(TICKET_CHANNEL_ID)
            except discord.NotFound:
                await interaction.followup.send(
                    f"{LOGO} Không tìm thấy kênh ticket.",
                    ephemeral=True,
                )
                return
            except discord.Forbidden:
                await interaction.followup.send(
                    f"{LOGO} Bot không có quyền xem kênh ticket.",
                    ephemeral=True,
                )
                return
            except discord.HTTPException:
                await interaction.followup.send(
                    f"{LOGO} Không thể lấy thông tin kênh ticket.",
                    ephemeral=True,
                )
                return

        if not isinstance(ticketChannel, discord.TextChannel):
            await interaction.followup.send(
                f"{LOGO} TICKET_CHANNEL_ID không phải là text channel.",
                ephemeral=True,
            )
            return

        await ticketChannel.send(
            embed=self.buildTicketEmbed(interaction.guild),
            view=TicketCreateButtonView(),
            allowed_mentions=discord.AllowedMentions.none(),
        )

        await interaction.followup.send(
            f"{LOGO} Đã tạo tin nhắn ticket tại {ticketChannel.mention}.",
            ephemeral=True,
        )

    def buildTicketEmbed(self, guild: discord.Guild):
        embed = discord.Embed(
            title=f"Chill Station - Ticket",
            description=(
                f"# {LOGO}\n\n"
                f"{TYM_ARROW} Hãy ấn mở ticket khi cần hỗ trợ, chúng tớ sẽ hỗ trợ hết mình trong khả năng \n\n"
                f"{SATURN} Có thể sẽ mất một khoảng thời gian cho đến khi ai đó trả lời, đợi xíu nhé."
            ),
            color=discord.Color.blue(),
        )

        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)

        embed.set_image(url=TICKET_DECORATION_IMG_URL)
        embed.set_footer(text="Chill Station - Ticket")

        return embed


async def setup(bot):
    bot.add_view(TicketCloseButtonView())
    bot.add_view(TicketCreateButtonView())
    await bot.add_cog(CreateTicketCommand(bot))
