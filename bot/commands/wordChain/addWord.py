import discord
from discord import app_commands
from discord.ext import commands

from bot.services.wordChain.wordChainPhraseAdminService import WordChainPhraseAdminService
from bot.validation.isOwnerValidation import isOwner


class AddWord(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wordChainPhraseAdminService = WordChainPhraseAdminService()

    @app_commands.command(
        name="addword",
        description="Thêm cụm từ nối chữ vào database",
    )
    @app_commands.describe(
        phrases="Mỗi dòng là một cụm 2 từ cần thêm",
    )
    @isOwner()
    async def addWord(
        self,
        interaction: discord.Interaction,
        phrases: str,
    ):
        await interaction.response.defer(ephemeral=True, thinking=True)

        result = self.wordChainPhraseAdminService.addPhrases(phrases)
        message = self.buildResultMessage(result)

        await interaction.followup.send(
            message,
            ephemeral=True,
        )

    def buildResultMessage(self, result):
        messageLines = [
            "Đã xử lý dữ liệu nối chữ.",
            f"Thêm mới: **{result['createdCount']}**",
            f"Cập nhật lại: **{result['updatedCount']}**",
            f"Bỏ qua: **{result['skippedCount']}**",
            f"Cache hiện tại: **{result['cacheCount']}** cụm",
        ]

        skippedPhrases = result["skippedPhrases"][:10]

        if skippedPhrases:
            messageLines.append("")
            messageLines.append("Các dòng bị bỏ qua:")

            for skippedPhrase in skippedPhrases:
                messageLines.append(
                    f"- `{skippedPhrase['phrase']}`: {skippedPhrase['reason']}"
                )

        if result["skippedCount"] > len(skippedPhrases):
            remainingCount = result["skippedCount"] - len(skippedPhrases)
            messageLines.append(f"... và {remainingCount} dòng khác.")

        return "\n".join(messageLines)


async def setup(bot):
    await bot.add_cog(AddWord(bot))
