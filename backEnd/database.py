import os
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    DateTime,
    Text,
    Integer,
    desc
)
from sqlalchemy.orm import declarative_base, sessionmaker

# Database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "sentrix.db")
DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ScanRecord(Base):
    __tablename__ = "scan_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String(32), unique=True, index=True)
    input_type = Column(String(20), index=True)  # text, email, url, file, audio
    input_summary = Column(Text)
    raw_input = Column(Text, nullable=True)
    verdict = Column(String(20), index=True)  # SAFE, SUSPICIOUS, FRAUDULENT
    confidence = Column(Float)  # 0.0 to 100.0
    risk_score = Column(Float)  # 0.0 to 100.0
    explanation = Column(Text)
    indicators_json = Column(Text, default="[]")
    probabilities_json = Column(Text, default="{}")
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self) -> Dict[str, Any]:
        try:
            indicators = json.loads(self.indicators_json) if self.indicators_json else []
        except Exception:
            indicators = []

        try:
            probabilities = json.loads(self.probabilities_json) if self.probabilities_json else {}
        except Exception:
            probabilities = {}

        try:
            meta = json.loads(self.metadata_json) if self.metadata_json else {}
        except Exception:
            meta = {}

        return {
            "id": self.id,
            "scan_id": self.scan_id,
            "input_type": self.input_type,
            "input_summary": self.input_summary,
            "raw_input": self.raw_input,
            "verdict": self.verdict,
            "confidence": round(self.confidence, 2) if self.confidence is not None else 0.0,
            "risk_score": round(self.risk_score, 1) if self.risk_score is not None else 0.0,
            "explanation": self.explanation,
            "indicators": indicators,
            "probabilities": probabilities,
            "metadata": meta,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# Initialize tables
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_scan(
    input_type: str,
    input_summary: str,
    verdict: str,
    confidence: float,
    risk_score: float,
    explanation: str,
    indicators: List[str],
    probabilities: Dict[str, float],
    raw_input: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        # Generate friendly scan id: SCN-YYYYMMDD-XXXX
        now = datetime.utcnow()
        short_id = uuid.uuid4().hex[:6].upper()
        scan_id = f"SCN-{now.strftime('%Y%m%d')}-{short_id}"

        record = ScanRecord(
            scan_id=scan_id,
            input_type=input_type.lower(),
            input_summary=input_summary[:300] if input_summary else "",
            raw_input=raw_input[:2000] if raw_input else None,
            verdict=verdict.upper(),
            confidence=float(confidence),
            risk_score=float(risk_score),
            explanation=explanation,
            indicators_json=json.dumps(indicators or []),
            probabilities_json=json.dumps(probabilities or {}),
            metadata_json=json.dumps(metadata or {}),
            created_at=now
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.to_dict()
    finally:
        db.close()


def get_history(
    limit: int = 50,
    offset: int = 0,
    input_type: Optional[str] = None,
    verdict: Optional[str] = None,
    search: Optional[str] = None
) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        query = db.query(ScanRecord)
        if input_type:
            query = query.filter(ScanRecord.input_type == input_type.lower())
        if verdict:
            query = query.filter(ScanRecord.verdict == verdict.upper())
        if search:
            query = query.filter(
                (ScanRecord.scan_id.ilike(f"%{search}%")) |
                (ScanRecord.input_summary.ilike(f"%{search}%")) |
                (ScanRecord.explanation.ilike(f"%{search}%"))
            )

        total = query.count()
        records = (
            query.order_by(desc(ScanRecord.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [r.to_dict() for r in records]
        }
    finally:
        db.close()


def get_scan_by_id(scan_id: str) -> Optional[Dict[str, Any]]:
    db = SessionLocal()
    try:
        record = (
            db.query(ScanRecord)
            .filter((ScanRecord.scan_id == scan_id) | (ScanRecord.id == scan_id))
            .first()
        )
        return record.to_dict() if record else None
    finally:
        db.close()


def delete_scan(scan_id: str) -> bool:
    db = SessionLocal()
    try:
        record = (
            db.query(ScanRecord)
            .filter((ScanRecord.scan_id == scan_id) | (ScanRecord.id == scan_id))
            .first()
        )
        if record:
            db.delete(record)
            db.commit()
            return True
        return False
    finally:
        db.close()


def clear_history() -> int:
    db = SessionLocal()
    try:
        count = db.query(ScanRecord).delete()
        db.commit()
        return count
    finally:
        db.close()


def get_dashboard_stats() -> Dict[str, Any]:
    db = SessionLocal()
    try:
        total = db.query(ScanRecord).count()
        safe_count = db.query(ScanRecord).filter(ScanRecord.verdict == "SAFE").count()
        suspicious_count = db.query(ScanRecord).filter(ScanRecord.verdict == "SUSPICIOUS").count()
        fraud_count = db.query(ScanRecord).filter(ScanRecord.verdict == "FRAUDULENT").count()

        type_counts = {
            "text": db.query(ScanRecord).filter(ScanRecord.input_type == "text").count(),
            "email": db.query(ScanRecord).filter(ScanRecord.input_type == "email").count(),
            "url": db.query(ScanRecord).filter(ScanRecord.input_type == "url").count(),
            "file": db.query(ScanRecord).filter(ScanRecord.input_type == "file").count(),
            "audio": db.query(ScanRecord).filter(ScanRecord.input_type == "audio").count(),
        }

        # Calculate average confidence
        all_records = db.query(ScanRecord.confidence).all()
        avg_conf = (
            round(sum(r[0] for r in all_records if r[0] is not None) / len(all_records), 1)
            if all_records
            else 0.0
        )

        recent = (
            db.query(ScanRecord)
            .order_by(desc(ScanRecord.created_at))
            .limit(5)
            .all()
        )

        return {
            "total_scans": total,
            "verdicts": {
                "safe": safe_count,
                "suspicious": suspicious_count,
                "fraudulent": fraud_count
            },
            "type_counts": type_counts,
            "average_confidence": avg_conf,
            "threats_blocked": fraud_count + suspicious_count,
            "recent_scans": [r.to_dict() for r in recent]
        }
    finally:
        db.close()
