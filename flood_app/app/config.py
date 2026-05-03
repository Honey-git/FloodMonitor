from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any
import yaml
from pathlib import Path


class CSVConfig(BaseModel):
    path: str = "data/sample_readings.csv"


class DataSourceConfig(BaseModel):
    type: Literal["csv", "sheets"] = "csv"
    csv: CSVConfig = Field(default_factory=CSVConfig)


class ThresholdConfig(BaseModel):
    warning_cm: Optional[float] = None
    danger_cm: Optional[float] = None


class RiseRateConfig(BaseModel):
    medium_cm_per_min: float = 1.0
    high_cm_per_min: float = 2.0


class PollingConfig(BaseModel):
    interval_seconds: int = 5
    lookback_points: int = 120


class SystemConfig(BaseModel):
    sensor_height_cm: float = 120.0
    drain_height_cm: float = 100.0


class TimestampConfig(BaseModel):
    # elapsed_ms = milliseconds since logging started
    format: Literal["auto", "elapsed_ms", "epoch_ms", "epoch_s", "iso"] = "elapsed_ms"
    base_date: Literal["today"] = "today"


class AppConfig(BaseModel):
    data_source: DataSourceConfig = Field(default_factory=DataSourceConfig)
    system: SystemConfig = Field(default_factory=SystemConfig)
    thresholds: ThresholdConfig = Field(default_factory=ThresholdConfig)
    rise_rate: RiseRateConfig = Field(default_factory=RiseRateConfig)
    polling: PollingConfig = Field(default_factory=PollingConfig)
    timestamp: TimestampConfig = Field(default_factory=TimestampConfig)


def load_config(path: str = "config.yaml") -> AppConfig:
    p = Path(path)
    if not p.exists():
        return AppConfig()
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return AppConfig.model_validate(raw)


def deep_update(base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    # Recursively merge patch dict into base dict.
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k] = deep_update(base[k], v)
        else:
            base[k] = v
    return base
