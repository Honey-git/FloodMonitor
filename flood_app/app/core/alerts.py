from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal

from .thresholds import Thresholds

AlertLevel = Literal["HIGH", "MEDIUM", "LOW", "NO_ALERT"]


@dataclass(frozen=True)
class AlertResult:
    level: AlertLevel
    reason: str


def classify_level(water_level_cm: float, thresholds: Thresholds) -> AlertLevel:
    if water_level_cm >= thresholds.danger_cm:
        return "HIGH"
    if water_level_cm >= thresholds.warning_cm:
        return "MEDIUM"
    if water_level_cm >= thresholds.warning_cm * 0.85:
        return "LOW"
    return "NO_ALERT"


def apply_alert_rules(
    water_level_cm: Optional[float],
    rise_rate_cm_per_min: Optional[float],
    thresholds: Thresholds,
    rise_rate_medium: float,
    rise_rate_high: float,
) -> AlertResult:
    if water_level_cm is None:
        return AlertResult(level="NO_ALERT", reason="No valid sensor readings available.")

    base = classify_level(water_level_cm, thresholds)

    if base == "HIGH":
        reason = f"Water level {water_level_cm:.1f}cm is at/above danger threshold {thresholds.danger_cm:.1f}cm."
    elif base == "MEDIUM":
        reason = f"Water level {water_level_cm:.1f}cm is at/above warning threshold {thresholds.warning_cm:.1f}cm."
    elif base == "LOW":
        reason = f"Water level {water_level_cm:.1f}cm is approaching warning threshold {thresholds.warning_cm:.1f}cm."
    else:
        reason = f"Water level {water_level_cm:.1f}cm is below warning threshold {thresholds.warning_cm:.1f}cm."

    if rise_rate_cm_per_min is not None:
        if rise_rate_cm_per_min >= rise_rate_high and base in ("MEDIUM", "LOW", "NO_ALERT"):
            return AlertResult(
                level="HIGH",
                reason=reason + f" Rise rate is high ({rise_rate_cm_per_min:.2f} cm/min), escalating to HIGH.",
            )
        if rise_rate_cm_per_min >= rise_rate_medium and base in ("LOW", "NO_ALERT"):
            return AlertResult(
                level="MEDIUM",
                reason=reason + f" Rise rate is elevated ({rise_rate_cm_per_min:.2f} cm/min), escalating to MEDIUM.",
            )
        reason += f" Rise rate: {rise_rate_cm_per_min:.2f} cm/min."
    else:
        reason += " Rise rate: insufficient data."

    return AlertResult(level=base, reason=reason)
