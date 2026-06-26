import random

import discord
from discord.ext import commands

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.numberFormatHelper import formatNumber
from bot.repository.memberRepository import MemberRepository


class FarmTrapGame:
    ROWS = 5
    COLS = 5
    BOMB_COUNT = 4

    FIELD_EMOJI = "🌾"
    FARMER_EMOJI = "👨‍🌾"
    GIFT_EMOJI = "🎁"
    BOMB_EMOJI = "💣"

    def __init__(self):
        self.playerPos = [self.ROWS - 1, self.COLS // 2]
        self.giftPos = (0, random.randrange(self.COLS))
        self.bombs = self.createBombs()
        self.revealedBombs = False

    def createBombs(self):
        possiblePositions = [
            (row, col)
            for row in range(1, self.ROWS)
            for col in range(self.COLS)
            if (row, col) != (self.playerPos[0], self.playerPos[1])
        ]

        return set(random.sample(possiblePositions, self.BOMB_COUNT))

    def movePlayer(self, direction: str):
        row, col = self.playerPos
        newRow = row
        newCol = col

        if direction == "up":
            newRow -= 1
        elif direction == "left":
            newCol -= 1
        elif direction == "right":
            newCol += 1
        else:
            return {
                "success": False,
                "result": "invalid",
            }

        if newRow < 0 or newRow >= self.ROWS or newCol < 0 or newCol >= self.COLS:
            return {
                "success": False,
                "result": "outOfBounds",
            }

        self.playerPos = [newRow, newCol]

        if (newRow, newCol) in self.bombs:
            self.revealedBombs = True
            return {
                "success": True,
                "result": "bomb",
            }

        if newRow == 0:
            self.revealedBombs = True

            if (newRow, newCol) == self.giftPos:
                return {
                    "success": True,
                    "result": "gift",
                }

            return {
                "success": True,
                "result": "win",
            }

        return {
            "success": True,
            "result": "moved",
        }

    def formatGrid(self):
        rows = []

        for row in range(self.ROWS):
            cells = []

            for col in range(self.COLS):
                position = (row, col)

                if [row, col] == self.playerPos and position not in self.bombs:
                    cells.append(self.FARMER_EMOJI)
                elif position == self.giftPos:
                    cells.append(self.GIFT_EMOJI)
                elif self.revealedBombs and position in self.bombs:
                    cells.append(self.BOMB_EMOJI)
                else:
                    cells.append(self.FIELD_EMOJI)

            rows.append("".join(cells))

        return "\n".join(rows)


class FarmTrapView(discord.ui.View):
    def __init__(self, cog, ctx, game: FarmTrapGame, bet: int):
        super().__init__(timeout=30)
        self.cog = cog
        self.ctx = ctx
        self.game = game
        self.bet = bet
        self.message = None
        self.isFinished = False

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "Đây không phải lượt chơi của bạn.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(label="←", style=discord.ButtonStyle.secondary, row=0)
    async def moveLeft(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handleMove(interaction, "left")

    @discord.ui.button(label="↑", style=discord.ButtonStyle.primary, row=0)
    async def moveUp(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handleMove(interaction, "up")

    @discord.ui.button(label="→", style=discord.ButtonStyle.secondary, row=0)
    async def moveRight(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handleMove(interaction, "right")

    async def handleMove(self, interaction: discord.Interaction, direction: str):
        moveResult = self.game.movePlayer(direction)

        if not moveResult["success"]:
            await interaction.response.edit_message(
                embed=self.cog.buildGameEmbed(
                    ctx=self.ctx,
                    game=self.game,
                    bet=self.bet,
                    statusText="Không thể đi ra ngoài ruộng.",
                    color=discord.Color.gold(),
                ),
                view=self,
            )
            return

        result = moveResult["result"]

        if result == "moved":
            await interaction.response.edit_message(
                embed=self.cog.buildGameEmbed(
                    ctx=self.ctx,
                    game=self.game,
                    bet=self.bet,
                    statusText="Tiếp tục tìm đường lên hàng cuối.",
                    color=discord.Color.gold(),
                ),
                view=self,
            )
            return

        if result == "bomb":
            await self.finishGame(
                interaction=interaction,
                coinDelta=-self.bet,
                statusText=(
                    f"Bạn dẫm trúng bẫy {self.game.BOMB_EMOJI}.\n"
                    f"Mất **{formatNumber(self.bet)}** {FARM_GAME_EMOJI['chill_coin']}."
                ),
                color=discord.Color.red(),
            )
            return

        if result == "gift":
            await self.finishGame(
                interaction=interaction,
                coinDelta=self.bet * 2,
                statusText=(
                    f"Bạn đến hàng cuối và mở đúng hộp quà {self.game.GIFT_EMOJI}.\n"
                    f"Nhận thưởng x3, lãi **{formatNumber(self.bet * 2)}** "
                    f"{FARM_GAME_EMOJI['chill_coin']}."
                ),
                color=discord.Color.green(),
            )
            return

        await self.finishGame(
            interaction=interaction,
            coinDelta=self.bet,
            statusText=(
                f"Bạn đã đến hàng cuối an toàn.\n"
                f"Nhận thưởng x2, lãi **{formatNumber(self.bet)}** "
                f"{FARM_GAME_EMOJI['chill_coin']}."
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
                statusText="Hết thời gian di chuyển. Lượt chơi bị hủy, không trừ coin.",
                color=discord.Color.greyple(),
            ),
            view=self,
        )

    def disableButtons(self):
        for child in self.children:
            child.disabled = True

    def cleanup(self):
        self.cog.activeUserIds.discard(self.ctx.author.id)


class FarmTrap(commands.Cog):
    MAX_BET = 500

    def __init__(self, bot):
        self.bot = bot
        self.activeUserIds = set()

    @commands.command(name="farmtrap")
    async def farmTrap(self, ctx, bet: int = None):
        if bet is None:
            await ctx.reply("Cách dùng: `cg farmtrap <số chill coin cược>`")
            return

        if ctx.author.id in self.activeUserIds:
            await ctx.reply("Bạn đang có một lượt farm trap chưa kết thúc.")
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
            game = FarmTrapGame()
            view = FarmTrapView(
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
                    statusText="Đi qua ruộng lúa và tránh bẫy. Tiến lên nằm ở nút giữa.",
                    color=discord.Color.gold(),
                ),
                view=view,
            )
            view.message = message
        except Exception as e:
            self.activeUserIds.discard(ctx.author.id)
            print(f"Farm trap error: {e}")
            await ctx.reply("Đã xảy ra lỗi khi chơi farm trap.")

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
                    f"Mỗi lượt farm trap chỉ được cược tối đa "
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
        game: FarmTrapGame,
        bet: int,
        statusText: str,
        color,
    ):
        chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

        embed = discord.Embed(
            title="Farm Trap",
            description=(
                f"```txt\n{game.formatGrid()}\n```\n"
                f"{statusText}"
            ),
            color=color,
        )

        embed.set_author(
            name=f"Lượt chơi của {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        embed.add_field(
            name="Tiền cược",
            value=f"**{formatNumber(bet)}** {chillCoinEmoji}",
            inline=True,
        )

        embed.add_field(
            name="Thưởng",
            value="Đến hàng cuối: x2\nĐúng hộp quà: x3",
            inline=True,
        )

        return embed


async def setup(bot):
    await bot.add_cog(FarmTrap(bot))
