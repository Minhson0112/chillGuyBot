import discord
from discord.ext import commands, tasks
import asyncio
from bot.config.config import DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True  # Cho phép đọc nội dung tin nhắn
intents.guilds = True  # đếm số server
bot = commands.Bot(command_prefix="/", intents=intents) # Tạo bot instance với prefix "/"

# TASK LOOP cập nhật status
@tasks.loop(minutes=10)
async def update_status():
    guild_count = len(bot.guilds)
    await bot.change_presence(
        activity=discord.Game(name=f"trong {guild_count} server")
    )

@bot.event
async def on_ready():
    print(f"✅ Bot đã đăng nhập với tên: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"🔧 Slash commands đã sync: {len(synced)} lệnh")
    except Exception as e:
        print(f"❌ Lỗi sync commands: {e}")

    update_status.start()

# Hàm main để load các extension
async def main():
    # Danh sách các module cần load
    extensions = [
        "bot.commands.loadMember",
    ]

    # Load từng extension
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ Đã load {ext}")
        except Exception as e:
            print(f"❌ Không thể load {ext}: {e}")

    # Bắt đầu bot
    await bot.start(DISCORD_TOKEN)

# Entry point
if __name__ == "__main__":
    asyncio.run(main())