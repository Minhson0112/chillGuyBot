import asyncio
import random

import discord
from discord.ext import commands

from bot.helper.numberFormatHelper import formatNumber
from bot.config.database import getDbSession
from bot.config.emoji import BLACKJACK_CARD_EMOJI, FARM_GAME_EMOJI, UPSIDE_DOWN_CARD
from bot.repository.memberRepository import MemberRepository


class Blackjack(commands.Cog):
    MAX_BET = 500

    HIT_EMOJI = "🟢"
    STAND_EMOJI = "🔴"

    DEALER_DRAW_ON_17_RATE = 0.2

    CARD_VALUE = {
        "A": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "J": 10,
        "Q": 10,
        "K": 10,
    }

    def __init__(self, bot):
        self.bot = bot
        self.activeUserIds = set()

    @commands.command(name="bj")
    async def blackjack(self, ctx, bet: int = None):
        if bet is None:
            await ctx.reply("Cách dùng: `cg bj <số chill coin cược>`")
            return

        if ctx.author.id in self.activeUserIds:
            await ctx.reply("Bạn đang có một ván blackjack chưa kết thúc.")
            return

        validateResult = self.validateBet(ctx.author.id, bet)

        if not validateResult["success"]:
            await ctx.reply(validateResult["message"])
            return

        self.activeUserIds.add(ctx.author.id)

        try:
            await self.playBlackjack(ctx, bet)
        except Exception as e:
            print(f"Blackjack error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi chơi blackjack.")
        finally:
            self.activeUserIds.discard(ctx.author.id)

    async def playBlackjack(self, ctx, bet: int):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        deck = self.createDeck()
        playerCards = [deck.pop(), deck.pop()]
        dealerCards = [deck.pop(), deck.pop()]

        playerTotal = self.calculateTotal(playerCards)

        embed = self.buildGameEmbed(
            ctx=ctx,
            playerCards=playerCards,
            dealerCards=dealerCards,
            bet=bet,
            isDealerHidden=True,
            statusText=(
                f"{self.HIT_EMOJI}: Rút bài\n"
                f"{self.STAND_EMOJI}: Dừng\n"
            ),
        )

        message = await ctx.reply(embed=embed)

        playerDoubleAce = self.isDoubleAce(playerCards)
        dealerDoubleAce = self.isDoubleAce(dealerCards)

        if playerDoubleAce or dealerDoubleAce:
            if playerDoubleAce and not dealerDoubleAce:
                coinDelta = bet * 4
                outcome = "Bạn có 2 lá A. Bạn thắng x4 tiền."
                color = discord.Color.green()
            elif dealerDoubleAce and not playerDoubleAce:
                coinDelta = -bet * 4
                outcome = "Nhà cái có 2 lá A. Bạn thua x4 tiền."
                color = discord.Color.red()
            else:
                coinDelta = 0
                outcome = "Cả hai đều có 2 lá A. Hòa."
                color = discord.Color.gold()

            await self.finishGame(
                ctx=ctx,
                message=message,
                playerCards=playerCards,
                dealerCards=dealerCards,
                bet=bet,
                coinDelta=coinDelta,
                outcome=outcome,
                color=color,
            )
            return

        playerBlackjack = self.isBlackjack(playerCards)
        dealerBlackjack = self.isBlackjack(dealerCards)

        if playerBlackjack or dealerBlackjack:
            if playerBlackjack and not dealerBlackjack:
                coinDelta = bet * 3
                outcome = "Blackjack. Bạn thắng x3 tiền."
                color = discord.Color.green()
            elif playerBlackjack and dealerBlackjack:
                coinDelta = -bet
                outcome = "Cả hai cùng blackjack. Nhà cái thắng."
                color = discord.Color.red()
            else:
                coinDelta = -bet
                outcome = "Nhà cái có blackjack. Bạn thua."
                color = discord.Color.red()

            await self.finishGame(
                ctx=ctx,
                message=message,
                playerCards=playerCards,
                dealerCards=dealerCards,
                bet=bet,
                coinDelta=coinDelta,
                outcome=outcome,
                color=color,
            )
            return

        await message.add_reaction(self.HIT_EMOJI)
        await message.add_reaction(self.STAND_EMOJI)

        playerBusted = False
        playerFiveCard = False

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add",
                    timeout=30.0,
                    check=lambda reaction, user: self.checkReaction(
                        reaction=reaction,
                        user=user,
                        message=message,
                        userId=ctx.author.id,
                    ),
                )
            except asyncio.TimeoutError:
                break

            if str(reaction.emoji) == self.HIT_EMOJI:
                await self.removeReaction(message, reaction.emoji, user)

                playerCards.append(deck.pop())
                playerTotal = self.calculateTotal(playerCards)

                if playerTotal > 21:
                    playerBusted = True
                    break

                if len(playerCards) == 5 and playerTotal <= 21:
                    playerFiveCard = True
                    break

                embed = self.buildGameEmbed(
                    ctx=ctx,
                    playerCards=playerCards,
                    dealerCards=dealerCards,
                    bet=bet,
                    isDealerHidden=True,
                    statusText=(
                        f"{self.HIT_EMOJI}: Rút bài\n"
                        f"{self.STAND_EMOJI}: Dừng\n"
                        f"Cược: **{formatNumber(bet)}** {chillCoinEmoji}"
                    ),
                )

                await message.edit(embed=embed)

            elif str(reaction.emoji) == self.STAND_EMOJI:
                break

        await self.clearReactions(message)

        if playerFiveCard:
            await self.finishGame(
                ctx=ctx,
                message=message,
                playerCards=playerCards,
                dealerCards=dealerCards,
                bet=bet,
                coinDelta=bet,
                outcome="Bạn đạt 5 lá không quá 21. Bạn thắng.",
                color=discord.Color.green(),
            )
            return

        if playerBusted:
            await self.finishGame(
                ctx=ctx,
                message=message,
                playerCards=playerCards,
                dealerCards=dealerCards,
                bet=bet,
                coinDelta=-bet,
                outcome="Bạn bị quá 21 điểm. Bạn thua.",
                color=discord.Color.red(),
            )
            return

        dealerTotal = self.calculateTotal(dealerCards)

        embed = self.buildGameEmbed(
            ctx=ctx,
            playerCards=playerCards,
            dealerCards=dealerCards,
            bet=bet,
            isDealerHidden=False,
            statusText="Nhà cái bắt đầu rút bài...",
        )
        await message.edit(embed=embed)
        await asyncio.sleep(1)

        dealerFiveCard = False

        while self.shouldDealerDraw(dealerTotal) and len(deck) > 0:
            dealerCards.append(deck.pop())
            dealerTotal = self.calculateTotal(dealerCards)

            if len(dealerCards) == 5 and dealerTotal <= 21:
                dealerFiveCard = True
                break

            embed = self.buildGameEmbed(
                ctx=ctx,
                playerCards=playerCards,
                dealerCards=dealerCards,
                bet=bet,
                isDealerHidden=False,
                statusText="Nhà cái rút bài...",
            )
            await message.edit(embed=embed)
            await asyncio.sleep(1)

        if dealerFiveCard:
            await self.finishGame(
                ctx=ctx,
                message=message,
                playerCards=playerCards,
                dealerCards=dealerCards,
                bet=bet,
                coinDelta=-bet,
                outcome="Nhà cái đạt 5 lá không quá 21. Bạn thua.",
                color=discord.Color.red(),
            )
            return

        playerTotal = self.calculateTotal(playerCards)
        dealerTotal = self.calculateTotal(dealerCards)

        if dealerTotal > 21:
            coinDelta = bet
            outcome = "Nhà cái bị quá 21 điểm. Bạn thắng."
            color = discord.Color.green()
        elif playerTotal > dealerTotal:
            coinDelta = bet
            outcome = "Bạn thắng."
            color = discord.Color.green()
        elif playerTotal == dealerTotal:
            coinDelta = 0
            outcome = "Hòa."
            color = discord.Color.gold()
        else:
            coinDelta = -bet
            outcome = "Bạn thua."
            color = discord.Color.red()

        await self.finishGame(
            ctx=ctx,
            message=message,
            playerCards=playerCards,
            dealerCards=dealerCards,
            bet=bet,
            coinDelta=coinDelta,
            outcome=outcome,
            color=color,
        )

    def validateBet(self, userId: int, bet: int):
        if bet <= 0:
            return {
                "success": False,
                "message": "Số chill coin cược phải lớn hơn 0.",
            }

        if bet > self.MAX_BET:
            return {
                "success": False,
                "message": f"Mỗi ván chỉ được cược tối đa **{formatNumber(self.MAX_BET)}** chill coin.",
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
                chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

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

    async def finishGame(
        self,
        ctx,
        message,
        playerCards,
        dealerCards,
        bet: int,
        coinDelta: int,
        outcome: str,
        color,
    ):
        newBalance = self.applyCoinDelta(
            userId=ctx.author.id,
            coinDelta=coinDelta,
        )

        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        if coinDelta > 0:
            resultText = f"Thắng **{formatNumber(coinDelta)}** {chillCoinEmoji}"
        elif coinDelta < 0:
            resultText = f"Thua **{formatNumber(abs(coinDelta))}** {chillCoinEmoji}"
        else:
            resultText = "Không thay đổi số dư"

        embed = self.buildGameEmbed(
            ctx=ctx,
            playerCards=playerCards,
            dealerCards=dealerCards,
            bet=bet,
            isDealerHidden=False,
            statusText=(
                f"{outcome}\n"
                f"Kết quả: {resultText}\n"
                f"Số dư hiện tại: **{formatNumber(newBalance)}** {chillCoinEmoji}"
            ),
            color=color,
        )

        await message.edit(embed=embed)

    def applyCoinDelta(
        self,
        userId: int,
        coinDelta: int,
    ):
        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            member = memberRepository.findByUserId(userId)

            if member is None:
                return 0

            member.chill_coin += coinDelta
            session.commit()

            return member.chill_coin

    def createDeck(self):
        deck = []

        for rank, cardEmojis in BLACKJACK_CARD_EMOJI.items():
            for cardEmoji in cardEmojis:
                deck.append({
                    "rank": rank,
                    "emoji": cardEmoji,
                    "value": self.CARD_VALUE[rank],
                })

        random.shuffle(deck)

        return deck

    def calculateTotal(self, cards):
        return sum(card["value"] for card in cards)

    def isBlackjack(self, cards):
        if len(cards) != 2:
            return False

        ranks = [card["rank"] for card in cards]

        return "A" in ranks and any(rank in ["10", "J", "Q", "K"] for rank in ranks)

    def isDoubleAce(self, cards):
        if len(cards) != 2:
            return False

        return cards[0]["rank"] == "A" and cards[1]["rank"] == "A"

    def shouldDealerDraw(self, dealerTotal: int):
        if dealerTotal < 17:
            return True

        if dealerTotal == 17:
            return random.random() < self.DEALER_DRAW_ON_17_RATE

        return False

    def checkReaction(
        self,
        reaction,
        user,
        message,
        userId: int,
    ):
        return (
            user.id == userId
            and reaction.message.id == message.id
            and str(reaction.emoji) in [self.HIT_EMOJI, self.STAND_EMOJI]
        )

    async def removeReaction(self, message, emoji, user):
        try:
            await message.remove_reaction(emoji, user)
        except Exception:
            pass

    async def clearReactions(self, message):
        try:
            await message.clear_reactions()
        except Exception:
            pass

    def buildGameEmbed(
        self,
        ctx,
        playerCards,
        dealerCards,
        bet: int,
        isDealerHidden: bool,
        statusText: str,
        color=None,
    ):
        if color is None:
            color = discord.Color.green()

        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        embed = discord.Embed(
            title="Blackjack",
            description=statusText,
            color=color,
        )

        embed.set_author(
            name=f"Ván bài của {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        embed.add_field(
            name=f"Bài của bạn - {self.calculateTotal(playerCards)} điểm",
            value=self.formatCards(playerCards),
            inline=False,
        )

        if isDealerHidden:
            dealerDisplay = self.formatHiddenDealerCards(dealerCards)
            dealerTitle = "Bài của nhà cái"
        else:
            dealerDisplay = self.formatCards(dealerCards)
            dealerTitle = f"Bài của nhà cái - {self.calculateTotal(dealerCards)} điểm"

        embed.add_field(
            name=dealerTitle,
            value=dealerDisplay,
            inline=False,
        )

        embed.add_field(
            name="Cược",
            value=f"**{formatNumber(bet)}** {chillCoinEmoji}",
            inline=True,
        )

        embed.set_footer(text="Rút bài hoặc dừng trong vòng 30 giây.")

        return embed

    def formatCards(self, cards):
        return " ".join(card["emoji"] for card in cards)

    def formatHiddenDealerCards(self, cards):
        if not cards:
            return "-"

        hiddenCards = [UPSIDE_DOWN_CARD for _ in cards[1:]]

        return " ".join([cards[0]["emoji"]] + hiddenCards)



async def setup(bot):
    await bot.add_cog(Blackjack(bot))
