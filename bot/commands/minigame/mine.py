import random

import discord
from discord.ext import commands

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.numberFormatHelper import formatNumber
from bot.repository.memberRepository import MemberRepository


class MineGame:
    SIZE = 4
    BOMB_COUNT = 4

    HIDDEN_EMOJI = "⬛"
    SAFE_EMOJI = "💎"
    BOMB_EMOJI = "💣"

    PROFIT_PERCENT_BY_SAFE_COUNT = {
        1: 20,
        2: 45,
        3: 80,
        4: 130,
        5: 200,
        6: 300,
        7: 450,
        8: 650,
        9: 900,
        10: 1200,
        11: 1600,
        12: 2200,
    }

    def __init__(self):
        positions = [
            (row, col)
            for row in range(self.SIZE)
            for col in range(self.SIZE)
        ]
        self.bombs = set(random.sample(positions, self.BOMB_COUNT))
        self.openedSafeCells = set()
        self.revealedBombs = False

    def openCell(self, row: int, col: int):
        position = (row, col)

        if position in self.openedSafeCells:
            return {
                "success": False,
                "result": "opened",
            }

        if position in self.bombs:
            self.revealedBombs = True
            return {
                "success": True,
                "result": "bomb",
            }

        self.openedSafeCells.add(position)

        if self.safeCount() == self.maxSafeCount():
            self.revealedBombs = True
            return {
                "success": True,
                "result": "complete",
            }

        return {
            "success": True,
            "result": "safe",
        }

    def safeCount(self):
        return len(self.openedSafeCells)

    def maxSafeCount(self):
        return self.SIZE * self.SIZE - self.BOMB_COUNT

    def calculateCoinDelta(self, bet: int):
        profitPercent = self.PROFIT_PERCENT_BY_SAFE_COUNT.get(self.safeCount(), 0)

        return bet * profitPercent // 100

    def formatMultiplierText(self):
        profitPercent = self.PROFIT_PERCENT_BY_SAFE_COUNT.get(self.safeCount(), 0)

        if profitPercent == 0:
            return "Chưa thể cashout"

        return f"+{profitPercent}%"

    def formatGrid(self):
        rows = []

        for row in range(self.SIZE):
            cells = []

            for col in range(self.SIZE):
                position = (row, col)

                if position in self.openedSafeCells:
                    cells.append(self.SAFE_EMOJI)
                elif self.revealedBombs and position in self.bombs:
                    cells.append(self.BOMB_EMOJI)
                else:
                    cells.append(self.HIDDEN_EMOJI)

            rows.append("".join(cells))

        return "\n".join(rows)


class MineCellButton(discord.ui.Button):
    def __init__(self, row: int, col: int):
        super().__init__(
            label="\u200b",
            emoji=MineGame.HIDDEN_EMOJI,
            style=discord.ButtonStyle.secondary,
            row=row,
        )
        self.cellRow = row
        self.cellCol = col

    async def callback(self, interaction: discord.Interaction):
        await self.view.handleOpenCell(
            interaction=interaction,
            button=self,
            row=self.cellRow,
            col=self.cellCol,
        )


class MineCashoutButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Cashout",
            emoji="💰",
            style=discord.ButtonStyle.success,
            row=4,
            disabled=True,
        )

    async def callback(self, interaction: discord.Interaction):
        await self.view.handleCashout(interaction)


