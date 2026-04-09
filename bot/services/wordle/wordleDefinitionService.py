import requests
from googletrans import Translator


class WordleDefinitionService:
    DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"

    def __init__(self):
        self.translator = Translator()

    async def getDefinitionData(self, keyWord: str):
        englishEntries = self.getEnglishEntries(keyWord)
        if not englishEntries:
            return {
                "entries": [],
            }

        translatedEntries = []

        for entry in englishEntries:
            definitionVi = await self.translateToVietnamese(entry["definitionEn"])
            exampleVi = None

            if entry["exampleEn"]:
                exampleVi = await self.translateToVietnamese(entry["exampleEn"])

            translatedEntries.append({
                "partOfSpeech": entry["partOfSpeech"],
                "definitionEn": entry["definitionEn"],
                "definitionVi": definitionVi,
                "exampleEn": entry["exampleEn"],
                "exampleVi": exampleVi,
            })

        return {
            "entries": translatedEntries,
        }

    def getEnglishEntries(self, keyWord: str):
        try:
            response = requests.get(
                f"{self.DICTIONARY_API_URL}/{keyWord}",
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
        except Exception:
            return []

        if not isinstance(data, list) or not data:
            return []

        entries = []

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

                    entries.append({
                        "partOfSpeech": partOfSpeech,
                        "definitionEn": definitionText.strip(),
                        "exampleEn": exampleText.strip() if exampleText else None,
                    })

                    if len(entries) >= 3:
                        return entries

        return entries

    async def translateToVietnamese(self, text: str):
        try:
            translated = await self.translator.translate(text, src="en", dest="vi")
            return translated.text
        except Exception:
            return None


wordleDefinitionService = WordleDefinitionService()