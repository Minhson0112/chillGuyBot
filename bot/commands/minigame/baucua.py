import os
import random
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import discord
from discord.ext import commands
from discord import app_commands

from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.numberFormatHelper import formatNumber
from bot.repository.memberRepository import MemberRepository

EMOJI_MAPPING = {
    "bau": "<:bau:1534833315759263835>",
    "cua": "<:cua:1534833318808260668>",
    "ca": "<:ca:1534833320595161088>",
    "ga": "<:ga:1534833322029613147>",
    "tom": "<:tom:1534833323543760997>",
    "nai": "<:nai:1534833317298569237>",
}

ANIMAL_NAMES = {
    "bau": "Bầu",
    "cua": "Cua",
    "ca": "Cá",
    "ga": "Gà",
    "tom": "Tôm",
    "nai": "Nai",
}


def parse_wager(wager_str: str, balance: int) -> int:
    wager_str = wager_str.strip().lower()
    if wager_str == "all":
        return balance
    wager_str = wager_str.replace(",", "").replace(" ", "")

    if wager_str.endswith("k"):
        try:
            return int(float(wager_str[:-1]) * 1000)
        except ValueError:
            raise ValueError("Số lượng cược k không hợp lệ.")
    elif wager_str.endswith("m"):
        try:
            return int(float(wager_str[:-1]) * 1000000)
        except ValueError:
            raise ValueError("Số lượng cược m không hợp lệ.")
    else:
        try:
            return int(wager_str)
        except ValueError:
            raise ValueError("Số lượng cược phải là số nguyên.")


def render_board(wagers: dict) -> BytesIO:
    assets_dir = os.path.join(os.getcwd(), "bot", "assets", "images", "baucua")
    board_path = os.path.join(assets_dir, "bancofull.png")
    image = Image.open(board_path).convert("RGBA")
    draw = ImageDraw.Draw(image)

    font_path = "bot/assets/fonts/arial.ttf"
    try:
        font = ImageFont.truetype(font_path, 36)
    except IOError:
        font = ImageFont.load_default()

    totals = {"bau": 0, "cua": 0, "ca": 0, "ga": 0, "tom": 0, "nai": 0}
    for user_id, user_bets in wagers.items():
        for animal, amount in user_bets.items():
            totals[animal] = totals.get(animal, 0) + amount

    coords = {
        "nai": (235, 192),
        "bau": (704, 192),
        "ga": (1173, 192),
        "ca": (235, 576),
        "cua": (704, 576),
        "tom": (1173, 576),
    }

    for animal, (x, y) in coords.items():
        amount = totals[animal]
        if amount > 0:
            text = formatNumber(amount)
            draw.text(
                (x, y),
                text,
                fill=(255, 255, 255, 255),
                stroke_width=3,
                stroke_fill=(0, 0, 0, 255),
                font=font,
                anchor="mm",
            )

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def render_results(rolled: list) -> BytesIO:
    assets_dir = os.path.join(os.getcwd(), "bot", "assets", "images", "baucua")
    bg_path = os.path.join(assets_dir, "winer.png")
    image = Image.open(bg_path).convert("RGBA")

    centers = [(424, 453), (705, 453), (989, 453)]

    for i, animal in enumerate(rolled):
        cx, cy = centers[i]
        filename = f"{animal}xoanen.png"
        filepath = os.path.join(assets_dir, filename)
        if os.path.exists(filepath):
            item = Image.open(filepath).convert("RGBA")
            bbox = item.getbbox()
            if bbox:
                item = item.crop(bbox)
            item.thumbnail((220, 220), Image.Resampling.LANCZOS)
            w, h = item.size
            x = cx - w // 2
            y = cy - h // 2
            image.paste(item, (x, y), item)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


