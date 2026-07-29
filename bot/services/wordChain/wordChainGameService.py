import re
import unicodedata

from bot.config.database import getDbSession
from bot.repository.wordChainGameStateRepository import WordChainGameStateRepository
from bot.repository.wordChainWinHistoryRepository import WordChainWinHistoryRepository
from bot.services.wordChain.wordChainCacheService import wordChainCacheService
from bot.services.wordChain.wordChainStartupService import WordChainStartupService


class WordChainGameService:
    RECENT_WIN_LIMIT = 10

    def __init__(self):
        self.wordChainStartupService = WordChainStartupService()

    async def submitPhrase(self, bot, phraseInput: str, userId: int):
        normalizedPhrase = self.normalizePhrase(phraseInput)
        words = normalizedPhrase.split(" ")

        if len(words) != 2:
            return self.buildInvalidResult()

        if "-" in normalizedPhrase:
            return self.buildInvalidResult()

        phraseData = wordChainCacheService.findPhraseByText(normalizedPhrase)

        if phraseData is None:
            return self.buildInvalidResult()

        gameState = wordChainCacheService.getCurrentGameState()

        if gameState is None or gameState.get("lastWord") is None:
            gameState = await self.wordChainStartupService.startNewGame(bot)

        if gameState is None or gameState.get("lastWord") is None:
            return self.buildInvalidResult()

        if gameState.get("lastUserId") == userId:
            return {
                "success": False,
                "isCompleted": False,
                "message": "Bạn không thể tự nối tiếp từ của chính mình.",
            }

        if phraseData["firstWord"] != gameState["lastWord"]:
            return self.buildInvalidResult()

        hasNextPhrase = wordChainCacheService.hasNextPhrase(phraseData["lastWord"])

        if hasNextPhrase:
            self.updateGameState(
                lastPhraseMasterId=phraseData["id"],
                lastWord=phraseData["lastWord"],
                lastUserId=userId,
            )

            return {
                "success": True,
                "isCompleted": False,
                "newGameState": wordChainCacheService.getCurrentGameState(),
            }

        waitGameCount = self.getRecentWinWaitGameCount(phraseData["id"])

        if waitGameCount is not None:
            return {
                "success": False,
                "isCompleted": False,
                "message": f"Từ này đã được dùng trong 10 game gần nhất, hãy dùng lại từ này sau {waitGameCount} game.",
            }

        self.createWinHistory(
            userId=userId,
            phraseMasterId=phraseData["id"],
        )
        newGameState = await self.wordChainStartupService.startNewGame(bot)

        return {
            "success": True,
            "isCompleted": True,
            "newGameState": newGameState,
        }

    def updateGameState(
        self,
        lastPhraseMasterId,
        lastWord,
        lastUserId,
    ):
        with getDbSession() as session:
            gameStateRepository = WordChainGameStateRepository(session)
            gameState = gameStateRepository.findOrCreateCurrent()
            gameStateRepository.updateCurrent(
                gameState=gameState,
                lastPhraseMasterId=lastPhraseMasterId,
                lastWord=lastWord,
                lastUserId=lastUserId,
            )
            session.commit()

        wordChainCacheService.setCurrentGameState(
            lastPhraseMasterId=lastPhraseMasterId,
            lastWord=lastWord,
            lastUserId=lastUserId,
        )

    def getRecentWinWaitGameCount(self, phraseMasterId: int):
        with getDbSession() as session:
            winHistoryRepository = WordChainWinHistoryRepository(session)
            recentPhraseMasterIds = winHistoryRepository.findLatestPhraseMasterIds(
                self.RECENT_WIN_LIMIT,
            )

        for index, recentPhraseMasterId in enumerate(recentPhraseMasterIds):
            if recentPhraseMasterId == phraseMasterId:
                return self.RECENT_WIN_LIMIT - index

        return None

    def createWinHistory(self, userId: int, phraseMasterId: int):
        with getDbSession() as session:
            winHistoryRepository = WordChainWinHistoryRepository(session)
            winHistoryRepository.create(
                userId=userId,
                phraseMasterId=phraseMasterId,
            )
            session.commit()

    def normalizePhrase(self, value: str):
        value = unicodedata.normalize("NFC", value)
        value = value.strip().lower()
        value = re.sub(r"\s+", " ", value)

        return value

    def buildInvalidResult(self):
        return {
            "success": False,
            "isCompleted": False,
            "message": None,
        }
