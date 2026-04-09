import requests
from googletrans import Translator


class WordleDefinitionService:
    DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"

    def __init__(self):
        self.translator = Translator()

    async def getDefinitionData(self, keyWord: str):
        definitionEn = self.getEnglishDefinition(keyWord)
        if not definitionEn:
            return {
                "definitionEn": None,
                "definitionVi": None,
            }

        definitionVi = await self.translateToVietnamese(definitionEn)

        return {
            "definitionEn": definitionEn,
            "definitionVi": definitionVi,
        }

    def getEnglishDefinition(self, keyWord: str):
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

        definitions = []

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

                    line = definitionText.strip()

                    if partOfSpeech:
                        line = f"({partOfSpeech}) {line}"

                    if exampleText:
                        line += f" Example: {exampleText.strip()}"

                    definitions.append(line)

                    if len(definitions) >= 3:
                        return "\n".join(definitions)

        if not definitions:
            return None

        return "\n".join(definitions)

    async def translateToVietnamese(self, text: str):
        try:
            translated = await self.translator.translate(text, src="en", dest="vi")
            return translated.text
        except Exception:
            return None


wordleDefinitionService = WordleDefinitionService()