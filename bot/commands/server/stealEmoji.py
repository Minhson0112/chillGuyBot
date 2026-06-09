import discord
from discord import app_commands
from discord.ext import commands

from bot.services.server.emojiStealService import EmojiStealService
from bot.validation.guildValidation import chillStationOnly


class StealEmojiCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojiStealService = EmojiStealService()

    @app_commands.command(
        name="stealemoji",
        description="Thêm custom emoji vào server với tên chỉ định",
    )
    @app_commands.describe(
        emoji="Custom emoji cần thêm vào server",
        emoji_name="Tên emoji mới trong server",
    )
    @app_commands.rename(emoji_name="ten_emoji")
    @app_commands.default_permissions(manage_emojis_and_stickers=True)
    @chillStationOnly()
    async def stealEmoji(
        self,
        interaction: discord.Interaction,
        emoji: str,
        emoji_name: str,
    ):
        if interaction.guild is None:
            await interaction.response.send_message("Lệnh này chỉ dùng được trong server.", ephemeral=True)
            return

        member = interaction.user

        if not isinstance(member, discord.Member):
            raise app_commands.CheckFailure("Không xác định được member trong server.")

        if not member.guild_permissions.manage_emojis_and_stickers:
            raise app_commands.CheckFailure("Bạn cần quyền quản lý emoji để sử dụng lệnh này.")

        botMember = interaction.guild.get_member(self.bot.user.id)

        if botMember is None or not botMember.guild_permissions.manage_emojis_and_stickers:
            await interaction.response.send_message("Bot cần quyền quản lý emoji để thêm emoji mới.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            createdEmoji = await self.emojiStealService.stealEmoji(
                guild=interaction.guild,
                emoji=emoji,
                emojiName=emoji_name,
                reason=f"Steal emoji command by {interaction.user} ({interaction.user.id})",
            )
        except ValueError as e:
            await interaction.followup.send(str(e), ephemeral=True)
            return
        except discord.Forbidden:
            await interaction.followup.send("Bot không có quyền thêm emoji vào server.", ephemeral=True)
            return
        except discord.HTTPException as e:
            await interaction.followup.send(f"Thêm emoji thất bại do lỗi Discord: {e}", ephemeral=True)
            return

        await interaction.followup.send(
            f"Đã thêm emoji {createdEmoji} với tên `{createdEmoji.name}`.",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(StealEmojiCommand(bot))
