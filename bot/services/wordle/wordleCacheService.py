class WordleCacheService:
    def __init__(self):
        self.currentGame = None

    def setCurrentGame(self, historyId, wordId, keyWord, definitionEntries=None):
        self.currentGame = {
            "historyId": historyId,
            "wordId": wordId,
            "keyWord": keyWord,
            "definitionEntries": definitionEntries or [],
        }

    def getCurrentGame(self):
        return self.currentGame

    def clearCurrentGame(self):
        self.currentGame = None

    def hasCurrentGame(self):
        return self.currentGame is not None

    def getHistoryId(self):
        if self.currentGame is None:
            return None
        return self.currentGame["historyId"]

    def getWordId(self):
        if self.currentGame is None:
            return None
        return self.currentGame["wordId"]

    def getKeyWord(self):
        if self.currentGame is None:
            return None
        return self.currentGame["keyWord"]

    def getDefinitionEntries(self):
        if self.currentGame is None:
            return []
        return self.currentGame["definitionEntries"]


wordleCacheService = WordleCacheService()