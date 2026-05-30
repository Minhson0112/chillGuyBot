import traceback

import discord

from bot.services.partner.cancelPartnerService import CancelPartnerService


class PartnerCancelConfirmView(discord.ui.View):
    def __init__(
        self,
        bot,
        partnerId: int,
        requestedByUserId: int,
    ):
        super().__init__(timeout=180)
        self.bot = bot
        self.partnerId = partnerId
        self.requestedByUserId = requestedByUserId
        self.cancelPartnerService = CancelPartnerService()

    @discord.ui.button(
        label="hủy PN",
        style=discord.ButtonStyle.danger,
        emoji="✅",
    )
    async def cancelPartnerButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.requestedByUserId:
            await interaction.response.send_message(
                "Chỉ người dùng lệnh cancelpn mới có thể xác nhận hủy PN.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        result = await self.cancelPartnerService.cancelPartner(
            bot=self.bot,
            guild=interaction.guild,
            partnerId=self.partnerId,
        )

        if result["success"]:
            for item in self.children:
                item.disabled = True

            if interaction.message is not None:
                await interaction.message.edit(view=self)

        await interaction.followup.send(result["message"])

    async def on_error(self, interaction: discord.Interaction, error: Exception, item):
        traceback.print_exception(type(error), error, error.__traceback__)

        if interaction.response.is_done():
            await interaction.followup.send(
                "Đã xảy ra lỗi khi hủy PN.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "Đã xảy ra lỗi khi hủy PN.",
            ephemeral=True,
        )
