class WordChainCacheService:
    def __init__(self):
        self.phraseByText = {}
        self.phraseById = {}
        self.phraseIdsByFirstWord = {}
        self.currentGameState = None

    def setPhrases(self, phrases):
        phraseByText = {}
        phraseById = {}
        phraseIdsByFirstWord = {}

        for phrase in phrases:
            phraseData = {
                "id": phrase.id,
                "phrase": phrase.phrase,
                "normalizedPhrase": phrase.normalized_phrase,
                "firstWord": phrase.first_word,
                "lastWord": phrase.last_word,
            }

            phraseByText[phrase.normalized_phrase] = phraseData
            phraseById[phrase.id] = phraseData
            phraseIdsByFirstWord.setdefault(phrase.first_word, []).append(phrase.id)

        self.phraseByText = phraseByText
        self.phraseById = phraseById
        self.phraseIdsByFirstWord = phraseIdsByFirstWord

    def countPhrases(self):
        return len(self.phraseById)

    def findPhraseByText(self, normalizedPhrase):
        return self.phraseByText.get(normalizedPhrase)

    def hasNextPhrase(self, firstWord):
        return bool(self.phraseIdsByFirstWord.get(firstWord))

    def setCurrentGameState(
        self,
        lastPhraseMasterId,
        lastWord,
        lastUserId,
    ):
        self.currentGameState = {
            "lastPhraseMasterId": lastPhraseMasterId,
            "lastWord": lastWord,
            "lastUserId": lastUserId,
        }

    def getCurrentGameState(self):
        return self.currentGameState

    def clearCurrentGameState(self):
        self.currentGameState = None


wordChainCacheService = WordChainCacheService()
