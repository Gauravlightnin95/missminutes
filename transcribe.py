"""Optional local audio-to-text wrapper for OpenAI Whisper."""
from __future__ import annotations


class WhisperUnavailableError(RuntimeError):
    """Raised when optional Whisper dependencies have not been installed."""


def transcribe_audio(audio_path: str, model_name: str = "base", language: str | None = None) -> str:
    try:
        import whisper
    except ImportError as exc:
        raise WhisperUnavailableError(
            "Whisper is not installed. Install audio dependencies with: python -m pip install openai-whisper torch"
        ) from exc
    model = whisper.load_model(model_name)
    options: dict = {"fp16": False}
    if language:
        options["language"] = language
    result = model.transcribe(audio_path, **options)
    text = str(result.get("text", "")).strip()
    if not text:
        raise ValueError("Whisper returned no speech. Check the audio file or try a different Whisper model.")
    return text