import requests
from googletrans import Translator


class WordleDefinitionService:
    DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"

    def __init__(self):
        self.translator = Translator()

    async def getDefinitionData(self, keyWord: str):
        englishEntry = self.getEnglishEntry(keyWord)
        if englishEntry is None:
            return {
                "entries": [],
            }

        definitionVi = await self.translateToVietnamese(englishEntry["definitionEn"])
        exampleVi = None

        if englishEntry["exampleEn"]:
            exampleVi = await self.translateToVietnamese(englishEntry["exampleEn"])

        return {
            "entries": [
                {
                    "partOfSpeech": englishEntry["partOfSpeech"],
                    "definitionEn": englishEntry["definitionEn"],
                    "definitionVi": definitionVi,
                    "exampleEn": englishEntry["exampleEn"],
                    "exampleVi": exampleVi,
                }
            ],
        }

    def getEnglishEntry(self, keyWord: str):
        try:
            response = requests.get(
                f"{self.DICTIONARY_API_URL}/{keyWord}",
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
        except Exception:
            return None

        if not isinstance(data, list) or not data:
            return None

        for entry in data:
            meanings = entry.get("meanings", [])
            for meaning in meanings:
                partOfSpeech = meaning.get("partOfSpeech")
                definitionItems = meaning.get("definitions", [])

                for definitionItem in definitionItems:
                    definitionText = definitionItem.get("definition")
                    exampleText = definitionItem.get("example")

                    if not definitionText:
                        continue

                    return {
                        "partOfSpeech": partOfSpeech,
                        "definitionEn": definitionText.strip(),
                        "exampleEn": exampleText.strip() if exampleText else None,
                    }

        return None

    async def translateToVietnamese(self, text: str):
        try:
            translated = await self.translator.translate(text, src="en", dest="vi")
            return translated.text
        except Exception:
            return None


wordleDefinitionService = WordleDefinitionService()