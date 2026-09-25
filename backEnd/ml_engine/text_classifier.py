import re
import torch
from typing import Dict, Any, List, Tuple
from .model_manager import ModelManager


URGENCY_KEYWORDS = [
    "urgent", "immediately", "act now", "action required", "warning",
    "suspended", "suspended immediately", "final notice", "terminated",
    "locked", "compromised", "unauthorized", "security alert"
]

FINANCIAL_KEYWORDS = [
    "winner", "prize", "cash", "lottery", "crypto", "bitcoin", "investment",
    "wire transfer", "bank account", "refund", "claim now", "free gift",
    "inheritance", "million dollars", "western union", "congratulations"
]

CREDENTIAL_KEYWORDS = [
    "password", "verify your account", "login credentials", "confirm password",
    "otp", "social security", "pin code", "identity verification"
]


def analyze_text(text: str) -> Dict[str, Any]:
    text = str(text).strip()
    if not text:
        return {
            "verdict": "SAFE",
            "confidence": 100.0,
            "risk_score": 0.0,
            "explanation": "No text provided for analysis.",
            "indicators": [],
            "probabilities": {"Safe": 100.0, "Critical": 0.0}
        }

    mm = ModelManager.get_instance()
    device = mm.device
    model = mm.text_model
    tokenizer = mm.text_tokenizer

    if model is None or tokenizer is None:
        raise RuntimeError("Text Model not loaded!")

    # 1. DistilBERT Inference
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=1)[0]

    # In Text Model: 0 -> Safe, 1 -> Critical
    prob_safe = probabilities[0].item() * 100
    prob_critical = probabilities[1].item() * 100

    # 2. Linguistic and Feature Indicators
    lower_text = text.lower()
    indicators: List[str] = []

    urgency_hits = [w for w in URGENCY_KEYWORDS if w in lower_text]
    financial_hits = [w for w in FINANCIAL_KEYWORDS if w in lower_text]
    cred_hits = [w for w in CREDENTIAL_KEYWORDS if w in lower_text]

    if urgency_hits:
        indicators.append(f"High Urgency Cues: {', '.join(urgency_hits[:3])}")
    if financial_hits:
        indicators.append(f"Financial / Prize Lures: {', '.join(financial_hits[:3])}")
    if cred_hits:
        indicators.append(f"Credential Harvesting Cues: {', '.join(cred_hits[:3])}")

    # Check for suspicious URLs in text
    urls_found = re.findall(r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?', text)
    if urls_found:
        indicators.append(f"Embedded URLs Detected ({len(urls_found)} link(s))")

    # Check excessive uppercase / capitalization
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    if caps_ratio > 0.35 and len(text) > 20:
        indicators.append("Aggressive Capitalization Pattern")

    # 3. Verdict Synthesis
    # Base risk score from model probability
    risk_score = prob_critical

    if not indicators:
        risk_score = min(risk_score, 20.0)
    # Adjust for strong heuristic red flags
    if len(cred_hits) >= 1 and len(urgency_hits) >= 1:
        risk_score = max(risk_score, 85.0)
    elif len(financial_hits) >= 2:
        risk_score = max(risk_score, 75.0)

    if risk_score >= 65.0:
        verdict = "FRAUDULENT"
        confidence = max(prob_critical, risk_score)
        explanation = (
            "This text displays classic markers of deceptive messaging, spam, or social engineering. "
            "Our DistilBERT model detected coercive, phishing, or financial lure language intended to deceive recipients."
        )
    elif risk_score >= 35.0 or (prob_critical > 30.0 and len(indicators) >= 2):
        verdict = "SUSPICIOUS"
        confidence = max(prob_critical, 60.0)
        explanation = (
            "The message exhibits borderline suspicious language patterns or moderate risk indicators. "
            "Proceed with caution and independently verify the sender's identity before interacting."
        )
    else:
        verdict = "SAFE"
        confidence = max(prob_safe, 80.0)
        explanation = (
            "No prominent scam or social engineering language detected. "
            "The text appears legitimate with standard communicative patterns."
        )

    return {
        "verdict": verdict,
        "confidence": round(confidence, 2),
        "risk_score": round(risk_score, 1),
        "explanation": explanation,
        "indicators": indicators,
        "probabilities": {
            "Safe": round(prob_safe, 2),
            "Fraudulent / Critical": round(prob_critical, 2)
        },
        "metadata": {
            "char_count": len(text),
            "word_count": len(text.split()),
            "urls_detected": len(urls_found)
        }
    }



