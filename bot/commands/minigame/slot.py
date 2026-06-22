import asyncio
import random

import discord
from discord.ext import commands

from bot.helper.numberFormatHelper import formatNumber
from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.repository.memberRepository import MemberRepository


class Slot(commands.Cog):
    MAX_BET = 500

    SLOT_EMOJIS = [
        "🍒",
        "🍋",
        "🍊",
        "🍇",
        "🍉",
        "⭐",
        "💎",
    ]

    def __init__(self, bot):
        self.bot = bot
        self.activeUserIds = set()

    @commands.command(name="slot")
    async def slot(self, ctx, bet: int = None):
        if bet is None:
            await ctx.reply("Cách dùng: `cg slot <số chill coin cược>`")
            return

        if ctx.author.id in self.activeUserIds:
            await ctx.reply("Bạn đang có một lượt slot chưa kết thúc.")
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
            await self.playSlot(ctx, bet)

        except Exception as e:
            print(f"Slot error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi chơi slot.")

        finally:
            self.activeUserIds.discard(ctx.author.id)

    async def playSlot(
        self,
        ctx,
        bet: int,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        outcome = [
            random.choice(self.SLOT_EMOJIS),
            random.choice(self.SLOT_EMOJIS),
            random.choice(self.SLOT_EMOJIS),
        ]

        multiplier = self.calculateMultiplier(outcome)

        embed = discord.Embed(
            title="Máy Slot",
            description=(
                f"Tiền cược: **{formatNumber(bet)}** {chillCoinEmoji}\n"
                f"Đang quay thưởng..."
            ),
            color=discord.Color.gold(),
        )

        embed.set_author(
            name=f"Lượt quay của {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        message = await ctx.reply(embed=embed)

        await asyncio.sleep(0.5)
        await message.edit(
            embed=self.buildRollingEmbed(
                ctx=ctx,
                displayText=f"{outcome[0]}",
                bet=bet,
            )
        )

        await asyncio.sleep(0.5)
        await message.edit(
            embed=self.buildRollingEmbed(
                ctx=ctx,
                displayText=f"{outcome[0]} | {outcome[1]}",
                bet=bet,
            )
        )

        await asyncio.sleep(0.5)
        await message.edit(
            embed=self.buildRollingEmbed(
                ctx=ctx,
                displayText=f"{outcome[0]} | {outcome[1]} | {outcome[2]}",
                bet=bet,
            )
        )

        await asyncio.sleep(1)

        applyResult = self.applySlotResult(
            userId=ctx.author.id,
            bet=bet,
            multiplier=multiplier,
        )

        if not applyResult["success"]:
            await message.edit(
                embed=discord.Embed(
                    title="Máy Slot",
                    description=applyResult["message"],
                    color=discord.Color.red(),
                )
            )
            return

        finalEmbed = self.buildFinalEmbed(
            ctx=ctx,
            outcome=outcome,
            bet=bet,
            multiplier=multiplier,
            coinDelta=applyResult["coinDelta"],
            newBalance=applyResult["newBalance"],
        )

        await message.edit(embed=finalEmbed)

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
                    f"Mỗi lượt slot chỉ được cược tối đa "
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

    def applySlotResult(
        self,
        userId: int,
        bet: int,
        multiplier: int,
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
                        f"Số dư của bạn không đủ để hoàn tất lượt quay. "
                        f"Cần **{formatNumber(bet)}** {chillCoinEmoji}, "
                        f"hiện có **{formatNumber(member.chill_coin)}** {chillCoinEmoji}."
                    ),
                }

            if multiplier > 0:
                reward = bet * multiplier
                coinDelta = reward - bet
            else:
                coinDelta = -bet

            member.chill_coin += coinDelta
            newBalance = member.chill_coin

            session.commit()

            return {
                "success": True,
                "coinDelta": coinDelta,
                "newBalance": newBalance,
            }

    def calculateMultiplier(self, outcome):
        uniqueCount = len(set(outcome))

        if uniqueCount == 1:
            return 10

        if uniqueCount == 2:
            return 2

        return 0

    def buildRollingEmbed(
        self,
        ctx,
        displayText: str,
        bet: int,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        embed = discord.Embed(
            title="Máy Slot",
            description=(
                f"```txt\n{displayText}\n```\n"
                f"Tiền cược: **{formatNumber(bet)}** {chillCoinEmoji}"
            ),
            color=discord.Color.gold(),
        )

        embed.set_author(
            name=f"Lượt quay của {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        return embed

    def buildFinalEmbed(
        self,
        ctx,
        outcome,
        bet: int,
        multiplier: int,
        coinDelta: int,
        newBalance: int,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
        outcomeText = " | ".join(outcome)

        if multiplier == 10:
            resultText = (
                f"Jackpot. Bạn nhận thưởng x10.\n"
                f"Lãi: **{formatNumber(coinDelta)}** {chillCoinEmoji}"
            )
            color = discord.Color.green()

        elif multiplier == 2:
            resultText = (
                f"Bạn trúng thưởng x2.\n"
                f"Lãi: **{formatNumber(coinDelta)}** {chillCoinEmoji}"
            )
            color = discord.Color.green()

        else:
            resultText = (
                f"Không trúng thưởng.\n"
                f"Mất: **{formatNumber(abs(coinDelta))}** {chillCoinEmoji}"
            )
            color = discord.Color.red()

        embed = discord.Embed(
            title="Kết quả Máy Slot",
            description=(
                f"```txt\n{outcomeText}\n```\n"
                f"{resultText}\n\n"
                f"Số dư hiện tại: **{formatNumber(newBalance)}** {chillCoinEmoji}"
            ),
            color=color,
        )

        embed.set_author(
            name=f"Lượt quay của {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        embed.add_field(
            name="Tiền cược",
            value=f"**{formatNumber(bet)}** {chillCoinEmoji}",
            inline=True,
        )

        embed.add_field(
            name="Hệ số",
            value=f"x{multiplier}" if multiplier > 0 else "x0",
            inline=True,
        )

        return embed



async def setup(bot):
    await bot.add_cog(Slot(bot))
