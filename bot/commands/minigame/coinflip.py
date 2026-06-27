import asyncio
import random

import discord
from discord.ext import commands

from bot.config.database import getDbSession
from bot.config.emoji import (
    CHILL_COIN_HEADS,
    CHILL_COIN_SPINNING,
    CHILL_COIN_TAILS,
    FARM_GAME_EMOJI,
)
from bot.helper.numberFormatHelper import formatNumber
from bot.repository.memberRepository import MemberRepository


class CoinFlip(commands.Cog):
    MAX_BET = 500
    HEADS = "h"
    TAILS = "t"

    def __init__(self, bot):
        self.bot = bot
        self.activeUserIds = set()

    @commands.command(name="cf")
    async def coinFlip(self, ctx, choice: str = None, bet: str = None):
        if choice is None or bet is None:
            await ctx.reply(
                "Cách dùng: `cg cf h <số chill coin cược>` hoặc `cg cf t <số chill coin cược>`"
            )
            return

        choice = choice.lower()

        if choice not in [self.HEADS, self.TAILS]:
            await ctx.reply("Bạn chỉ được chọn `h` cho mặt ngửa hoặc `t` cho mặt xấp.")
            return

        try:
            bet = int(bet)
        except ValueError:
            await ctx.reply("Tiền cược phải là số nguyên.")
            return

        if ctx.author.id in self.activeUserIds:
            await ctx.reply("Bạn đang có một lượt lật đồng xu chưa kết thúc.")
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
            await self.playCoinFlip(ctx, choice, bet)
        except Exception as e:
            print(f"Coin flip error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi lật đồng xu.")
        finally:
            self.activeUserIds.discard(ctx.author.id)

    async def playCoinFlip(
        self,
        ctx,
        choice: str,
        bet: int,
    ):
        result = random.choice([self.HEADS, self.TAILS])
        message = await ctx.reply(
            embed=self.buildFlippingEmbed(
                ctx=ctx,
                choice=choice,
                bet=bet,
            )
        )

        await asyncio.sleep(1)

        applyResult = self.applyCoinFlipResult(
            userId=ctx.author.id,
            bet=bet,
            isWin=choice == result,
        )

        if not applyResult["success"]:
            await message.edit(
                embed=discord.Embed(
                    title="Lật Đồng Xu",
                    description=applyResult["message"],
                    color=discord.Color.red(),
                )
            )
            return

        await message.edit(
            embed=self.buildResultEmbed(
                ctx=ctx,
                choice=choice,
                result=result,
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
                    f"Mỗi lượt lật đồng xu chỉ được cược tối đa "
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

    def applyCoinFlipResult(
        self,
        userId: int,
        bet: int,
        isWin: bool,
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
                        f"Số dư của bạn không đủ để hoàn tất lượt chơi. "
                        f"Cần **{formatNumber(bet)}** {chillCoinEmoji}, "
                        f"hiện có **{formatNumber(member.chill_coin)}** {chillCoinEmoji}."
                    ),
                }

            coinDelta = bet if isWin else -bet
            member.chill_coin += coinDelta
            newBalance = member.chill_coin

            session.commit()

            return {
                "success": True,
                "coinDelta": coinDelta,
                "newBalance": newBalance,
            }

    def buildFlippingEmbed(
        self,
        ctx,
        choice: str,
        bet: int,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        embed = discord.Embed(
            title="Lật Đồng Xu",
            description=(
                f"{CHILL_COIN_SPINNING} Đang lật đồng xu...\n\n"
                f"Bạn chọn: **{self.getSideName(choice)}**\n"
                f"Tiền cược: **{formatNumber(bet)}** {chillCoinEmoji}"
            ),
            color=discord.Color.gold(),
        )

        embed.set_author(
            name=f"Lượt chơi của {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        return embed

    def buildResultEmbed(
        self,
        ctx,
        choice: str,
        result: str,
        bet: int,
        coinDelta: int,
        newBalance: int,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
        resultEmoji = self.getSideEmoji(result)
        resultName = self.getSideName(result)

        if coinDelta > 0:
            title = "Chúc Mừng"
            description = (
                f"Chúc mừng đồng xu là **{resultName}** {resultEmoji}\n"
                f"Bạn nhận được **{formatNumber(coinDelta)}** {chillCoinEmoji}"
            )
            color = discord.Color.green()
        else:
            title = "Rất Tiếc"
            description = (
                f"Rất tiếc đồng xu là **{resultName}** {resultEmoji}\n"
                f"Bạn mất **{formatNumber(abs(coinDelta))}** {chillCoinEmoji}"
            )
            color = discord.Color.red()

        embed = discord.Embed(
            title=title,
            description=(
                f"{description}\n\n"
                f"Số dư hiện tại: **{formatNumber(newBalance)}** {chillCoinEmoji}"
            ),
            color=color,
        )

        embed.set_author(
            name=f"Lượt chơi của {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        embed.add_field(
            name="Bạn chọn",
            value=self.getSideName(choice),
            inline=True,
        )

        embed.add_field(
            name="Tiền cược",
            value=f"**{formatNumber(bet)}** {chillCoinEmoji}",
            inline=True,
        )

        return embed

    def getSideName(self, side: str):
        if side == self.HEADS:
            return "mặt ngửa"

        return "mặt xấp"

    def getSideEmoji(self, side: str):
        if side == self.HEADS:
            return CHILL_COIN_HEADS

        return CHILL_COIN_TAILS


async def setup(bot):
    await bot.add_cog(CoinFlip(bot))
