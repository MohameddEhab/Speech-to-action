from faster_whisper import WhisperModel

_model = None

def get_whisper_model(model_size: str = "small"):
    global _model
    if _model is None:
        _model = WhisperModel(
            model_size_or_path=model_size,
            device="cpu",       
            compute_type="int8" 
        )
    return _model


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe an audio file to text
    """
    model = get_whisper_model()

    segments, _ = model.transcribe(
        audio_path,
        language="en",
        beam_size=5
    )

    text = " ".join(seg.text for seg in segments)
    return text.strip()