import io

import edge_tts

class TextToSpeechService:
    VOICE_NAME = "vi-VN-HoaiMyNeural"

    async def synthesize(self, text: str) -> io.BytesIO:
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.VOICE_NAME,
        )

        audioBuffer = io.BytesIO()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audioBuffer.write(chunk["data"])

        audioBuffer.seek(0)
        return audioBuffer
