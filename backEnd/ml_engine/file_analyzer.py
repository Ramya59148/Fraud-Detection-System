import os
import re
import email
from email import policy
from io import BytesIO
from typing import Dict, Any

from pypdf import PdfReader

from .text_classifier import analyze_text
from .email_classifier import analyze_email
from .url_classifier import analyze_url


def extract_text_from_file(
    filename: str,
    content_bytes: bytes
) -> Dict[str, Any]:

    ext = os.path.splitext(filename)[1].lower()

    subject = None
    sender = None
    extracted_text = ""
    is_email = False

    # ============================================================
    # EMAIL FILES
    # ============================================================
    if ext in [".eml", ".msg"]:

        is_email = True

        try:
            msg = email.message_from_bytes(
                content_bytes,
                policy=policy.default
            )

            subject = msg.get("subject", "")
            sender = msg.get("from", "")

            body_parts = []

            if msg.is_multipart():

                for part in msg.walk():

                    content_type = part.get_content_type()

                    content_disposition = str(
                        part.get("Content-Disposition")
                    )

                    if (
                        content_type == "text/plain"
                        and "attachment" not in content_disposition
                    ):

                        payload = part.get_payload(
                            decode=True
                        )

                        if payload:
                            body_parts.append(
                                payload.decode(
                                    "utf-8",
                                    errors="replace"
                                )
                            )

            else:

                payload = msg.get_payload(
                    decode=True
                )

                if payload:
                    body_parts.append(
                        payload.decode(
                            "utf-8",
                            errors="replace"
                        )
                    )

            extracted_text = "\n".join(
                body_parts
            ).strip()

            if not extracted_text:

                extracted_text = content_bytes.decode(
                    "utf-8",
                    errors="replace"
                )

        except Exception:

            extracted_text = content_bytes.decode(
                "utf-8",
                errors="replace"
            )

    # ============================================================
    # PDF FILES
    # ============================================================
    elif ext == ".pdf":

        try:

            reader = PdfReader(
                BytesIO(content_bytes)
            )

            pages = []

            for page in reader.pages:

                page_text = page.extract_text()

                if page_text:
                    pages.append(page_text)

            extracted_text = "\n".join(
                pages
            ).strip()

        except Exception:

            # Never send raw PDF binary data
            # to the text classification model.
            extracted_text = ""

    # ============================================================
    # STANDARD TEXT / LOG / JSON / CSV / HTML FILES
    # ============================================================
    else:

        try:

            extracted_text = content_bytes.decode(
                "utf-8"
            )

        except UnicodeDecodeError:

            extracted_text = content_bytes.decode(
                "latin1",
                errors="replace"
            )

    return {
        "text": extracted_text,
        "is_email": is_email,
        "subject": subject,
        "sender": sender,
        "size_bytes": len(content_bytes)
    }


