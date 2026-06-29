import asyncio
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

from bot.commands.musicEvent.openMusicEvent import JoinMusicEventView
from bot.config.config import CHILL_STATION_GUILD_ID, DISCORD_TOKEN
from bot.config.database import getDbSession
from bot.repository.musicEventRepository import MusicEventRepository
from bot.repository.lottoEventRepository import LottoEventRepository
from bot.repository.giveawayRepository import GiveawayRepository
from bot.repository.giveawayWinnerRepository import GiveawayWinnerRepository
from bot.services.anonymousMatch.anonymousMatchCacheService import AnonymousMatchCacheService
from bot.services.autoResponder.autoResponderCacheService import AutoResponderCacheService
from bot.services.wordle.wordleStartupService import WordleStartupService
from bot.services.wordle.wordleDictionaryStartupService import WordleDictionaryStartupService
from bot.services.asset.assetImageService import assetImageService
from bot.views.giveaway.giveawayJoinButtonView import GiveawayJoinButtonView
from bot.views.giveaway.giveawayRerollView import GiveawayRerollView
from bot.views.lotto.lottoBuyTicketView import LottoBuyTicketView

autoResponderCacheService = AutoResponderCacheService()
anonymousMatchCacheService = AnonymousMatchCacheService()
wordleStartupService = WordleStartupService()
wordleDictionaryStartupService = WordleDictionaryStartupService()

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix=["cg ", "Cg "], intents=intents, help_command=None)


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
        chillStationGuild = discord.Object(id=CHILL_STATION_GUILD_ID)
        bot.tree.copy_global_to(guild=chillStationGuild)
        synced = await bot.tree.sync(guild=chillStationGuild)
        print(f"🔧 Slash commands đã sync vào Chill Station: {len(synced)} lệnh")
        autoResponderCacheService.loadKeys()
        anonymousMatchCount = anonymousMatchCacheService.loadActiveMatches()
        print(f"Loaded anonymous match cache: {anonymousMatchCount}")
        print("✅ Đã load auto responder keys")

        currentWordleGame = await wordleStartupService.loadCurrentGameToCache()
        if currentWordleGame is not None:
            print(f"✅ Đã load wordle game hiện tại: {currentWordleGame['keyWord']}")
        else:
            print("⚠️ Không load được wordle game hiện tại")

        loadedWordCount = wordleDictionaryStartupService.loadWordsToCache()
        print(f"✅ Đã load wordle dictionary: {loadedWordCount} từ")
        assetImageService.preloadAssets()
    except Exception as e:
        print(f"❌ Lỗi sync commands: {e}")

async def registerPersistentViews():
    rerollEndedAfter = datetime.now(timezone(timedelta(hours=7))).replace(
        tzinfo=None,
    ) - timedelta(days=1)

    with getDbSession() as dbSession:
        musicEventRepository = MusicEventRepository(dbSession)
        giveawayRepository = GiveawayRepository(dbSession)
        giveawayWinnerRepository = GiveawayWinnerRepository(dbSession)
        lottoEventRepository = LottoEventRepository(dbSession)
        musicEvents = musicEventRepository.findAll()
        giveaways = giveawayRepository.findActiveGiveawaysWithMessage()
        currentWinners = giveawayWinnerRepository.findCurrentWinnersByGiveawayEndedAfter(
            rerollEndedAfter,
        )
        lottoEvents = lottoEventRepository.findActiveOpenEvents()
        winnersByGiveawayId = {}

        for musicEvent in musicEvents:
            bot.add_view(JoinMusicEventView(musicEvent.id))

        for giveaway in giveaways:
            bot.add_view(GiveawayJoinButtonView(giveaway.id))

        for lottoEvent in lottoEvents:
            bot.add_view(LottoBuyTicketView(lottoEvent.id))

        for winner in currentWinners:
            winnersByGiveawayId.setdefault(winner.giveaway_id, []).append(winner)

        for giveawayId, winners in winnersByGiveawayId.items():
            bot.add_view(GiveawayRerollView(giveawayId, winners))

        print(f"✅ Đã đăng ký persistent views cho {len(musicEvents)} music event")
        print(f"✅ Đã đăng ký persistent views cho {len(giveaways)} giveaway")
        print(f"✅ Đã đăng ký persistent views cho {len(lottoEvents)} lotto event")
        print(f"✅ Đã đăng ký persistent views cho {len(winnersByGiveawayId)} giveaway reroll")


