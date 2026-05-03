from __future__ import annotations

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta, date


def _base_datetime(base_date: str) -> datetime:
    d = date.today()
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)


def parse_timestamp(ts: Any, fmt: str = "auto", base_date: str = "today") -> Optional[datetime]:
    if ts is None:
        return None

    if fmt == "elapsed_ms":
        try:
            ms = int(str(ts).strip())
            return _base_datetime(base_date) + timedelta(milliseconds=ms)
        except Exception:
            return None

    try:
        n = int(str(ts).strip())
        if fmt == "auto":
            if len(str(abs(n))) >= 13:
                return datetime.fromtimestamp(n / 1000.0, tz=timezone.utc)
            if len(str(abs(n))) == 10:
                return datetime.fromtimestamp(n, tz=timezone.utc)
            if 0 <= n <= 100_000_000:
                return _base_datetime(base_date) + timedelta(milliseconds=n)
            return datetime.fromtimestamp(n, tz=timezone.utc)
        if fmt == "epoch_ms":
            return datetime.fromtimestamp(n / 1000.0, tz=timezone.utc)
        if fmt == "epoch_s":
            return datetime.fromtimestamp(n, tz=timezone.utc)
    except Exception:
        pass

    try:
        s = str(ts).strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def water_level_cm(sensor_height_cm: float, distance_cm: float) -> float:
    return sensor_height_cm - distance_cm


def compute_rise_rate_cm_per_min(points: List[Tuple[datetime, float]]) -> Optional[float]:
    if len(points) < 2:
        return None
    (t1, l1), (t2, l2) = points[-2], points[-1]
    dt_min = (t2 - t1).total_seconds() / 60.0
    if dt_min <= 0:
        return None
    return (l2 - l1) / dt_min


def compute_metrics(
    rows: List[Dict[str, Any]],
    sensor_height_cm: float,
    timestamp_format: str = "auto",
    base_date: str = "today",
) -> Dict[str, Any]:
    parsed: List[Tuple[datetime, float, float]] = []

    for r in rows:
        dt = parse_timestamp(r.get("timestamp"), fmt=timestamp_format, base_date=base_date)
        dist = r.get("distance_cm")
        if dt is None or dist is None:
            continue
        try:
            dist_f = float(dist)
            lvl = water_level_cm(sensor_height_cm, dist_f)
        except Exception:
            continue
        parsed.append((dt, dist_f, lvl))

    parsed.sort(key=lambda x: x[0])
    if not parsed:
        return {"current_water_level_cm": None, "rise_rate_cm_per_min": None, "series": []}

    series = [{"t_iso": dt.isoformat(), "distance_cm": dist, "water_level_cm": lvl} for (dt, dist, lvl) in parsed]

    current_level = parsed[-1][2]
    rise_rate = compute_rise_rate_cm_per_min([(dt, lvl) for (dt, _, lvl) in parsed])

    return {"current_water_level_cm": current_level, "rise_rate_cm_per_min": rise_rate, "series": series}
