from TTS.api import TTS

print("Loading TTS model...")

# Preload TTS model at startup (avoids first-request delay)
tts = TTS(model_name="tts_models/en/ljspeech/vits")

print("TTS model loaded!")


def speak(text: str, output_path="response.wav"):
    """
    Convert text to speech
    """
    tts.tts_to_file(
        text=text,
        file_path=output_path
    )
    return output_path