class WordleDictionaryCacheService:
    def __init__(self):
        self.wordSet = set()

    def setWords(self, words):
        self.wordSet = {word.upper() for word in words}

    def hasWord(self, word: str) -> bool:
        return word.upper() in self.wordSet

    def clear(self):
        self.wordSet.clear()

    def count(self) -> int:
        return len(self.wordSet)


wordleDictionaryCacheService = WordleDictionaryCacheService()