class BauCuaBetModal(discord.ui.Modal, title="Đặt Cược Bầu Cua"):
    def __init__(self, session, animal_key, user_id, display_name, balance):
        super().__init__()
        self.session = session
        self.animal_key = animal_key
        self.user_id = user_id
        self.display_name = display_name
        self.balance = balance

        self.bet_input = discord.ui.TextInput(
            label=f"Ví: {formatNumber(balance)} chill coin",
            placeholder="Nhập số tiền cược (VD: 10000, 50k, 1m, all)",
            required=True,
            max_length=20,
        )
        self.add_item(self.bet_input)

    async def on_submit(self, interaction: discord.Interaction):
        if not self.session.is_active:
            await interaction.response.send_message(
                "Thời gian đặt cược đã kết thúc.",
                ephemeral=True,
            )
            return

        try:
            bet_amount = parse_wager(self.bet_input.value, self.balance)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return

        if bet_amount <= 0:
            await interaction.response.send_message(
                "Số tiền cược phải lớn hơn 0.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        with getDbSession() as db_session:
            member_repo = MemberRepository(db_session)
            member = member_repo.findByUserIdForUpdate(self.user_id)

            if member is None:
                await interaction.followup.send(
                    "Không tìm thấy thông tin tài khoản của bạn.",
                    ephemeral=True,
                )
                return

            if member.chill_coin < bet_amount:
                await interaction.followup.send(
                    f"Bạn không đủ chill coin. Hiện tại bạn có **{formatNumber(member.chill_coin)}** chill coin.",
                    ephemeral=True,
                )
                return

            user_wagers = self.session.wagers.setdefault(self.user_id, {})
            if len(user_wagers) >= 2 and self.animal_key not in user_wagers:
                await interaction.followup.send(
                    "Bạn chỉ được chọn đặt tối đa 2 ô cược khác nhau.",
                    ephemeral=True,
                )
                return

            if self.animal_key in user_wagers:
                await interaction.followup.send(
                    "Bạn không thể đặt cọc đè thêm tiền vào cửa đã chọn.",
                    ephemeral=True,
                )
                return

            member.chill_coin -= bet_amount
            db_session.commit()

        self.session.wagers[self.user_id][self.animal_key] = bet_amount
        self.session.user_names[self.user_id] = self.display_name

        try:
            embed = self.session.build_betting_embed()
            board_buffer = render_board(self.session.wagers)
            file = discord.File(board_buffer, filename="board.png")
            await self.session.message.edit(embed=embed, attachments=[file])
        except Exception as e:
            print(f"Error updating board message: {e}")

        coin_emoji = FARM_GAME_EMOJI.get("chill_coin", "")
        animal_emoji = EMOJI_MAPPING[self.animal_key]
        await interaction.followup.send(
            f"✅ Đã đặt **{formatNumber(bet_amount)}** {coin_emoji} vào {animal_emoji} **{ANIMAL_NAMES[self.animal_key]}**!",
            ephemeral=True,
        )


class BauCuaSelect(discord.ui.Select):
    def __init__(self, session):
        options = [
            discord.SelectOption(
                label="Bầu",
                emoji=discord.PartialEmoji(name="bau", id=1534833315759263835),
                value="bau",
                description="Đặt cược vào Bầu"
            ),
            discord.SelectOption(
                label="Cua",
                emoji=discord.PartialEmoji(name="cua", id=1534833318808260668),
                value="cua",
                description="Đặt cược vào Cua"
            ),
            discord.SelectOption(
                label="Cá",
                emoji=discord.PartialEmoji(name="ca", id=1534833320595161088),
                value="ca",
                description="Đặt cược vào Cá"
            ),
            discord.SelectOption(
                label="Gà",
                emoji=discord.PartialEmoji(name="ga", id=1534833322029613147),
                value="ga",
                description="Đặt cược vào Gà"
            ),
            discord.SelectOption(
                label="Tôm",
                emoji=discord.PartialEmoji(name="tom", id=1534833323543760997),
                value="tom",
                description="Đặt cược vào Tôm"
            ),
            discord.SelectOption(
                label="Nai",
                emoji=discord.PartialEmoji(name="nai", id=1534833317298569237),
                value="nai",
                description="Đặt cược vào Nai"
            ),
        ]
        super().__init__(placeholder="Chọn cửa bạn muốn đặt cược...", options=options)
        self.session = session

    async def callback(self, interaction: discord.Interaction):
        if not self.session.is_active:
            await interaction.response.send_message(
                "Thời gian đặt cược đã kết thúc.",
                ephemeral=True,
            )
            return

        animal_key = self.values[0]
        user_id = interaction.user.id
        display_name = interaction.user.display_name

        user_wagers = self.session.wagers.get(user_id, {})
        if len(user_wagers) >= 2 and animal_key not in user_wagers:
            await interaction.response.send_message(
                "Bạn chỉ được chọn tối đa 2 ô cược.",
                ephemeral=True,
            )
            return

        if animal_key in user_wagers:
            await interaction.response.send_message(
                "Bạn không thể đặt cọc đè thêm tiền vào cửa đã chọn.",
                ephemeral=True,
            )
            return

        with getDbSession() as db_session:
            member_repo = MemberRepository(db_session)
            member = member_repo.findByUserId(user_id)
            balance = member.chill_coin if member else 0

        modal = BauCuaBetModal(self.session, animal_key, user_id, display_name, balance)
        await interaction.response.send_modal(modal)


class BauCuaView(discord.ui.View):
    def __init__(self, session):
        super().__init__(timeout=120)
        self.session = session
        self.select_menu = BauCuaSelect(session)
        self.add_item(self.select_menu)


class BauCuaSession:
    def __init__(self, bot, session_id, channel):
        self.bot = bot
        self.session_id = session_id
        self.channel = channel
        self.duration = 40
        self.is_active = True
        self.wagers = {}  # userId -> {animal_key: bet_amount}
        self.user_names = {}  # userId -> display_name
        self.message = None
        self.task = None

    def build_betting_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=f"🎲 PHIÊN BẦU CUA #{self.session_id}",
            color=discord.Color.orange(),
        )
        embed.add_field(
            name="Tỉ lệ cược:",
            value="• Trúng 1: **x1.9** │ Trúng 2: **x2.8** │ Trúng 3: **x4.5**",
            inline=False,
        )

        total_blocks = 18
        progress_blocks = int((self.duration / 40) * total_blocks)
        if progress_blocks < 0:
            progress_blocks = 0
        empty_blocks = total_blocks - progress_blocks
        progress_bar = "▰" * progress_blocks + "▱" * empty_blocks

        embed.add_field(
            name=f"⏳ Thời gian cược: {self.duration} giây",
            value=f"[{progress_bar}]",
            inline=False,
        )

        total_users = len(self.wagers)
        total_coins = sum(sum(user_bets.values()) for user_bets in self.wagers.values())
        coin_emoji = FARM_GAME_EMOJI.get("chill_coin", "")
        embed.add_field(
            name="Thống kê phiên",
            value=f"👥 **{total_users}** người │ 💰 **{formatNumber(total_coins)}** {coin_emoji}",
            inline=False,
        )

        totals = {"bau": 0, "cua": 0, "ca": 0, "ga": 0, "tom": 0, "nai": 0}
        for user_id, user_bets in self.wagers.items():
            for animal, amount in user_bets.items():
                totals[animal] = totals.get(animal, 0) + amount

        bet_list = []
        for key in ["bau", "cua", "ca", "ga", "tom", "nai"]:
            emoji = EMOJI_MAPPING[key]
            name = ANIMAL_NAMES[key]
            amount = totals[key]
            bet_list.append(f"{emoji} {name} : {formatNumber(amount)}")

        divider = "╼" * 24
        embed.add_field(
            name=divider,
            value="\n".join(bet_list),
            inline=False,
        )

        embed.set_image(url="attachment://board.png")
        return embed

    async def start(self, active_sessions):
        board_buffer = render_board(self.wagers)
        file = discord.File(board_buffer, filename="board.png")

        embed = self.build_betting_embed()
        view = BauCuaView(self)

        self.message = await self.channel.send(
            embed=embed,
            file=file,
            view=view,
        )
        self.task = asyncio.create_task(self.run_countdown(active_sessions))

    async def run_countdown(self, active_sessions):
        try:
            while self.duration > 0:
                await asyncio.sleep(2)
                self.duration -= 2

                if not self.is_active:
                    break

                try:
                    embed = self.build_betting_embed()
                    board_buffer = render_board(self.wagers)
                    file = discord.File(board_buffer, filename="board.png")
                    await self.message.edit(embed=embed, attachments=[file])
                except Exception as e:
                    print(f"Error updating countdown frame: {e}")

            if self.is_active:
                await self.end_game(active_sessions)
        except Exception as e:
            print(f"Bau Cua task error: {e}")
            if self.is_active:
                await self.end_game(active_sessions)

    async def end_game(self, active_sessions):
        self.is_active = False
        active_sessions.pop(self.channel.id, None)

        try:
            await self.message.delete()
        except Exception:
            pass

        rolled = [random.choice(["bau", "cua", "ca", "ga", "tom", "nai"]) for _ in range(3)]

        assets_dir = os.path.join(os.getcwd(), "bot", "assets", "images", "baucua")
        gif_path = os.path.join(assets_dir, "baucua.gif")
        gif_file = discord.File(gif_path, filename="baucua.gif")

        try:
            shaking_msg = await self.channel.send(file=gif_file)
        except Exception as e:
            print(f"Error sending shaking gif: {e}")
            shaking_msg = None

        await asyncio.sleep(3.5)

        if shaking_msg:
            try:
                await shaking_msg.delete()
            except Exception:
                pass

        results_buffer = render_results(rolled)
        results_file = discord.File(results_buffer, filename="results.png")

        payouts_log = []
        total_pool = 0
        total_payout = 0

        rolled_counts = {}
        for anim in rolled:
            rolled_counts[anim] = rolled_counts.get(anim, 0) + 1

        coin_emoji = FARM_GAME_EMOJI.get("chill_coin", "")

        with getDbSession() as db_session:
            member_repo = MemberRepository(db_session)

            for user_id, user_bets in self.wagers.items():
                display_name = self.user_names.get(user_id, f"User {user_id}")
                member = member_repo.findByUserIdForUpdate(user_id)

                if member is None:
                    continue

                for animal, bet_amount in list(user_bets.items()):
                    total_pool += bet_amount
                    matches = rolled_counts.get(animal, 0)

                    if matches > 0:
                        rate = 1.9 if matches == 1 else 2.8 if matches == 2 else 4.5
                        win_amount = int(bet_amount * rate)
                        total_payout += win_amount
                        member.chill_coin += win_amount

                        animal_emoji = EMOJI_MAPPING[animal]
                        payouts_log.append(
                            f"✅ **{display_name}** | {animal_emoji} | (+{formatNumber(win_amount)} {coin_emoji})"
                        )
                    else:
                        animal_emoji = EMOJI_MAPPING[animal]
                        payouts_log.append(
                            f"❌ **{display_name}** | {animal_emoji} | (-{formatNumber(bet_amount)} {coin_emoji})"
                        )

            db_session.commit()

        rolled_names = " - ".join([ANIMAL_NAMES[r] for r in rolled])
        rolled_emojis = " ".join([EMOJI_MAPPING[r] for r in rolled])

        embed = discord.Embed(
            title=f"🏁 KẾT QUẢ BẦU CUA #{self.session_id}",
            color=discord.Color.green(),
        )
        embed.description = f"{rolled_emojis}\n\n**→ Kết quả: {rolled_names}**"

        if payouts_log:
            list_text = "\n".join(payouts_log)
        else:
            list_text = "*Không có ai đặt cược*"

        embed.add_field(
            name="📋 DANH SÁCH THAM GIA",
            value=(
                f"{list_text}\n\n"
                f"**Tổng cược:** {formatNumber(total_pool)} {coin_emoji} | "
                f"**Tổng trả:** {formatNumber(total_payout)} {coin_emoji}"
            ),
            inline=False
        )
        embed.set_image(url="attachment://results.png")

        await self.channel.send(embed=embed, file=results_file)


class BauCuaCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_sessions = {}

    @commands.command(name="bc")
    async def start_baucua(self, ctx):
        if ctx.guild is None:
            await ctx.reply("Lệnh này chỉ dùng được trong server.")
            return

        channel_id = ctx.channel.id
        if channel_id in self.active_sessions:
            await ctx.reply("Đã có một phiên chơi đang diễn ra, vui lòng đợi hết phiên chơi!")
            return

        session_id = random.randint(10, 99)
        session = BauCuaSession(self.bot, session_id, ctx.channel)
        self.active_sessions[channel_id] = session
        await session.start(self.active_sessions)


async def setup(bot):
    await bot.add_cog(BauCuaCommand(bot))
