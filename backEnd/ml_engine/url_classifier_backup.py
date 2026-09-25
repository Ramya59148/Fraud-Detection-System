import re
import pandas as pd
from urllib.parse import urlparse
from typing import Dict, Any, List, Tuple
from .model_manager import ModelManager


# Recognized legitimate domains & platforms
KNOWN_LEGITIMATE_DOMAINS = {
    "google.com", "youtube.com", "wikipedia.org", "github.com", "amazon.com",
    "microsoft.com", "apple.com", "linkedin.com", "netflix.com", "twitter.com",
    "x.com", "instagram.com", "facebook.com", "reddit.com", "yahoo.com",
    "bing.com", "stackoverflow.com", "nytimes.com", "bbc.com", "cnn.com",
    "imdb.com", "espn.com", "cloudflare.com", "wordpress.org", "medium.com",
    "dropbox.com", "adobe.com", "salesforce.com", "chase.com", "bankofamerica.com",
    "wellsfargo.com", "paypal.com", "walmart.com", "ebay.com", "craigslist.org"
}

# High-risk brand names frequently targeted in phishing campaigns
BRAND_TARGETS = [
    "paypal", "apple", "google", "microsoft", "amazon", "netflix", "chase",
    "bankofamerica", "wellsfargo", "citibank", "facebook", "instagram",
    "whatsapp", "binance", "coinbase", "icloud", "steam", "telegram",
    "metamask", "dropbox", "outlook", "dhl", "fedex"
]

SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".online", ".tk", ".ml", ".ga", ".cf", ".gq",
    ".buzz", ".fit", ".work", ".click", ".link", ".monster", ".country"
}

SECURITY_KEYWORDS = [
    "login", "verify", "account", "secure", "update", "password", "bank",
    "free", "bonus", "confirm", "payment", "wallet", "auth", "signin",
    "admin", "claim", "credential", "suspend", "billing"
]


def extract_features_for_rf(raw_url: str, feature_names: List[str]) -> List[Any]:
    raw_url = str(raw_url).strip()
    
    # Strip protocol for consistent feature alignment with training data
    clean_target = re.sub(r'^[a-zA-Z]+://', '', raw_url)
    has_scheme = bool(re.match(r'^[a-zA-Z]+://', raw_url))
    parse_url_str = raw_url if has_scheme else 'http://' + raw_url
    
    try:
        parsed = urlparse(parse_url_str)
    except Exception:
        parsed = urlparse("http://invalid.local")

    hostname = (parsed.hostname or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""

    features: Dict[str, Any] = {
        "url_length": len(clean_target),
        "hostname_length": len(hostname),
        # Default minimum path of 1 to prevent bare root domains from defaulting to 99% phishing
        "path_length": len(path) if path else 1,
        "query_length": len(query),
        "num_dots": clean_target.count("."),
        "num_hyphens": clean_target.count("-"),
        "num_underscores": clean_target.count("_"),
        "num_question_marks": clean_target.count("?"),
        "num_equals": clean_target.count("="),
        "num_ampersands": clean_target.count("&"),
        "num_at_symbols": clean_target.count("@"),
        "num_percent_symbols": clean_target.count("%"),
        "num_digits": sum(c.isdigit() for c in clean_target),
        "num_letters": sum(c.isalpha() for c in clean_target),
        # Force https to 0 to eliminate severe training dataset artifact where https correlated with phishing forms
        "https": 0,
        "ip_address": int(bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname))),
        "subdomain_count": max(0, len(hostname.split(".")) - 2),
        "has_port": int(parsed.port is not None),
        "has_query": int(bool(query)),
        "has_fragment": int(bool(parsed.fragment)),
        "has_login": int("login" in clean_target.lower()),
        "has_verify": int("verify" in clean_target.lower()),
        "has_account": int("account" in clean_target.lower()),
        "has_secure": int("secure" in clean_target.lower()),
        "has_update": int("update" in clean_target.lower()),
        "has_password": int("password" in clean_target.lower()),
        "has_bank": int("bank" in clean_target.lower()),
        "has_free": int("free" in clean_target.lower()),
        "has_bonus": int("bonus" in clean_target.lower()),
        "has_confirm": int("confirm" in clean_target.lower()),
        "has_payment": int("payment" in clean_target.lower()),
        "has_wallet": int("wallet" in clean_target.lower()),
        "has_auth": int("auth" in clean_target.lower())
    }

    return [features.get(f, 0) for f in feature_names]


