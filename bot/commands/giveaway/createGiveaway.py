import discord
from discord import app_commands
from discord.ext import commands

from bot.enums.giveawayType import GiveawayType
from bot.services.giveaway.createGiveawayService import CreateGiveawayService
from bot.services.giveaway.giveawayMessageService import GiveawayMessageService
from bot.services.giveaway.giveawaySchedulerService import giveawaySchedulerService
from bot.validation.guildValidation import guildOnly
from bot.views.giveawayJoinButtonView import GiveawayJoinButtonView
from bot.enums.moderationActionType import ModerationActionType
from bot.validation.modPermissionValidation import hasModerationPermission


class CreateGiveawayCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.createGiveawayService = CreateGiveawayService()
        self.giveawayMessageService = GiveawayMessageService()

    @app_commands.command(
        name="creategiveaway",
        description="Tạo giveaway trong kênh hiện tại",
    )
    @app_commands.describe(
        title="Tiêu đề giveaway",
        giveaway_type="Loại phần thưởng giveaway",
        reward="Giá trị phần thưởng",
        winners="Số người thắng",
        duration="Thời gian tới lúc quay thưởng, tính bằng giây",
        limit_role="Role bắt buộc để được tham gia giveaway",
    )
    @app_commands.rename(giveaway_type="type")
    @app_commands.choices(
        giveaway_type=[
            app_commands.Choice(name=GiveawayType.COWONCY.value, value=GiveawayType.COWONCY.value),
            app_commands.Choice(name=GiveawayType.VND.value, value=GiveawayType.VND.value),
            app_commands.Choice(name=GiveawayType.CHILL_COIN.value, value=GiveawayType.CHILL_COIN.value),
        ],
    )
    @guildOnly()
    @hasModerationPermission(ModerationActionType.GIVEAWAY)
    async def createGiveaway(
        self,
        interaction: discord.Interaction,
        title: str,
        giveaway_type: app_commands.Choice[str],
        reward: int,
        winners: int,
        duration: int,
        limit_role: discord.Role | None = None,
    ):
        await interaction.response.defer(ephemeral=True)

        result = self.createGiveawayService.createGiveaway(
            title=title,
            giveawayType=giveaway_type.value,
            reward=reward,
            winnerCount=winners,
            durationSeconds=duration,
            channelId=interaction.channel_id,
            createdByUserId=interaction.user.id,
            limitRoleId=limit_role.id if limit_role is not None else None,
        )

        if not result["success"]:
            await interaction.followup.send(
                result["message"],
                ephemeral=True,
            )
            return

        giveawayId = result["giveawayId"]
        embed = self.giveawayMessageService.buildGiveawayEmbedById(
            giveawayId=giveawayId,
            guild=interaction.guild,
        )

        if embed is None:
            await interaction.followup.send(
                "Không thể tạo embed giveaway.",
                ephemeral=True,
            )
            return

        if interaction.channel is None:
            await interaction.followup.send(
                "Không thể xác định kênh tạo giveaway.",
                ephemeral=True,
            )
            return

        giveawayMessage = await interaction.channel.send(
            embed=embed,
            view=GiveawayJoinButtonView(giveawayId),
        )

        self.createGiveawayService.updateGiveawayMessageId(
            giveawayId=giveawayId,
            messageId=giveawayMessage.id,
        )
        giveawaySchedulerService.reloadSchedule()

        await interaction.followup.send(
            result["message"],
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(CreateGiveawayCommand(bot))
