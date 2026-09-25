import os
import joblib
import torch
from typing import Dict, Any, List
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, "training", "saved_models")

EMAIL_MODEL_PATH = os.path.join(MODELS_DIR, "email_model")
TEXT_MODEL_PATH = os.path.join(MODELS_DIR, "text_model")
URL_MODEL_PATH = os.path.join(MODELS_DIR, "url_model_new")


class ModelManager:
    _instance = None

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[ModelManager] Initializing on device: {self.device}")

        # Text Model
        self.text_tokenizer = None
        self.text_model = None

        # Email Model
        self.email_tokenizer = None
        self.email_model = None

        # URL Model
        self.url_rf_model = None
        self.url_encoder = None
        self.url_feature_names: List[str] = []

        self._load_all_models()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_all_models(self):
        self._load_text_model()
        self._load_email_model()
        self._load_url_model()

    def _load_text_model(self):
        try:
            print("[ModelManager] Loading Text Model (DistilBERT)...")
            self.text_tokenizer = DistilBertTokenizer.from_pretrained(
                TEXT_MODEL_PATH,
                local_files_only=True
            )
            self.text_model = DistilBertForSequenceClassification.from_pretrained(
                TEXT_MODEL_PATH,
                local_files_only=True
            )
            self.text_model.to(self.device)
            self.text_model.eval()
            print("[ModelManager] Text Model loaded successfully!")
        except Exception as e:
            print(f"[ModelManager] ERROR loading Text Model: {e}")

    def _load_email_model(self):
        try:
            print("[ModelManager] Loading Email Model (DistilBERT)...")
            self.email_tokenizer = DistilBertTokenizer.from_pretrained(
                EMAIL_MODEL_PATH,
                local_files_only=True
            )
            self.email_model = DistilBertForSequenceClassification.from_pretrained(
                EMAIL_MODEL_PATH,
                local_files_only=True
            )
            self.email_model.to(self.device)
            self.email_model.eval()
            print("[ModelManager] Email Model loaded successfully!")
        except Exception as e:
            print(f"[ModelManager] ERROR loading Email Model: {e}")

    def _load_url_model(self):
        try:
            print("[ModelManager] Loading URL Model (Random Forest)...")
            rf_file = os.path.join(URL_MODEL_PATH, "url_random_forest.pkl")
            enc_file = os.path.join(URL_MODEL_PATH, "label_mapping.pkl")
            feat_file = os.path.join(URL_MODEL_PATH, "feature_names.txt")

            if os.path.exists(rf_file):
                self.url_rf_model = joblib.load(rf_file)
            if os.path.exists(enc_file):
                self.url_encoder = joblib.load(enc_file)
            if os.path.exists(feat_file):
                with open(feat_file, "r", encoding="utf-8") as f:
                    self.url_feature_names = [line.strip() for line in f if line.strip()]

            print(f"[ModelManager] URL Model loaded with {len(self.url_feature_names)} features!")
        except Exception as e:
            print(f"[ModelManager] ERROR loading URL Model: {e}")

    def get_status(self) -> Dict[str, Any]:
        return {
            "device": str(self.device),
            "models": [
                {
                    "name": "Text Detection Engine",
                    "type": "DistilBERT Sequence Classification",
                    "status": "ONLINE" if self.text_model is not None else "OFFLINE",
                    "device": str(self.device),
                    "details": {
                        "architecture": "DistilBertForSequenceClassification",
                        "classes": ["Safe (0)", "Critical (1)"],
                        "max_length": 128
                    }
                },
                {
                    "name": "Email Phishing Engine",
                    "type": "DistilBERT Sequence Classification",
                    "status": "ONLINE" if self.email_model is not None else "OFFLINE",
                    "device": str(self.device),
                    "details": {
                        "architecture": "DistilBertForSequenceClassification",
                        "classes": ["Critical (0)", "Safe (1)"],
                        "max_length": 128
                    }
                },
                {
                    "name": "URL Threat Classifier",
                    "type": "Random Forest + Cyber Heuristic Engine",
                    "status": "ONLINE" if self.url_rf_model is not None else "OFFLINE",
                    "device": "CPU",
                    "details": {
                        "trees": 200,
                        "features": len(self.url_feature_names),
                        "classes": ["Safe (0)", "Critical (1)", "Suspicious (2)"]
                    }
                },
                {
                    "name": "Audio Deepfake / Scam Engine",
                    "type": "Acoustic Telemetry & Synthetic Artifact Analysis",
                    "status": "ONLINE",
                    "device": "CPU",
                    "details": {
                        "features": ["MFCC", "Spectral Centroid", "Flatness", "Pitch Variance"],
                        "detection": "Deepfake Voice / Robocall Scam"
                    }
                }
            ]
        }
