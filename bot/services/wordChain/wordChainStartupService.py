import discord

from bot.config.channel import WORD_CHAIN_CHANNEL_ID
from bot.config.database import getDbSession
from bot.helper.discordResolverHelper import resolveChannel
from bot.repository.wordChainGameStateRepository import WordChainGameStateRepository
from bot.repository.wordChainPhraseMasterRepository import WordChainPhraseMasterRepository
from bot.services.wordChain.wordChainCacheService import wordChainCacheService


class WordChainStartupService:
    def __init__(self):
        self.hasStarted = False

    async def startOnReady(self, bot):
        if self.hasStarted:
            return wordChainCacheService.getCurrentGameState()

        self.hasStarted = True

        with getDbSession() as session:
            phraseMasterRepository = WordChainPhraseMasterRepository(session)
            gameStateRepository = WordChainGameStateRepository(session)

            phrases = phraseMasterRepository.findAllActive()
            wordChainCacheService.setPhrases(phrases)

            gameState = gameStateRepository.findOrCreateCurrent()

            if gameState.last_word is not None:
                self.setGameStateCache(gameState)
                session.commit()
                return wordChainCacheService.getCurrentGameState()

        return await self.startNewGame(bot)

    async def startNewGame(self, bot):
        with getDbSession() as session:
            phraseMasterRepository = WordChainPhraseMasterRepository(session)
            gameStateRepository = WordChainGameStateRepository(session)

            gameState = gameStateRepository.findOrCreateCurrent()
            randomFirstWord = phraseMasterRepository.findRandomFirstWord()

            if randomFirstWord is None:
                wordChainCacheService.clearCurrentGameState()
                session.commit()
                return None

            gameStateRepository.updateCurrent(
                gameState=gameState,
                lastPhraseMasterId=None,
                lastWord=randomFirstWord,
                lastUserId=None,
            )
            self.setGameStateCache(gameState)
            session.commit()

        await self.sendNewGameMessage(bot, randomFirstWord)
        return wordChainCacheService.getCurrentGameState()

    def setGameStateCache(self, gameState):
        wordChainCacheService.setCurrentGameState(
            lastPhraseMasterId=gameState.last_phrase_master_id,
            lastWord=gameState.last_word,
            lastUserId=gameState.last_user_id,
        )

    async def sendNewGameMessage(self, bot, firstWord):
        try:
            channel = await resolveChannel(
                bot,
                WORD_CHAIN_CHANNEL_ID,
                discord.TextChannel,
            )

            if channel is None:
                return

            await channel.send(
                content=f"Trò chơi mới đã bắt đầu với từ: **{firstWord}**",
                allowed_mentions=discord.AllowedMentions(
                    users=False,
                    roles=False,
                    everyone=False,
                ),
            )
        except Exception as e:
            print(f"Send word chain new game message error: {e}")
