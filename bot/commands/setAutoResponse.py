import discord
from discord import app_commands
from discord.ext import commands

from bot.config.userId import CAN_CREATE_AUTO_RESPONSE_USER_ID
from bot.services.autoResponder.setAutoResponseService import SetAutoResponseService
from bot.validation.guildValidation import chillStationOnly


class SetAutoResponse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.setAutoResponseService = SetAutoResponseService()

    @app_commands.command(name="setautoresponse", description="Tạo auto response từ key và link template")
    @app_commands.describe(
        msg_key="Key để kích hoạt auto response",
        is_global="Cho phép mọi người dùng key này hay không",
        is_exact_match="True: phải giống hệt key, False: chỉ cần key xuất hiện trong tin nhắn",
        msg_link="Link tin nhắn template",
    )
    @chillStationOnly()
    async def setAutoResponse(
        self,
        interaction: discord.Interaction,
        msg_key: str,
        is_global: bool,
        is_exact_match: bool,
        msg_link: str,
    ):
        if interaction.user.id not in CAN_CREATE_AUTO_RESPONSE_USER_ID:
            await interaction.response.send_message("Bạn không có quyền dùng lệnh này.")
            return

        msgKey = msg_key.strip().lower()

        if not msgKey:
            await interaction.response.send_message("msg_key không được để trống.")
            return

        if len(msgKey) > 100:
            await interaction.response.send_message("msg_key không được vượt quá 100 ký tự.")
            return

        if not self.isValidDiscordMessageLink(msg_link):
            await interaction.response.send_message("msg_link không phải link tin nhắn Discord hợp lệ.")
            return

        await interaction.response.defer()

        autoResponder = self.setAutoResponseService.createAutoResponder(
            userId=interaction.user.id,
            msgKey=msgKey,
            isGlobal=is_global,
            isExactMatch=is_exact_match,
            msgLink=msg_link,
        )

        if autoResponder is None:
            await interaction.followup.send(
                "msg_key này đã tồn tại, hãy chọn key khác.",
            )
            return

        embed = discord.Embed(
            title="Tạo auto response thành công",
            description="Đã lưu rule auto response mới.",
        )
        embed.add_field(
            name="Người tạo",
            value=f"{interaction.user.mention}",
            inline=False,
        )
        embed.add_field(
            name="Key",
            value=msgKey,
            inline=False,
        )
        embed.add_field(
            name="Global",
            value="Có" if is_global else "Không",
            inline=False,
        )
        embed.add_field(
            name="Match type",
            value="Exact match" if is_exact_match else "Contains match",
            inline=False,
        )
        embed.add_field(
            name="Template link",
            value=msg_link,
            inline=False,
        )

        await interaction.followup.send(
            embed=embed,
        )

    def isValidDiscordMessageLink(self, msgLink):
        parts = msgLink.strip().split("/")

        if len(parts) < 3:
            return False

        if not msgLink.startswith("https://discord.com/channels/"):
            return False

        try:
            int(parts[-3])
            int(parts[-2])
            int(parts[-1])
            return True
        except ValueError:
            return False


async def setup(bot):
    await bot.add_cog(SetAutoResponse(bot))