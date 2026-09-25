from typing import Dict, Any, List, Optional
from ..database import save_scan
from .text_classifier import analyze_text
from .email_classifier import analyze_email
from .url_classifier import analyze_url
from .file_analyzer import analyze_file
from .audio_analyzer import analyze_audio_bytes
from .transcription import transcribe_audio_bytes


class VerdictEngine:
    @staticmethod
    def process_text_scan(text: str, title: Optional[str] = None) -> Dict[str, Any]:
        result = analyze_text(text)
        summary = text[:150] + ("..." if len(text) > 150 else "")
        record = save_scan(
            input_type="text",
            input_summary=summary,
            verdict=result["verdict"],
            confidence=result["confidence"],
            risk_score=result["risk_score"],
            explanation=result["explanation"],
            indicators=result.get("indicators", []),
            probabilities=result.get("probabilities", {}),
            raw_input=text,
            metadata=result.get("metadata", {})
        )
        # Merge record id/scan_id into return dictionary
        result.update(record)
        return result

    @staticmethod
    def process_email_scan(
        body: str,
        subject: Optional[str] = None,
        sender: Optional[str] = None
    ) -> Dict[str, Any]:
        result = analyze_email(body=body, subject=subject, sender=sender)
        subj_preview = f"[{subject}] " if subject else ""
        summary = (subj_preview + body)[:150] + ("..." if len(body) > 150 else "")
        record = save_scan(
            input_type="email",
            input_summary=summary,
            verdict=result["verdict"],
            confidence=result["confidence"],
            risk_score=result["risk_score"],
            explanation=result["explanation"],
            indicators=result.get("indicators", []),
            probabilities=result.get("probabilities", {}),
            raw_input=f"Subject: {subject}\nFrom: {sender}\n\n{body}",
            metadata=result.get("metadata", {})
        )
        result.update(record)
        return result

    @staticmethod
    def process_url_scan(url: str) -> Dict[str, Any]:
        result = analyze_url(url)
        summary = url[:150]
        record = save_scan(
            input_type="url",
            input_summary=summary,
            verdict=result["verdict"],
            confidence=result["confidence"],
            risk_score=result["risk_score"],
            explanation=result["explanation"],
            indicators=result.get("indicators", []),
            probabilities=result.get("probabilities", {}),
            raw_input=url,
            metadata=result.get("metadata", {})
        )
        result.update(record)
        return result

    @staticmethod
    def process_file_scan(filename: str, content_bytes: bytes) -> Dict[str, Any]:
        result = analyze_file(filename=filename, content_bytes=content_bytes)
        summary = f"File: {filename} ({len(content_bytes) / 1024:.1f} KB)"
        record = save_scan(
            input_type="file",
            input_summary=summary,
            verdict=result["verdict"],
            confidence=result["confidence"],
            risk_score=result["risk_score"],
            explanation=result["explanation"],
            indicators=result.get("indicators", []),
            probabilities=result.get("probabilities", {}),
            raw_input=summary,
            metadata=result.get("metadata", {})
        )
        result.update(record)
        return result

    @staticmethod
    def process_audio_scan(audio_bytes: bytes, filename: str = "recording.wav") -> Dict[str, Any]:
        acoustic_result = analyze_audio_bytes(audio_bytes=audio_bytes, filename=filename)

        transcription = transcribe_audio_bytes(audio_bytes=audio_bytes, filename=filename)
        transcript = transcription.get("transcript", "").strip()

        if transcript:
            text_result = analyze_text(transcript)
            result = dict(text_result)
            result["input_type"] = "audio"
            result["input_summary"] = f"Audio: {filename} | Transcript: {transcript[:150]}"

            result["indicators"] = list(text_result.get("indicators", []))
            result["indicators"].append("Speech Transcription: Audio converted to text and analyzed")

            for indicator in acoustic_result.get("indicators", []):
                result["indicators"].append(f"Acoustic Analysis: {indicator}")

            result["metadata"] = {
                **acoustic_result.get("metadata", {}),
                "transcript": transcript,
                "transcription_language": transcription.get("language", "en"),
                "transcription_enabled": True
            }

            result["explanation"] = (
                f"{text_result['explanation']} "
                "The recorded speech was transcribed and its text content was analyzed for fraud indicators."
            )
        else:
            result = dict(acoustic_result)
            result["input_type"] = "audio"
            result["input_summary"] = f"Audio: {filename} | No speech transcript detected"
            result["metadata"] = {
                **acoustic_result.get("metadata", {}),
                "transcript": "",
                "transcription_language": "en",
                "transcription_enabled": True
            }

        duration = result.get("metadata", {}).get("duration_seconds", 0)
        summary = f"Audio: {filename} ({duration}s, {len(audio_bytes) / 1024:.1f} KB)"

        record = save_scan(
            input_type="audio",
            input_summary=summary,
            verdict=result["verdict"],
            confidence=result["confidence"],
            risk_score=result["risk_score"],
            explanation=result["explanation"],
            indicators=result.get("indicators", []),
            probabilities=result.get("probabilities", {}),
            raw_input=transcript if transcript else summary,
            metadata=result.get("metadata", {})
        )

        result.update(record)
        return result

