import os
import subprocess
import tempfile
from typing import Dict, Any

from transformers import pipeline

_whisper = None


def _get_whisper():
    global _whisper

    if _whisper is None:
        _whisper = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-tiny.en"
        )

    return _whisper


def transcribe_audio_bytes(audio_bytes: bytes, filename: str = "recording.wav") -> Dict[str, Any]:
    if not audio_bytes:
        return {
            "transcript": "",
            "language": "en",
            "duration_seconds": 0.0
        }

    input_ext = os.path.splitext(filename)[1].lower() or ".wav"

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, f"input{input_ext}")
        wav_path = os.path.join(temp_dir, "converted.wav")

        with open(input_path, "wb") as f:
            f.write(audio_bytes)

        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel", "error",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-f", "wav",
            wav_path
        ]

        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        whisper = _get_whisper()
        result = whisper(wav_path)

        transcript = str(result.get("text", "")).strip()

        return {
            "transcript": transcript,
            "language": "en"
        }
