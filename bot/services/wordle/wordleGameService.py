from bot.config.config import WORDLE_LETTER_EMOJI
from bot.config.database import getDbSession
from bot.repository.memberRepository import MemberRepository
from bot.repository.wordGuessHistoryRepository import WordGuessHistoryRepository
from bot.repository.wordRepository import WordRepository
from bot.services.wordle.wordleCacheService import wordleCacheService


class WordleGameService:
    def guessWord(self, guessedWord: str, guessedByUserId: int):
        currentGame = wordleCacheService.getCurrentGame()
        if currentGame is None:
            return {
                "success": False,
                "message": "Hiện tại chưa có từ nào đang được chơi.",
            }

        keyWord = currentGame["keyWord"].upper()
        guessedWord = guessedWord.upper().strip()

        if len(guessedWord) != len(keyWord):
            return {
                "success": False,
                "message": f"Từ đoán phải có đúng {len(keyWord)} ký tự.",
            }

        guessEmojiRow = self.buildGuessEmojiRow(keyWord, guessedWord)
        isCompleted = guessedWord == keyWord

        if not isCompleted:
            return {
                "success": True,
                "isCompleted": False,
                "guessEmojiRow": guessEmojiRow,
                "message": None,
            }

        nextGame = self.finishCurrentRoundAndStartNewRound(guessedByUserId)

        if nextGame is None:
            return {
                "success": False,
                "message": "Đã đoán đúng nhưng không thể tạo vòng chơi mới.",
            }

        return {
            "success": True,
            "isCompleted": True,
            "guessEmojiRow": guessEmojiRow,
            "winnerUserId": guessedByUserId,
            "completedWord": keyWord,
            "nextWordLength": len(nextGame["keyWord"]),
            "message": "Chúc mừng, bạn đã hoàn thành từ khóa.",
        }

    def buildGuessEmojiRow(self, keyWord: str, guessedWord: str) -> str:
        result = []

        for index in range(len(keyWord)):
            guessedLetter = guessedWord[index]

            if guessedLetter == keyWord[index]:
                result.append(WORDLE_LETTER_EMOJI["green"][guessedLetter])
            else:
                result.append(WORDLE_LETTER_EMOJI["gray"][guessedLetter])

        return "".join(result)

    def finishCurrentRoundAndStartNewRound(self, guessedByUserId: int):
        currentGame = wordleCacheService.getCurrentGame()
        if currentGame is None:
            return None

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            wordRepository = WordRepository(session)
            wordGuessHistoryRepository = WordGuessHistoryRepository(session)

            member = memberRepository.incrementCorrectWordGuessCount(guessedByUserId)
            if member is None:
                session.rollback()
                return None

            updatedHistory = wordGuessHistoryRepository.updateGuessedByUserId(
                currentGame["historyId"],
                guessedByUserId,
            )
            if updatedHistory is None:
                session.rollback()
                return None

            randomWord = wordRepository.findRandomWord()
            if randomWord is None:
                session.rollback()
                return None

            newHistory = wordGuessHistoryRepository.create({
                "word_id": randomWord.id,
                "guessed_by_user_id": None,
            })

            session.commit()

            wordleCacheService.setCurrentGame(
                historyId=newHistory.id,
                wordId=randomWord.id,
                keyWord=randomWord.key_word,
            )

            return wordleCacheService.getCurrentGame()
