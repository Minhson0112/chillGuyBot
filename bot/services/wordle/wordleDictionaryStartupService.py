from bot.config.database import getDbSession
from bot.repository.wordRepository import WordRepository
from bot.services.wordle.wordleDictionaryCacheService import wordleDictionaryCacheService


class WordleDictionaryStartupService:
    def loadWordsToCache(self):
        with getDbSession() as session:
            wordRepository = WordRepository(session)
            words = wordRepository.findAllKeyWords()
            wordleDictionaryCacheService.setWords(words)
            return wordleDictionaryCacheService.count()