import asyncio
import random

import discord
from discord.ext import commands

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.numberFormatHelper import formatNumber
from bot.repository.memberRepository import MemberRepository


class Bingo(commands.Cog):
    MAX_BET = 500
    CARD_SIZE = 5
    BALL_POOL = list(range(1, 11))

    NUMBER_EMOJIS = {
        1: "1️⃣",
        2: "2️⃣",
        3: "3️⃣",
        4: "4️⃣",
        5: "5️⃣",
        6: "6️⃣",
        7: "7️⃣",
        8: "8️⃣",
        9: "9️⃣",
        10: "🔟",
    }

    def __init__(self, bot):
        self.bot = bot
        self.activeUserIds = set()

    @commands.command(name="bingo")
    async def bingo(self, ctx, bet: int = None):
        if bet is None:
            await ctx.reply("Cách dùng: `cg bingo <số chill coin cược>`")
            return

        if ctx.author.id in self.activeUserIds:
            await ctx.reply("Bạn đang có một lượt bingo chưa kết thúc.")
            return

        validateResult = self.validateBet(
            userId=ctx.author.id,
            bet=bet,
        )

        if not validateResult["success"]:
            await ctx.reply(validateResult["message"])
            return

        self.activeUserIds.add(ctx.author.id)

        try:
            await self.playBingo(ctx, bet)
        except Exception as e:
            print(f"Bingo error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi chơi bingo.")
        finally:
            self.activeUserIds.discard(ctx.author.id)

    async def playBingo(
        self,
        ctx,
        bet: int,
    ):
        playerCard = sorted(random.sample(self.BALL_POOL, self.CARD_SIZE))
        drawNumbers = random.sample(self.BALL_POOL, self.CARD_SIZE)

        message = await ctx.reply(
            embed=self.buildIntroEmbed(
                ctx=ctx,
                playerCard=playerCard,
                bet=bet,
            )
        )

        revealedNumbers = []

        for number in drawNumbers:
            await asyncio.sleep(0.55)
            revealedNumbers.append(number)
            await message.edit(
                embed=self.buildDrawingEmbed(
                    ctx=ctx,
                    playerCard=playerCard,
                    revealedNumbers=revealedNumbers,
                    bet=bet,
                )
            )

        await asyncio.sleep(0.8)

        matchCount = self.countMatches(playerCard, drawNumbers)
        coinDelta = self.calculateCoinDelta(matchCount, bet)
        applyResult = self.applyBingoResult(
            userId=ctx.author.id,
            bet=bet,
            coinDelta=coinDelta,
        )

        if not applyResult["success"]:
            await message.edit(
                embed=discord.Embed(
                    title="Bingo",
                    description=applyResult["message"],
                    color=discord.Color.red(),
                )
            )
            return

        await message.edit(
            embed=self.buildFinalEmbed(
                ctx=ctx,
                playerCard=playerCard,
                drawNumbers=drawNumbers,
                matchCount=matchCount,
                payoutText=self.getPayoutText(matchCount),
                bet=bet,
                coinDelta=applyResult["coinDelta"],
                newBalance=applyResult["newBalance"],
            )
        )

    def validateBet(
        self,
        userId: int,
        bet: int,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        if bet <= 0:
            return {
                "success": False,
                "message": "Số chill coin cược phải lớn hơn 0.",
            }

        if bet > self.MAX_BET:
            return {
                "success": False,
                "message": (
                    f"Mỗi lượt bingo chỉ được cược tối đa "
                    f"**{formatNumber(self.MAX_BET)}** {chillCoinEmoji}."
                ),
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            member = memberRepository.findByUserId(userId)

            if member is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của bạn.",
                }

            if member.chill_coin < bet:
                return {
                    "success": False,
                    "message": (
                        f"Bạn cần **{formatNumber(bet)}** {chillCoinEmoji} để chơi, "
                        f"hiện có **{formatNumber(member.chill_coin)}** {chillCoinEmoji}."
                    ),
                }

        return {
            "success": True,
        }

    def applyBingoResult(
        self,
        userId: int,
        bet: int,
        coinDelta: int,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            member = memberRepository.findByUserId(userId)

            if member is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của bạn.",
                }

            if member.chill_coin < bet:
                return {
                    "success": False,
                    "message": (
                        f"Số dư của bạn không đủ để hoàn tất lượt bingo. "
                        f"Cần **{formatNumber(bet)}** {chillCoinEmoji}, "
                        f"hiện có **{formatNumber(member.chill_coin)}** {chillCoinEmoji}."
                    ),
                }

            member.chill_coin += coinDelta
            newBalance = member.chill_coin

            session.commit()

            return {
                "success": True,
                "coinDelta": coinDelta,
                "newBalance": newBalance,
            }

    def calculateCoinDelta(self, matchCount: int, bet: int):
        if matchCount == 5:
            return bet * 9

        if matchCount == 4:
            return bet * 2

        if matchCount == 3:
            return bet // 2

        return -bet

    def getPayoutText(self, matchCount: int):
        if matchCount == 5:
            return "x10"

        if matchCount == 4:
            return "x3"

        if matchCount == 3:
            return "+50%"

        return "x0"

    def countMatches(self, playerCard, drawNumbers):
        return len(set(playerCard).intersection(drawNumbers))

    def buildIntroEmbed(
        self,
        ctx,
        playerCard,
        bet: int,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        embed = discord.Embed(
            title="Bingo Royale",
            description=(
                f"```txt\n{self.formatCard(playerCard)}\n```\n"
                f"Đang chuẩn bị lồng quay...\n"
                f"Tiền cược: **{formatNumber(bet)}** {chillCoinEmoji}"
            ),
            color=discord.Color.blurple(),
        )

        embed.set_author(
            name=f"Vé bingo của {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        embed.add_field(
            name="Bảng thưởng",
            value="3 số: +50%\n4 số: x3\n5 số: x10",
            inline=True,
        )

        embed.add_field(
            name="Trạng thái",
            value="Sắp rút bóng",
            inline=True,
        )

        return embed

    def buildDrawingEmbed(
        self,
        ctx,
        playerCard,
        revealedNumbers,
        bet: int,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
        matchCount = self.countMatches(playerCard, revealedNumbers)

        embed = discord.Embed(
            title="Bingo Royale",
            description=(
                f"```txt\n{self.formatCard(playerCard)}\n```\n"
                f"Bi rút ra: {self.formatNumbers(revealedNumbers)}\n"
                f"Đã khớp: **{matchCount}/{self.CARD_SIZE}** số\n"
                f"Tiền cược: **{formatNumber(bet)}** {chillCoinEmoji}"
            ),
            color=discord.Color.blurple(),
        )

        embed.set_author(
            name=f"Vé bingo của {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        return embed

    def buildFinalEmbed(
        self,
        ctx,
        playerCard,
        drawNumbers,
        matchCount: int,
        payoutText: str,
        bet: int,
        coinDelta: int,
        newBalance: int,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        if coinDelta >= 0:
            resultText = (
                f"Bingo **{matchCount}/{self.CARD_SIZE}** số. Mức thưởng {payoutText}.\n"
                f"Lãi: **{formatNumber(coinDelta)}** {chillCoinEmoji}"
            )
            color = discord.Color.green()
        else:
            resultText = (
                f"Chỉ khớp **{matchCount}/{self.CARD_SIZE}** số. Chưa đủ để trúng thưởng.\n"
                f"Mất: **{formatNumber(abs(coinDelta))}** {chillCoinEmoji}"
            )
            color = discord.Color.red()

        embed = discord.Embed(
            title="Kết quả Bingo Royale",
            description=(
                f"Vé của bạn\n"
                f"```txt\n{self.formatCard(playerCard)}\n```\n"
                f"Bi đã rút: {self.formatNumbers(drawNumbers)}\n\n"
                f"{resultText}\n\n"
                f"Số dư hiện tại: **{formatNumber(newBalance)}** {chillCoinEmoji}"
            ),
            color=color,
        )

        embed.set_author(
            name=f"Lượt bingo của {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        embed.add_field(
            name="Tiền cược",
            value=f"**{formatNumber(bet)}** {chillCoinEmoji}",
            inline=True,
        )

        embed.add_field(
            name="Hệ số",
            value=payoutText,
            inline=True,
        )

        return embed

    def formatCard(self, numbers):
        return " ".join(self.NUMBER_EMOJIS[number] for number in numbers)

    def formatNumbers(self, numbers):
        if not numbers:
            return "-"

        return " ".join(self.NUMBER_EMOJIS[number] for number in numbers)


async def setup(bot):
    await bot.add_cog(Bingo(bot))
