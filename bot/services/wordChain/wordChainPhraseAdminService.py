import re
import unicodedata

from bot.config.database import getDbSession
from bot.repository.wordChainPhraseMasterRepository import WordChainPhraseMasterRepository
from bot.services.wordChain.wordChainCacheService import wordChainCacheService


class WordChainPhraseAdminService:
    def addPhrases(self, phraseInput: str):
        phraseLines = self.extractPhraseLines(phraseInput)
        createdCount = 0
        updatedCount = 0
        skippedPhrases = []

        with getDbSession() as session:
            phraseMasterRepository = WordChainPhraseMasterRepository(session)

            for phraseLine in phraseLines:
                normalizedPhrase = self.normalizePhrase(phraseLine)
                validateResult = self.validatePhrase(normalizedPhrase)

                if not validateResult["success"]:
                    skippedPhrases.append({
                        "phrase": phraseLine,
                        "reason": validateResult["reason"],
                    })
                    continue

                words = normalizedPhrase.split(" ")
                _, isCreated = phraseMasterRepository.upsertPhrase(
                    phrase=normalizedPhrase,
                    normalizedPhrase=normalizedPhrase,
                    firstWord=words[0],
                    lastWord=words[1],
                )

                if isCreated:
                    createdCount += 1
                else:
                    updatedCount += 1

            phrases = phraseMasterRepository.findAllActive()
            wordChainCacheService.setPhrases(phrases)
            cacheCount = wordChainCacheService.countPhrases()
            session.commit()

        return {
            "createdCount": createdCount,
            "updatedCount": updatedCount,
            "skippedCount": len(skippedPhrases),
            "skippedPhrases": skippedPhrases,
            "cacheCount": cacheCount,
        }

    def extractPhraseLines(self, phraseInput: str):
        return [
            line
            for line in phraseInput.splitlines()
            if line.strip()
        ]

    def normalizePhrase(self, value: str):
        value = unicodedata.normalize("NFC", value)
        value = value.strip().lower()
        value = re.sub(r"\s+", " ", value)

        return value

    def validatePhrase(self, phrase: str):
        if not phrase:
            return {
                "success": False,
                "reason": "rỗng",
            }

        if "-" in phrase:
            return {
                "success": False,
                "reason": "có dấu -",
            }

        if len(phrase.split(" ")) != 2:
            return {
                "success": False,
                "reason": "không phải cụm đúng 2 từ",
            }

        return {
            "success": True,
            "reason": None,
        }
