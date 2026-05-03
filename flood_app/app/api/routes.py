from __future__ import annotations

from fastapi import APIRouter
from typing import Dict, Any

from ..config import AppConfig, deep_update


def build_router(monitor, config_holder):
    router = APIRouter()

    @router.get("/status")
    def get_status() -> Dict[str, Any]:
        return monitor.get_status()

    @router.get("/config")
    def get_config() -> Dict[str, Any]:
        return config_holder["cfg"].model_dump()

    @router.post("/config")
    def update_config(patch: Dict[str, Any]) -> Dict[str, Any]:
        raw = config_holder["cfg"].model_dump()
        merged = deep_update(raw, patch)
        cfg = AppConfig.model_validate(merged)
        config_holder["cfg"] = cfg
        monitor.update_config(cfg)
        return {"ok": True, "config": cfg.model_dump()}

    return router
