from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SensorDataSource(ABC):
    @abstractmethod
    def fetch_latest(self, limit: int = 10) -> List[Dict[str, Any]]:
        # Return latest sensor rows with keys: timestamp, distance_cm.
        raise NotImplementedError
