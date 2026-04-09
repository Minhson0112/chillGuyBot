import asyncio

import discord
from discord import app_commands
from discord.ext import commands, tasks

from bot.commands.openMusicEvent import JoinMusicEventView
from bot.config.config import DISCORD_TOKEN
from bot.config.database import getDbSession
from bot.repository.musicEventRepository import MusicEventRepository
from bot.services.autoResponder.autoResponderCacheService import AutoResponderCacheService
from bot.services.wordle.wordleStartupService import WordleStartupService
from bot.services.wordle.wordleDictionaryStartupService import WordleDictionaryStartupService

autoResponderCacheService = AutoResponderCacheService()
wordleStartupService = WordleStartupService()
wordleDictionaryStartupService = WordleDictionaryStartupService()

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
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
        return

    print(f"❌ App command error: {error}")

    if interaction.response.is_done():
        await interaction.followup.send("Đã xảy ra lỗi khi thực hiện lệnh.", ephemeral=True)
    else:
        await interaction.response.send_message("Đã xảy ra lỗi khi thực hiện lệnh.", ephemeral=True)


@bot.event
async def on_ready():
    print(f"✅ Bot đã đăng nhập với tên: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"🔧 Slash commands đã sync: {len(synced)} lệnh")
        autoResponderCacheService.loadKeys()
        print("✅ Đã load auto responder keys")

        currentWordleGame = await wordleStartupService.loadCurrentGameToCache()
        if currentWordleGame is not None:
            print(f"✅ Đã load wordle game hiện tại: {currentWordleGame['keyWord']}")
        else:
            print("⚠️ Không load được wordle game hiện tại")

        loadedWordCount = wordleDictionaryStartupService.loadWordsToCache()
        print(f"✅ Đã load wordle dictionary: {loadedWordCount} từ")
    except Exception as e:
        print(f"❌ Lỗi sync commands: {e}")

    if not update_status.is_running():
        update_status.start()


async def registerPersistentViews():
    with getDbSession() as dbSession:
        musicEventRepository = MusicEventRepository(dbSession)
        musicEvents = musicEventRepository.findAllOpenEvents()

        for musicEvent in musicEvents:
            bot.add_view(JoinMusicEventView(musicEvent.id))

        print(f"✅ Đã đăng ký persistent views cho {len(musicEvents)} music event")


async def main():
    extensions = [
        "bot.commands.memberInfo",
        "bot.commands.loadMember",
        "bot.commands.ban",
        "bot.commands.kick",
        "bot.commands.mute",
        "bot.commands.unmute",
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
        #"bot.commands.wordle",
        "bot.commands.wordleTop",
        "bot.commands.topDonate",
        "bot.commands.myDonate",
        "bot.commands.delMsg",
        "bot.commands.createmusicevent",
        "bot.commands.openMusicEvent",
        "bot.commands.showallmusicevent",
        "bot.commands.closeMusicEvent",
        "bot.events.memberJoinEvent",
        "bot.events.memberLeaveEvent",
        "bot.events.messageCreateEvent",
        "bot.events.autoModerationEvent",
        "bot.events.autoResponderEvent",
        "bot.events.wordleEvent",
        "bot.events.owoDonateEvent",
        "bot.tasks.chatCountFlushTask",
    ]

    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ Đã load {ext}")
        except Exception as e:
            print(f"❌ Không thể load {ext}: {e}")

    await registerPersistentViews()

    await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())