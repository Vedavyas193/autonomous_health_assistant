import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional, Union

from diagnostic_context import context_sha256, verify_diagnostic_context


def _ensure_columns(cursor: sqlite3.Cursor, table: str, name: str, col_type: str) -> None:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = {row[1] for row in cursor.fetchall()}
    if name not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {name} {col_type}")


class RecordStorageAgent:
    def __init__(
        self,
        db_name: str = "patient_records.db",
        hmac_secret: Optional[bytes] = None,
    ):
        self.db_path = db_name
        self._hmac_secret = hmac_secret
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symptoms TEXT,
                predicted_disease TEXT,
                confidence REAL,
                risk_level TEXT,
                specialist TEXT,
                explanation TEXT
            )
            """
        )
        for name, ctype in [
            ("explanation_json", "TEXT"),
            ("audit_json", "TEXT"),
            ("context_hash", "TEXT"),
            ("hmac_signature", "TEXT"),
        ]:
            _ensure_columns(cursor, "records", name, ctype)
        conn.commit()
        conn.close()

    def save_record(
        self,
        symptoms: Union[str, List[str]],
        disease: str,
        confidence: float,
        risk_level: str,
        specialist: str,
        explanation_text: str,
        explanation_struct: Mapping[str, Any],
        audit_payload: Mapping[str, Any],
        signature_hex: str,
    ) -> bool:
        """Verifies HMAC on audit_payload before insert."""
        if self._hmac_secret is None:
            raise RuntimeError("HMAC secret not configured for RecordStorageAgent")
        if not verify_diagnostic_context(audit_payload, self._hmac_secret, signature_hex):
            print("HMAC verification failed — record not stored.")
            return False

        sym_str = ", ".join(symptoms) if isinstance(symptoms, list) else str(symptoms)
        expl_json = json.dumps(dict(explanation_struct), ensure_ascii=False)
        audit_json = json.dumps(dict(audit_payload), sort_keys=True, separators=(",", ":"))
        chash = context_sha256(audit_payload)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO records (
                    timestamp, symptoms, predicted_disease, confidence, risk_level,
                    specialist, explanation, explanation_json, audit_json, context_hash, hmac_signature
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    sym_str,
                    disease,
                    confidence,
                    risk_level,
                    specialist,
                    explanation_text,
                    expl_json,
                    audit_json,
                    chash,
                    signature_hex,
                ),
            )
            conn.commit()
            conn.close()
            print(f"Record stored with integrity hash {chash[:16]}...")
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
