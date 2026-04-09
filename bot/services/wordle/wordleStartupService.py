from bot.config.database import getDbSession
from bot.repository.wordGuessHistoryRepository import WordGuessHistoryRepository
from bot.repository.wordRepository import WordRepository
from bot.services.wordle.wordleCacheService import wordleCacheService
from bot.services.wordle.wordleDefinitionService import wordleDefinitionService


class WordleStartupService:
    async def loadCurrentGameToCache(self):
        with getDbSession() as session:
            wordRepository = WordRepository(session)
            wordGuessHistoryRepository = WordGuessHistoryRepository(session)

            currentGuessingWord = wordGuessHistoryRepository.findCurrentGuessingWord()

            if currentGuessingWord is not None:
                word = wordRepository.findById(currentGuessingWord.word_id)

                if word is None:
                    return None

                definitionData = await wordleDefinitionService.getDefinitionData(word.key_word)

                wordleCacheService.setCurrentGame(
                    historyId=currentGuessingWord.id,
                    wordId=word.id,
                    keyWord=word.key_word,
                    definitionEntries=definitionData["entries"],
                )

                return wordleCacheService.getCurrentGame()

            randomWord = wordRepository.findRandomWord()
            if randomWord is None:
                return None

            newWordGuessHistory = wordGuessHistoryRepository.create({
                "word_id": randomWord.id,
                "guessed_by_user_id": None,
            })

            session.commit()

            definitionData = await wordleDefinitionService.getDefinitionData(randomWord.key_word)

            wordleCacheService.setCurrentGame(
                historyId=newWordGuessHistory.id,
                wordId=randomWord.id,
                keyWord=randomWord.key_word,
                definitionEntries=definitionData["entries"],
            )

            return wordleCacheService.getCurrentGame()