async def main():
    extensions = [
        "bot.commands.member.memberInfo",
        "bot.commands.member.loadMember",
        "bot.commands.moderation.ban",
        "bot.commands.moderation.kick",
        "bot.commands.moderation.mute",
        "bot.commands.moderation.unmute",
        "bot.commands.autoResponder.setAutoResponse",
        "bot.commands.autoResponder.deleteAutoResponse",
        "bot.commands.autoResponder.showAllAutoResponse",
        "bot.commands.member.avatar",
        "bot.commands.member.banner",
        "bot.commands.voice.joinVoice",
        "bot.commands.voice.leaveVoice",
        "bot.commands.voice.speak",
        "bot.commands.server.serverInfo",
        "bot.commands.server.listInvites",
        "bot.commands.server.syncInvites",
        "bot.commands.server.stealEmoji",
        "bot.commands.server.topInvite",
        "bot.commands.partner.checkServer",
        "bot.commands.partner.createPartner",
        "bot.commands.partner.editPartnerLink",
        "bot.commands.partner.cancelPartner",
        "bot.commands.partner.showPartner",
        #"bot.commands.wordle.wordle",
        "bot.commands.wordle.wordleTop",
        "bot.commands.donate.topDonate",
        "bot.commands.donate.topMonthlyDonate",
        "bot.commands.donate.myDonate",
        "bot.commands.moderation.delMsg",
        "bot.commands.musicEvent.createmusicevent",
        "bot.commands.musicEvent.openMusicEvent",
        "bot.commands.musicEvent.showallmusicevent",
        "bot.commands.musicEvent.closeMusicEvent",
        "bot.commands.member.memberBirthday",
        "bot.commands.farm.myFarm",
        "bot.commands.farm.shopFarm",
        "bot.commands.farm.cash",
        "bot.commands.farm.buy",
        "bot.commands.farm.buySkin",
        "bot.commands.farm.mySkin",
        "bot.commands.farm.mySilo",
        "bot.commands.farm.plant",
        "bot.commands.farm.myBarn",
        "bot.commands.farm.visitFarm",
        "bot.commands.farm.sellFarmItem",
        "bot.commands.farm.sellShopFarmItem",
        "bot.commands.farm.buyShopFarmItem",
        "bot.commands.farm.giveChillCoin",
        "bot.commands.farm.farmRecipe",
        "bot.commands.farm.farmCook",
        "bot.commands.farm.createTrainEvent",
        "bot.commands.farm.closeTrainEvent",
        "bot.commands.farm.topFishing",
        "bot.commands.farm.topTrain",
        "bot.commands.memberActivity.topChat",
        "bot.commands.member.setStaff",
        "bot.commands.member.removeStaff",
        "bot.commands.member.setMod",
        "bot.commands.member.removeMod",
        "bot.commands.member.setAdmin",
        "bot.commands.member.removeAdmin",
        "bot.commands.member.setAutoRes",
        "bot.commands.member.removeAutoRes",
        "bot.commands.memberActivity.topVoice",
        "bot.commands.memberActivity.topChatStaff",
        "bot.commands.memberActivity.myChatRank",
        "bot.commands.memberActivity.myVoiceRank",
        "bot.commands.member.noti",
        "bot.commands.chat.chat",
        "bot.commands.anonymousMatch.match",
        "bot.commands.anonymousMatch.stop",
        "bot.commands.farm.daily",
        "bot.commands.farm.task",
        "bot.commands.farm.findMarketItem",
        "bot.commands.minigame.slot",
        "bot.commands.minigame.blackjack",
        "bot.commands.minigame.coinflip",
        "bot.commands.minigame.bingo",
        "bot.commands.minigame.farmTrap",
        "bot.commands.minigame.mine",
        "bot.commands.mergeverse.topMergeGame",
        "bot.commands.mergeverse.myMergeGame",
        "bot.commands.fortune.fortune",
        "bot.commands.farm.giftcode",
        "bot.commands.giveaway.createGiveaway",
        "bot.commands.farm.createFarm",
        "bot.commands.roleShop.sellRole",
        "bot.commands.roleShop.createRoleShop",
        "bot.commands.exchange.exchange",
        "bot.commands.exchange.checkExchange",
        "bot.commands.roleShop.cancelBuyRole",
        "bot.commands.booster.setRole",
        "bot.commands.lotto.createLottoEvent",
        "bot.commands.lotto.openLottoEvent",
        "bot.commands.lotto.cancelLotto",
        "bot.commands.lotto.myLotto",
        "bot.commands.lotto.closeLottoEvent",
        "bot.commands.farm.toolBag",
        "bot.commands.farm.use",
        "bot.commands.farm.info",
        "bot.commands.homies.setHomies",
        "bot.commands.ticket.createTicket",
        "bot.events.memberJoinEvent",
        "bot.events.memberLeaveEvent",
        "bot.events.memberUpdateEvent",
        "bot.events.messageCreateEvent",
        "bot.events.boosterMessageEvent",
        "bot.events.autoModerationEvent",
        "bot.events.autoResponderEvent",
        "bot.events.anonymousMatchMessageRelayEvent",
        "bot.events.serverInviteEvent",
        "bot.events.wordleEvent",
        "bot.events.owoGiveEvent",
        "bot.events.voiceStateUpdateEvent",
        "bot.tasks.chatCountFlushTask",
        "bot.tasks.memberBirthdayTask",
        "bot.tasks.farmDryCheckTask",
        "bot.tasks.farmPestCheckTask",
        "bot.tasks.farmHarvestReadyCheckTask",
        "bot.tasks.farmCookReadyCheckTask",
        "bot.tasks.farmFishingReadyCheckTask",
        "bot.tasks.farmEggReadyCheckTask",
        "bot.tasks.farmMilkReadyCheckTask",
        "bot.tasks.farmChickenHungryCheckTask",
        "bot.tasks.farmCowHungryCheckTask",
        "bot.tasks.farmMarketAutoBuyTask",
        "bot.tasks.memberDailyActivityFlushTask",
        "bot.tasks.giveawayDrawTask",
        "bot.tasks.dailyGiveawayTask",
        "bot.tasks.monthlyDonatorGiveawayTask",
        "bot.tasks.monthlyTopChatRewardTask",
        "bot.tasks.monthlyDonatorRoleCleanupTask",
        "bot.tasks.roleShopExpireTask",
        "bot.tasks.boosterCustomRoleExpireTask",
        "bot.tasks.farmAnimalStarvationTask",
        "bot.tasks.farmTrainEventAutoTask",
        "bot.tasks.homiesRoleCheckTask",
        "bot.tasks.memberSyncTask",
        "bot.tasks.serverInviteSyncTask",
        "bot.tasks.partnerInviteCheckTask",
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
