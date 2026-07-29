from bot.models.wordChainGameState import WordChainGameState


class WordChainGameStateRepository:
    GAME_STATE_ID = 1

    def __init__(self, session):
        self.session = session

    def findCurrent(self):
        return (
            self.session.query(WordChainGameState)
            .filter(WordChainGameState.id == self.GAME_STATE_ID)
            .first()
        )

    def findOrCreateCurrent(self):
        gameState = self.findCurrent()

        if gameState is not None:
            return gameState

        gameState = WordChainGameState(id=self.GAME_STATE_ID)
        self.session.add(gameState)
        self.session.flush()

        return gameState

    def updateCurrent(
        self,
        gameState: WordChainGameState,
        lastPhraseMasterId,
        lastWord,
        lastUserId,
    ):
        gameState.last_phrase_master_id = lastPhraseMasterId
        gameState.last_word = lastWord
        gameState.last_user_id = lastUserId

        self.session.flush()

        return gameState