def analyze_file(
    filename: str,
    content_bytes: bytes
) -> Dict[str, Any]:

    # ============================================================
    # EXTRACT FILE CONTENT
    # ============================================================
    file_info = extract_text_from_file(
        filename,
        content_bytes
    )

    text = file_info["text"]
    is_email = file_info["is_email"]

    # ============================================================
    # EMPTY / NON-TEXT FILE
    # ============================================================
    if not text.strip():

        return {
            "verdict": "SAFE",
            "confidence": 100.0,
            "risk_score": 0.0,
            "explanation": (
                f"File '{filename}' contains no "
                "inspectable text or content."
            ),
            "indicators": [
                "Empty or non-textual file payload"
            ],
            "probabilities": {
                "Safe": 100.0,
                "Fraudulent": 0.0
            },
            "metadata": {
                "filename": filename,
                "size_bytes": file_info["size_bytes"],
                "text_length": 0,
                "is_email_format": is_email,
                "subject": file_info["subject"],
                "sender": file_info["sender"],
                "character_count": 0,
                "embedded_urls_scanned": 0,
                "url_scan_details": []
            }
        }

    # ============================================================
    # PRIMARY CONTENT ANALYSIS
    # ============================================================

    if is_email:

        # Keep email analysis exactly as before.
        base_result = analyze_email(
            body=text,
            subject=file_info["subject"],
            sender=file_info["sender"]
        )

    else:

        # --------------------------------------------------------
        # DOCUMENT ANALYSIS
        # --------------------------------------------------------
        # The DistilBERT text model was trained on short messages.
        # Sending an entire PDF/document as one sequence can cause
        # false positives because the model truncates the input.
        #
        # Instead, split the document into smaller meaningful
        # chunks and analyze each chunk separately.
        # --------------------------------------------------------

        chunks = [
            chunk.strip()
            for chunk in re.split(
                r'(?<=[.!?])\s+|\n+',
                text
            )
            if chunk.strip()
        ]

        # Safety fallback in case extraction produced unusual
        # content without normal sentence/line boundaries.
        if not chunks:
            chunks = [text.strip()]

        # Analyze at most 50 chunks so extremely large files
        # cannot cause excessive model inference.
        chunks = chunks[:50]

        chunk_results = [
            analyze_text(chunk)
            for chunk in chunks
        ]

        # --------------------------------------------------------
        # FIND FRAUDULENT / SUSPICIOUS CHUNKS
        # --------------------------------------------------------

        fraud_results = [
            result
            for result in chunk_results
            if result["verdict"] == "FRAUDULENT"
        ]

        suspicious_results = [
            result
            for result in chunk_results
            if result["verdict"] == "SUSPICIOUS"
        ]

        # --------------------------------------------------------
        # AGGREGATE RESULTS
        # --------------------------------------------------------

        if fraud_results:

            # A genuinely fraudulent chunk should remain visible.
            base_result = max(
                fraud_results,
                key=lambda result: result["risk_score"]
            )

        elif suspicious_results:

            # Suspicious chunks are considered next.
            base_result = max(
                suspicious_results,
                key=lambda result: result["risk_score"]
            )

        else:

            # Otherwise select the highest-risk SAFE chunk.
            base_result = max(
                chunk_results,
                key=lambda result: result["risk_score"]
            )

        # --------------------------------------------------------
        # DOCUMENT-LEVEL RISK CALCULATION
        # --------------------------------------------------------
        #
        # A single harmless heading should not make the entire
        # document fraudulent.
        #
        # If there are no genuinely fraudulent chunks, calculate
        # the overall risk from the average chunk risk.
        # --------------------------------------------------------

        if not fraud_results:

            highest_risk = max(
                result["risk_score"]
                for result in chunk_results
            )

            average_risk = (
                sum(
                    result["risk_score"]
                    for result in chunk_results
                )
                / len(chunk_results)
            )

            # No chunk reached the fraudulent threshold.
            if highest_risk < 65.0:

                base_result = dict(base_result)

                if average_risk >= 35.0:

                    base_result["verdict"] = "SUSPICIOUS"

                else:

                    base_result["verdict"] = "SAFE"

                base_result["risk_score"] = round(
                    average_risk,
                    1
                )

                base_result["confidence"] = round(
                    100.0 - average_risk,
                    2
                )

                if base_result["verdict"] == "SAFE":

                    base_result["explanation"] = (
                        "The document was analyzed in multiple "
                        "content segments. No significant scam, "
                        "phishing, or social-engineering patterns "
                        "were detected across the document."
                    )

                else:

                    base_result["explanation"] = (
                        "The document contains some language "
                        "patterns that warrant caution, but no "
                        "individual content segment reached the "
                        "fraudulent-risk threshold."
                    )

    # ============================================================
    # URL EXTRACTION
    # ============================================================

    urls_found = list(
        set(
            re.findall(
                r'https?://[^\s<>"]+|www\.[^\s<>"]+',
                text
            )
        )
    )

    url_results = []

    has_fraud_url = False
    has_suspicious_url = False

    # Scan maximum 10 URLs per document.
    for url_str in urls_found[:10]:

        try:

            url_res = analyze_url(
                url_str
            )

            url_results.append(
                {
                    "url": url_str,
                    "verdict": url_res["verdict"],
                    "confidence": url_res["confidence"],
                    "indicators": url_res["indicators"]
                }
            )

            if url_res["verdict"] == "FRAUDULENT":

                has_fraud_url = True

            elif url_res["verdict"] == "SUSPICIOUS":

                has_suspicious_url = True

        except Exception:

            continue

    # ============================================================
    # BUILD INDICATORS
    # ============================================================

    indicators = list(
        base_result.get(
            "indicators",
            []
        )
    )

    indicators.append(
        f"File Ingestion: {filename} "
        f"({file_info['size_bytes'] / 1024:.1f} KB)"
    )

    if urls_found:

        indicators.append(
            f"Embedded Links: "
            f"{len(urls_found)} link(s) found in document"
        )

    # ============================================================
    # BASE RESULT
    # ============================================================

    risk_score = base_result["risk_score"]

    verdict = base_result["verdict"]

    confidence = base_result["confidence"]

    explanation = base_result["explanation"]

    # ============================================================
    # URL THREAT CORRELATION
    # ============================================================

    if has_fraud_url:

        verdict = "FRAUDULENT"

        risk_score = max(
            risk_score,
            94.0
        )

        confidence = max(
            confidence,
            92.0
        )

        indicators.append(
            "Critical Finding: Document contains "
            "confirmed malicious/fraudulent URL(s)"
        )

        explanation = (
            "FILE COMPROMISED: Although document text "
            "was processed, the file contains confirmed "
            "fraudulent / phishing link(s). Recipients "
            "opening this document are exposed to "
            "credential theft or deceptive web redirections."
        )

    elif has_suspicious_url:

        if verdict != "FRAUDULENT":

            verdict = "SUSPICIOUS"

            risk_score = max(
                risk_score,
                65.0
            )

            confidence = max(
                confidence,
                75.0
            )

            indicators.append(
                "Caution: Document contains "
                "unverified or suspicious external link(s)"
            )

            explanation = (
                f"POTENTIAL THREAT: File '{filename}' "
                "embeds links with suspicious characteristics. "
                "Verify link integrity before following "
                "external destinations."
            )

    # ============================================================
    # FINAL RESPONSE
    # ============================================================

    return {
        "verdict": verdict,
        "confidence": round(
            confidence,
            2
        ),
        "risk_score": round(
            risk_score,
            1
        ),
        "explanation": explanation,
        "indicators": indicators,
        "probabilities": base_result.get(
            "probabilities",
            {}
        ),
        "metadata": {
            "filename": filename,
            "size_bytes": file_info["size_bytes"],
            "is_email_format": is_email,
            "subject": file_info["subject"],
            "sender": file_info["sender"],
            "character_count": len(text),
            "embedded_urls_scanned": len(url_results),
            "url_scan_details": url_results
        }
    }