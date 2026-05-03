from __future__ import annotations

import csv
from typing import List, Dict, Any, Optional
from pathlib import Path

from .base import SensorDataSource


def _norm_key(k: str) -> str:
    return "".join(ch.lower() for ch in k.strip() if ch.isalnum() or ch == "_")


def _pick(row: Dict[str, Any], candidates: List[str]) -> Optional[Any]:
    norm_map = {_norm_key(k): k for k in row.keys()}
    for c in candidates:
        ck = _norm_key(c)
        if ck in norm_map:
            return row.get(norm_map[ck])
    return None


def _sniff_dialect(sample: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(sample, delimiters=[",", "	", ";", "|"])
    except Exception:
        return csv.excel


class CSVSensorSource(SensorDataSource):
    def __init__(self, path: str):
        self.path = Path(path)

    def fetch_latest(self, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []



        text = self.path.read_text(encoding="utf-8", errors="ignore")
        sample = "\n".join(text.splitlines()[:20])
        dialect = _sniff_dialect(sample)

        with self.path.open("r", newline="", encoding="utf-8", errors="ignore") as f:
            rows = list(csv.DictReader(f, dialect=dialect))

        latest = rows[-limit:] if limit > 0 else rows
        out: List[Dict[str, Any]] = []
        for r in latest:
            ts = _pick(r, ["timestamp", "Timestamp", "Timestamp_MS", "timestamp_ms", "time_ms"])
            dist = _pick(r, ["distance_cm", "Distance_CM", "distance", "Distance"])
            if ts is None or dist is None:
                continue
            try:
                out.append({
                    "timestamp": str(ts).strip(),
                    "distance_cm": float(str(dist).strip()),
                })
            except Exception:
                continue
        return out
