class WordleCacheService:
    def __init__(self):
        self.currentGame = None

    def setCurrentGame(self, historyId, wordId, keyWord, definitionEn=None, definitionVi=None):
        self.currentGame = {
            "historyId": historyId,
            "wordId": wordId,
            "keyWord": keyWord,
            "definitionEn": definitionEn,
            "definitionVi": definitionVi,
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

    def getDefinitionEn(self):
        if self.currentGame is None:
            return None
        return self.currentGame["definitionEn"]

    def getDefinitionVi(self):
        if self.currentGame is None:
            return None
        return self.currentGame["definitionVi"]


wordleCacheService = WordleCacheService()