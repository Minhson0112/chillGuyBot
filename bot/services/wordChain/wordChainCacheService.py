import re
import unicodedata


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
            normalizedPhrase = self.normalizeText(phrase.normalized_phrase)
            firstWord = self.normalizeText(phrase.first_word)
            lastWord = self.normalizeText(phrase.last_word)
            phraseData = {
                "id": phrase.id,
                "phrase": self.normalizeText(phrase.phrase),
                "normalizedPhrase": normalizedPhrase,
                "firstWord": firstWord,
                "lastWord": lastWord,
            }

            phraseByText[normalizedPhrase] = phraseData
            phraseById[phrase.id] = phraseData
            phraseIdsByFirstWord.setdefault(firstWord, []).append(phrase.id)

        self.phraseByText = phraseByText
        self.phraseById = phraseById
        self.phraseIdsByFirstWord = phraseIdsByFirstWord

    def countPhrases(self):
        return len(self.phraseById)

    def findPhraseByText(self, normalizedPhrase):
        return self.phraseByText.get(self.normalizeText(normalizedPhrase))

    def hasNextPhrase(self, firstWord):
        return bool(self.phraseIdsByFirstWord.get(self.normalizeText(firstWord)))

    def setCurrentGameState(
        self,
        lastPhraseMasterId,
        lastWord,
        lastUserId,
    ):
        self.currentGameState = {
            "lastPhraseMasterId": lastPhraseMasterId,
            "lastWord": self.normalizeText(lastWord) if lastWord is not None else None,
            "lastUserId": lastUserId,
        }

    def getCurrentGameState(self):
        return self.currentGameState

    def clearCurrentGameState(self):
        self.currentGameState = None

    def normalizeText(self, value: str):
        value = unicodedata.normalize("NFC", value)
        value = value.strip().lower()
        value = re.sub(r"\s+", " ", value)

        return value


wordChainCacheService = WordChainCacheService()
