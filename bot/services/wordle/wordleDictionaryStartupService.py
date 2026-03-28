from bot.config.database import getDbSession
from bot.repository.wordGuessInputRepository import WordGuessInputRepository
from bot.services.wordle.wordleDictionaryCacheService import wordleDictionaryCacheService


class WordleDictionaryStartupService:
    def loadWordsToCache(self):
        with getDbSession() as session:
            wordGuessInputRepository = WordGuessInputRepository(session)
            words = wordGuessInputRepository.findAllGuessWords()
            wordleDictionaryCacheService.setWords(words)
            return wordleDictionaryCacheService.count()