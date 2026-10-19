import io
from importlib.metadata import version
from time import monotonic

import edge_tts

class TextToSpeechService:
    VOICE_NAME = "vi-VN-HoaiMyNeural"

    async def synthesize(self, text: str) -> io.BytesIO:
        startedAt = monotonic()
        print(
            f"[TTS] Starting: edge-tts={version('edge-tts')}, voice={self.VOICE_NAME}, textLength={len(text)}",
            flush=True,
        )
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.VOICE_NAME,
        )

        audioBuffer = io.BytesIO()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                if audioBuffer.tell() == 0:
                    print(f"[TTS] First audio received after {monotonic() - startedAt:.2f}s", flush=True)
                audioBuffer.write(chunk["data"])

        print(
            f"[TTS] Completed: audioBytes={audioBuffer.tell()}, elapsedSeconds={monotonic() - startedAt:.2f}",
            flush=True,
        )
        audioBuffer.seek(0)
        return audioBuffer