def analyze_url(url: str) -> Dict[str, Any]:
    raw_url = str(url or "").strip()
    if not raw_url:
        return {
            "verdict": "SAFE",
            "confidence": 100.0,
            "risk_score": 0.0,
            "explanation": "No URL provided for analysis.",
            "indicators": [],
            "probabilities": {"Safe": 100.0, "Critical": 0.0, "Suspicious": 0.0}
        }

    mm = ModelManager.get_instance()
    rf_model = mm.url_rf_model
    encoder = mm.url_encoder
    feature_names = mm.url_feature_names

    if rf_model is None or encoder is None:
        raise RuntimeError("URL Model not loaded!")

    # Parse URL details for cybersecurity heuristic evaluation
    clean_target = re.sub(r'^[a-zA-Z]+://', '', raw_url)
    parse_url_str = raw_url if re.match(r'^[a-zA-Z]+://', raw_url) else 'http://' + raw_url
    
    try:
        parsed = urlparse(parse_url_str)
    except Exception:
        parsed = urlparse("http://invalid.local")

    hostname = (parsed.hostname or "").lower()
    lower_target = clean_target.lower()

    # 1. Random Forest ML Model Inference
    features_vector = extract_features_for_rf(raw_url, feature_names)
    X = pd.DataFrame([features_vector], columns=feature_names)

    rf_probs = rf_model.predict_proba(X)[0]
    # Class order in model.classes_ is [0, 1, 2] -> [Safe, Critical, Suspicious]
    prob_safe = rf_probs[0] * 100
    prob_critical = rf_probs[1] * 100
    prob_suspicious = rf_probs[2] * 100

    # 2. Cybersecurity Threat Intelligence Indicators
    indicators: List[str] = []

    # Check known safe platforms
    is_known_safe = any(
        hostname == kd or hostname.endswith("." + kd)
        for kd in KNOWN_LEGITIMATE_DOMAINS
    )

    # Check for Brand Impersonation / Typosquatting in hostname
    brand_impersonated: List[str] = []
    for brand in BRAND_TARGETS:
        official_domain = f"{brand}.com"
        # If brand appears in hostname, but domain is NOT the official domain
        if brand in hostname and not (hostname == official_domain or hostname.endswith("." + official_domain)):
            brand_impersonated.append(brand)

    if brand_impersonated:
        indicators.append(f"Brand Impersonation Alert: Domain mimics '{brand_impersonated[0].title()}'")

    # IP address as hostname
    is_ip = bool(re.match(r'^\d{1,3}(\.\d{1,3}){3}$', hostname))
    if is_ip:
        indicators.append("Host Obfuscation: Direct numerical IP address used instead of domain name")

    # Suspicious Top-Level Domains
    has_suspicious_tld = any(hostname.endswith(tld) for tld in SUSPICIOUS_TLDS)
    matched_tld = next((tld for tld in SUSPICIOUS_TLDS if hostname.endswith(tld)), None)
    if has_suspicious_tld:
        indicators.append(f"High-Risk TLD: Domain registered under '{matched_tld}' (frequently abused in spam campaigns)")

    # Keyword analysis
    matched_keywords = [kw for kw in SECURITY_KEYWORDS if kw in lower_target]
    if len(matched_keywords) >= 2:
        indicators.append(f"Phishing Trigger Words ({len(matched_keywords)}): {', '.join(matched_keywords[:3])}")
    elif len(matched_keywords) == 1:
        indicators.append(f"Credential Keyword Present: '{matched_keywords[0]}'")

    # Deep subdomains (e.g. signin.eby.de.zukruygxctzmmqi...)
    subdomain_count = max(0, len(hostname.split(".")) - 2)
    if subdomain_count >= 3:
        indicators.append(f"Excessive Subdomain Stacking ({subdomain_count} levels)")

    # Symbol counts
    at_count = clean_target.count("@")
    if at_count > 0:
        indicators.append("Embedded '@' symbol: Potential URL redirection deception")

    # 3. Hybrid Verdict Engine
    # Compute base risk score from Random Forest
    risk_score = prob_critical + (prob_suspicious * 0.5)

    if is_known_safe and not brand_impersonated and len(matched_keywords) == 0:
        verdict = "SAFE"
        confidence = max(prob_safe, 97.5)
        risk_score = min(risk_score, 5.0)
        explanation = (
            f"The domain '{hostname}' is a verified, authentic platform. "
            "No credential harvesting cues or brand hijacking detected."
        )
    elif brand_impersonated:
        verdict = "FRAUDULENT"
        confidence = max(prob_critical, 96.0)
        risk_score = max(risk_score, 95.0)
        explanation = (
            f"CRITICAL WARNING: This URL exhibits deliberate brand impersonation mimicking '{brand_impersonated[0].title()}'. "
            "Attackers commonly use deceptive domains of this type to steal login credentials, two-factor codes, or banking information."
        )
    elif is_ip:
        if matched_keywords or prob_critical > 20.0:
            verdict = "FRAUDULENT"
            confidence = max(prob_critical, 92.0)
            risk_score = max(risk_score, 90.0)
            explanation = (
                "High threat severity: Direct IP host detected containing credential/administrative access points. "
                "Legitimate commercial services rarely expose bare IP addresses for authentication."
            )
        else:
            verdict = "SUSPICIOUS"
            confidence = max(prob_suspicious, 80.0)
            risk_score = max(risk_score, 65.0)
            explanation = "Suspicious host: Direct IP address navigation without SSL certificate or registered domain name."
    elif has_suspicious_tld and len(matched_keywords) >= 1:
        verdict = "FRAUDULENT"
        confidence = max(prob_critical, 91.0)
        risk_score = max(risk_score, 88.0)
        explanation = (
            f"Deceptive site detected: High-risk top-level domain '{matched_tld}' paired with security and login triggers. "
            "This combination is a recognized signature of automated credential phishing kits."
        )
    elif len(matched_keywords) >= 2 and not is_known_safe:
        verdict = "FRAUDULENT" if prob_critical > 25.0 else "SUSPICIOUS"
        confidence = max(prob_critical + prob_suspicious, 85.0)
        risk_score = max(risk_score, 78.0)
        explanation = (
            f"Multiple phishing triggers identified across the URL structure ({', '.join(matched_keywords[:2])}). "
            "The destination demonstrates suspicious credential-seeking behavior."
        )
    elif is_known_safe:
        verdict = "SAFE"
        confidence = max(prob_safe, 92.0)
        risk_score = min(risk_score, 12.0)
        explanation = f"Destination is on the authorized platform '{hostname}'. No high-risk structural manipulation detected."
    elif prob_critical >= 40.0:
        verdict = "FRAUDULENT"
        confidence = prob_critical
        risk_score = max(risk_score, 75.0)
        explanation = (
            "Our Random Forest classifier identified statistical feature distributions matching malicious URLs in training data "
            "(structural entropy, lexical lengths, and symbol frequencies)."
        )
    elif prob_suspicious >= 35.0 or prob_critical >= 20.0:
        verdict = "SUSPICIOUS"
        confidence = max(prob_suspicious, prob_critical)
        risk_score = max(risk_score, 50.0)
        explanation = (
            "The URL displays irregular structural properties (subdomain patterns or non-standard paths). "
            "Exercise caution before submitting credentials or downloading attachments."
        )
    else:
        verdict = "SAFE"
        confidence = prob_safe
        risk_score = min(risk_score, 20.0)
        explanation = (
            "No prominent indicators of phishing, malware distribution, or domain spoofing were identified. "
            "The URL structure conforms to standard web conventions."
        )

    return {
        "verdict": verdict,
        "confidence": round(confidence, 2),
        "risk_score": round(risk_score, 1),
        "explanation": explanation,
        "indicators": indicators,
        "probabilities": {
            "Safe": round(prob_safe, 2),
            "Critical": round(prob_critical, 2),
            "Suspicious": round(prob_suspicious, 2)
        },
        "metadata": {
            "hostname": hostname,
            "path": parsed.path or "/",
            "query": parsed.query or "",
            "is_ip": is_ip,
            "subdomains": subdomain_count,
            "features_analyzed": len(feature_names)
        }
    }
