import asyncio

import discord
from discord import app_commands
from discord.ext import commands, tasks

from bot.config.config import DISCORD_TOKEN
from bot.services.autoResponder.autoResponderCacheService import AutoResponderCacheService

autoResponderCacheService = AutoResponderCacheService()
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="cg ", intents=intents)


@tasks.loop(minutes=10)
async def update_status():
    guildCount = len(bot.guilds)
    await bot.change_presence(
        activity=discord.Game(name=f"trong {guildCount} server")
    )


@bot.tree.error
async def onAppCommandError(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        message = str(error)

        if interaction.response.is_done():

            await interaction.followup.send(message)
        else:
            await interaction.response.send_message(message)
        return

    print(f"❌ App command error: {error}")

    if interaction.response.is_done():
        await interaction.followup.send("Đã xảy ra lỗi khi thực hiện lệnh.")
    else:
        await interaction.response.send_message("Đã xảy ra lỗi khi thực hiện lệnh.")


@bot.event
async def on_ready():
    print(f"✅ Bot đã đăng nhập với tên: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"🔧 Slash commands đã sync: {len(synced)} lệnh")
        autoResponderCacheService.loadKeys()
        print("✅ Đã load auto responder keys")
    except Exception as e:
        print(f"❌ Lỗi sync commands: {e}")

    if not update_status.is_running():
        update_status.start()


async def main():
    extensions = [
        "bot.commands.memberInfo",
        "bot.commands.loadMember",
        "bot.commands.ban",
        "bot.commands.kick",
        "bot.commands.mute",
        "bot.commands.setAutoResponse",
        "bot.commands.deleteAutoResponse",
        "bot.commands.showAllAutoResponse",
        "bot.commands.avatar",
        "bot.commands.joinVoice",
        "bot.commands.leaveVoice",
        "bot.commands.speak",
        "bot.commands.serverInfo",
        "bot.commands.checkServer",
        "bot.commands.createPartner",
        "bot.events.memberJoinEvent",
        "bot.events.memberLeaveEvent",
        "bot.events.messageCreateEvent",
        "bot.events.autoModerationEvent",
        "bot.events.autoResponderEvent",
        "bot.tasks.chatCountFlushTask",
    ]

    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ Đã load {ext}")
        except Exception as e:
            print(f"❌ Không thể load {ext}: {e}")

    await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())