class MineView(discord.ui.View):
    def __init__(self, cog, ctx, game: MineGame, bet: int):
        super().__init__(timeout=45)
        self.cog = cog
        self.ctx = ctx
        self.game = game
        self.bet = bet
        self.message = None
        self.isFinished = False
        self.cashoutButton = MineCashoutButton()

        for row in range(game.SIZE):
            for col in range(game.SIZE):
                self.add_item(MineCellButton(row, col))

        self.add_item(self.cashoutButton)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "Đây không phải lượt chơi của bạn.",
                ephemeral=True,
            )
            return False

        return True

    async def handleOpenCell(
        self,
        interaction: discord.Interaction,
        button: MineCellButton,
        row: int,
        col: int,
    ):
        openResult = self.game.openCell(row, col)

        if not openResult["success"]:
            await interaction.response.edit_message(
                embed=self.cog.buildGameEmbed(
                    ctx=self.ctx,
                    game=self.game,
                    bet=self.bet,
                    statusText="Ô này đã được đào rồi.",
                    color=discord.Color.gold(),
                ),
                view=self,
            )
            return

        result = openResult["result"]

        if result == "bomb":
            button.emoji = self.game.BOMB_EMOJI
            button.style = discord.ButtonStyle.danger
            await self.finishGame(
                interaction=interaction,
                coinDelta=-self.bet,
                statusText=(
                    f"Bạn đào trúng bom {self.game.BOMB_EMOJI}.\n"
                    f"Mất **{formatNumber(self.bet)}** {FARM_GAME_EMOJI['chill_coin']}."
                ),
                color=discord.Color.red(),
            )
            return

        button.emoji = self.game.SAFE_EMOJI
        button.style = discord.ButtonStyle.success
        button.disabled = True
        self.cashoutButton.disabled = False

        if result == "complete":
            await self.finishGame(
                interaction=interaction,
                coinDelta=self.game.calculateCoinDelta(self.bet),
                statusText=(
                    f"Bạn đã đào sạch toàn bộ ô an toàn.\n"
                    f"Lãi **{formatNumber(self.game.calculateCoinDelta(self.bet))}** "
                    f"{FARM_GAME_EMOJI['chill_coin']}."
                ),
                color=discord.Color.green(),
            )
            return

        await interaction.response.edit_message(
            embed=self.cog.buildGameEmbed(
                ctx=self.ctx,
                game=self.game,
                bet=self.bet,
                statusText=(
                    f"Đào trúng kim cương {self.game.SAFE_EMOJI}.\n"
                    f"Có thể cashout ngay hoặc đào tiếp để tăng thưởng."
                ),
                color=discord.Color.gold(),
            ),
            view=self,
        )

    async def handleCashout(self, interaction: discord.Interaction):
        if self.game.safeCount() == 0:
            await interaction.response.edit_message(
                embed=self.cog.buildGameEmbed(
                    ctx=self.ctx,
                    game=self.game,
                    bet=self.bet,
                    statusText="Bạn cần đào ít nhất 1 ô an toàn trước khi cashout.",
                    color=discord.Color.gold(),
                ),
                view=self,
            )
            return

        coinDelta = self.game.calculateCoinDelta(self.bet)
        self.game.revealedBombs = True

        await self.finishGame(
            interaction=interaction,
            coinDelta=coinDelta,
            statusText=(
                f"Bạn cashout sau **{self.game.safeCount()}** ô an toàn.\n"
                f"Lãi **{formatNumber(coinDelta)}** {FARM_GAME_EMOJI['chill_coin']}."
            ),
            color=discord.Color.green(),
        )

    async def finishGame(
        self,
        interaction: discord.Interaction,
        coinDelta: int,
        statusText: str,
        color,
    ):
        self.isFinished = True
        self.revealButtons()
        self.disableButtons()
        applyResult = self.cog.applyCoinDelta(
            userId=self.ctx.author.id,
            bet=self.bet,
            coinDelta=coinDelta,
        )

        if not applyResult["success"]:
            statusText = applyResult["message"]
            color = discord.Color.red()
        else:
            statusText = (
                f"{statusText}\n\n"
                f"Số dư hiện tại: **{formatNumber(applyResult['newBalance'])}** "
                f"{FARM_GAME_EMOJI['chill_coin']}"
            )

        await interaction.response.edit_message(
            embed=self.cog.buildGameEmbed(
                ctx=self.ctx,
                game=self.game,
                bet=self.bet,
                statusText=statusText,
                color=color,
            ),
            view=self,
        )

        self.cleanup()
        self.stop()

    async def on_timeout(self):
        if self.isFinished:
            return

        self.isFinished = True
        self.disableButtons()
        self.cleanup()

        if self.message is None:
            return

        await self.message.edit(
            embed=self.cog.buildGameEmbed(
                ctx=self.ctx,
                game=self.game,
                bet=self.bet,
                statusText="Hết thời gian đào mỏ. Lượt chơi bị hủy, không trừ coin.",
                color=discord.Color.greyple(),
            ),
            view=self,
        )

    def revealButtons(self):
        for child in self.children:
            if not isinstance(child, MineCellButton):
                continue

            position = (child.cellRow, child.cellCol)

            if position in self.game.bombs:
                child.emoji = self.game.BOMB_EMOJI
                child.style = discord.ButtonStyle.danger
            elif position in self.game.openedSafeCells:
                child.emoji = self.game.SAFE_EMOJI
                child.style = discord.ButtonStyle.success

    def disableButtons(self):
        for child in self.children:
            child.disabled = True

    def cleanup(self):
        self.cog.activeUserIds.discard(self.ctx.author.id)


