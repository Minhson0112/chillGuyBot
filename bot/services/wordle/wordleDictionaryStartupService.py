from bot.config.database import getDbSession
from bot.repository.wordGuessInputRepository import WordGuessInputRepository
from bot.repository.wordRepository import WordRepository
from bot.services.wordle.wordleDictionaryCacheService import wordleDictionaryCacheService

class WordleDictionaryStartupService:
    def loadWordsToCache(self):
        with getDbSession() as session:
            wordGuessInputRepository = WordGuessInputRepository(session)
            wordRepository = WordRepository(session)

            guessWords = wordGuessInputRepository.findAllGuessWords()
            keyWords = wordRepository.findAllKeyWords()

            allWords = guessWords + keyWords

            wordleDictionaryCacheService.setWords(allWords)
            return wordleDictionaryCacheService.count()
        