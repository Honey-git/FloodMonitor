from __future__ import annotations

import threading
import time
from typing import Dict, Any

from ..config import AppConfig
from ..sources.csv_source import CSVSensorSource
from ..sources.base import SensorDataSource
from ..core.thresholds import compute_thresholds
from ..core.metrics import compute_metrics
from ..core.alerts import apply_alert_rules


class MonitorService:
    def __init__(self, cfg: AppConfig):
        self._lock = threading.Lock()
        self._cfg = cfg
        self._source = self._build_source(cfg)
        self._status: Dict[str, Any] = {"ok": False, "message": "Starting...", "data": {}}
        self._stop = False
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _build_source(self, cfg: AppConfig) -> SensorDataSource:
        if cfg.data_source.type == "csv":
            return CSVSensorSource(cfg.data_source.csv.path)
        raise ValueError(f"Unsupported data_source.type: {cfg.data_source.type}")

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop = True

    def update_config(self, cfg: AppConfig):
        with self._lock:
            self._cfg = cfg
            self._source = self._build_source(cfg)

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._status)

    def _run(self):
        while not self._stop:
            try:
                with self._lock:
                    cfg = self._cfg
                    source = self._source

                rows = source.fetch_latest(limit=cfg.polling.lookback_points)

                metrics = compute_metrics(
                    rows,
                    sensor_height_cm=cfg.system.sensor_height_cm,
                    timestamp_format=cfg.timestamp.format,
                    base_date=cfg.timestamp.base_date,
                )

                thresholds = compute_thresholds(
                    drain_height_cm=cfg.system.drain_height_cm,
                    warning_cm=cfg.thresholds.warning_cm,
                    danger_cm=cfg.thresholds.danger_cm,
                )

                alert = apply_alert_rules(
                    water_level_cm=metrics["current_water_level_cm"],
                    rise_rate_cm_per_min=metrics["rise_rate_cm_per_min"],
                    thresholds=thresholds,
                    rise_rate_medium=cfg.rise_rate.medium_cm_per_min,
                    rise_rate_high=cfg.rise_rate.high_cm_per_min,
                )

                payload = {
                    "ok": True,
                    "message": "OK",
                    "data": {
                        "current_water_level_cm": metrics["current_water_level_cm"],
                        "rise_rate_cm_per_min": metrics["rise_rate_cm_per_min"],
                        "series": metrics["series"],
                        "thresholds": {
                            "warning_cm": thresholds.warning_cm,
                            "danger_cm": thresholds.danger_cm,
                        },
                        "alert": {"level": alert.level, "reason": alert.reason},
                        "system": {
                            "sensor_height_cm": cfg.system.sensor_height_cm,
                            "drain_height_cm": cfg.system.drain_height_cm,
                        },
                    },
                }

                with self._lock:
                    self._status = payload

            except Exception as e:
                with self._lock:
                    self._status = {"ok": False, "message": str(e), "data": {}}

            time.sleep(max(1, self._cfg.polling.interval_seconds))