class Mine(commands.Cog):
    MAX_BET = 500

    def __init__(self, bot):
        self.bot = bot
        self.activeUserIds = set()

    @commands.command(name="mine")
    async def mine(self, ctx, bet: int = None):
        if bet is None:
            await ctx.reply("Cách dùng: `cg mine <số chill coin cược>`")
            return

        if ctx.author.id in self.activeUserIds:
            await ctx.reply("Bạn đang có một lượt mine chưa kết thúc.")
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
            game = MineGame()
            view = MineView(
                cog=self,
                ctx=ctx,
                game=game,
                bet=bet,
            )
            message = await ctx.reply(
                embed=self.buildGameEmbed(
                    ctx=ctx,
                    game=game,
                    bet=bet,
                    statusText="Chọn ô để đào. Trúng bom mất cược, trúng kim cương thì có thể cashout.",
                    color=discord.Color.gold(),
                ),
                view=view,
            )
            view.message = message
        except Exception as e:
            self.activeUserIds.discard(ctx.author.id)
            print(f"Mine error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi chơi mine.")

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
                    f"Mỗi lượt mine chỉ được cược tối đa "
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

    def applyCoinDelta(
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

            if member.chill_coin < bet and coinDelta < 0:
                return {
                    "success": False,
                    "message": (
                        f"Số dư của bạn không đủ để hoàn tất lượt chơi. "
                        f"Cần **{formatNumber(bet)}** {chillCoinEmoji}, "
                        f"hiện có **{formatNumber(member.chill_coin)}** {chillCoinEmoji}."
                    ),
                }

            member.chill_coin += coinDelta
            newBalance = member.chill_coin

            session.commit()

            return {
                "success": True,
                "newBalance": newBalance,
            }

    def buildGameEmbed(
        self,
        ctx,
        game: MineGame,
        bet: int,
        statusText: str,
        color,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]
        currentProfit = game.calculateCoinDelta(bet)

        embed = discord.Embed(
            title="Mine",
            description=(
                f"{game.formatGrid()}\n\n"
                f"{statusText}"
            ),
            color=color,
        )

        embed.set_author(
            name=f"Lượt đào mỏ của {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        embed.add_field(
            name="Tiền cược",
            value=f"**{formatNumber(bet)}** {chillCoinEmoji}",
            inline=True,
        )

        embed.add_field(
            name="Ô an toàn",
            value=f"**{game.safeCount()}/{game.maxSafeCount()}**",
            inline=True,
        )

        embed.add_field(
            name="Cashout",
            value=(
                f"{game.formatMultiplierText()}\n"
                f"Lãi hiện tại: **{formatNumber(currentProfit)}** {chillCoinEmoji}"
            ),
            inline=False,
        )

        return embed


async def setup(bot):
    await bot.add_cog(Mine(bot))
