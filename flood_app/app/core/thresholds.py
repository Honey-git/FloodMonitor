from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Thresholds:
    warning_cm: float
    danger_cm: float


def compute_thresholds(
    drain_height_cm: float,
    warning_cm: Optional[float] = None,
    danger_cm: Optional[float] = None,
    warning_pct: float = 0.70,
    danger_pct: float = 0.95,
) -> Thresholds:
    w = warning_cm if warning_cm is not None else drain_height_cm * warning_pct
    d = danger_cm if danger_cm is not None else drain_height_cm * danger_pct
    if d < w:
        d = w
    return Thresholds(warning_cm=w, danger_cm=d)
