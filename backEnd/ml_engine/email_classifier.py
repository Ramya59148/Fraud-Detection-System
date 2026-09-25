import re
import torch
from typing import Dict, Any, List, Optional
from .model_manager import ModelManager


FREE_MAIL_PROVIDERS = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "mail.com"}

IMPERSONATED_ENTITIES = {
    "paypal", "netflix", "apple", "amazon", "microsoft", "google", "chase",
    "bank of america", "wells fargo", "irs", "dhl", "fedex", "usps", "dropbox"
}


def analyze_email(
    body: str,
    subject: Optional[str] = None,
    sender: Optional[str] = None
) -> Dict[str, Any]:
    body = str(body or "").strip()
    subject = str(subject or "").strip()
    sender = str(sender or "").strip()

    # Build composite text for DistilBERT
    parts = []
    if subject:
        parts.append(f"Subject: {subject}")
    if sender:
        parts.append(f"From: {sender}")
    parts.append(body)
    composite_text = "\n".join(parts).strip()

    if not composite_text:
        return {
            "verdict": "SAFE",
            "confidence": 100.0,
            "risk_score": 0.0,
            "explanation": "Empty email content provided.",
            "indicators": [],
            "probabilities": {"Safe": 100.0, "Critical": 0.0}
        }

    mm = ModelManager.get_instance()
    device = mm.device
    model = mm.email_model
    tokenizer = mm.email_tokenizer

    if model is None or tokenizer is None:
        raise RuntimeError("Email Model not loaded!")

    # 1. DistilBERT Inference
    inputs = tokenizer(
        composite_text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=1)[0]

    # In Email Model: 0 -> Critical, 1 -> Safe
    prob_critical = probabilities[0].item() * 100
    prob_safe = probabilities[1].item() * 100

    # 2. Email-Specific Threat Indicators
    indicators: List[str] = []
    full_lower = composite_text.lower()

    # Sender Analysis
    if sender:
        sender_lower = sender.lower()
        # Extract sender domain
        match = re.search(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', sender_lower)
        if match:
            sender_domain = match.group(1)
            # Check if corporate brand is claimed from a free mail provider
            for entity in IMPERSONATED_ENTITIES:
                if entity in sender_lower and sender_domain in FREE_MAIL_PROVIDERS:
                    indicators.append(f"Sender Spoofing Alert: Claims to be {entity.title()} but sent from free email service ({sender_domain})")
                    break

    # Subject line triggers
    if subject:
        subj_lower = subject.lower()
        if any(w in subj_lower for w in ["urgent", "account suspended", "action required", "unauthorized login", "payment overdue", "security notification"]):
            indicators.append("Deceptive High-Urgency Subject Line")
        if any(w in subj_lower for w in ["invoice", "receipt", "wire transfer", "payment confirmation", "tax refund"]):
            indicators.append("Financial / Billing Lure in Subject")

    # Body Links
    links = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', body)
    if len(links) > 3:
        indicators.append(f"Multiple External Hyperlinks Detected ({len(links)} links)")
    elif len(links) >= 1:
        indicators.append(f"Embedded Action Link Detected ({len(links)} link(s))")

    # Call to action phrases
    if any(p in full_lower for p in ["click here to verify", "update your billing", "confirm your identity", "reset your security credentials", "unlock your account"]):
        indicators.append("Credential Harvesting Call-to-Action")

    # Attachment lures
    if any(p in full_lower for p in ["attached invoice", "see attachment", "open the attached pdf", "download your document"]):
        indicators.append("Malicious Attachment / Payload Lure")

    # 3. Verdict Engine Mapping
    # Base risk score directly from DistilBERT phishing probability
    risk_score = prob_critical

    # Apply risk escalation for severe spoofing or phishing triggers
    if any("Sender Spoofing Alert" in ind for ind in indicators):
        risk_score = max(risk_score, 92.0)
    if any("Credential Harvesting" in ind for ind in indicators):
        risk_score = max(risk_score, 80.0)

    if risk_score >= 60.0:
        verdict = "FRAUDULENT"
        confidence = max(prob_critical, risk_score)
        explanation = (
            "This email exhibits strong indicators of a targeted phishing or business email compromise (BEC) campaign. "
            "Our DistilBERT email detector identified social engineering tactics designed to induce panic or credential theft."
        )
    elif risk_score >= 35.0 or (prob_critical > 30.0 and len(indicators) >= 2):
        verdict = "SUSPICIOUS"
        confidence = max(prob_critical, 65.0)
        explanation = (
            "The email presents suspicious characteristics or elevated risk flags. "
            "Avoid clicking embedded links or providing credentials until the sender is verified through an out-of-band channel."
        )
    else:
        verdict = "SAFE"
        confidence = prob_safe
        explanation = (
            "This email appears clean and standard. "
            "Our AI detection model found no prominent phishing structures or malicious solicitation patterns."
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
            "subject": subject,
            "sender": sender,
            "body_length": len(body),
            "links_found": len(links),
            "extracted_urls": links[:5]
        }
    }
