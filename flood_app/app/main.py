from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import load_config, AppConfig
from .services.monitor import MonitorService
from .api.routes import build_router


def create_app() -> FastAPI:
    cfg: AppConfig = load_config("config.yaml")
    config_holder = {"cfg": cfg}

    monitor = MonitorService(cfg)
    monitor.start()

    app = FastAPI(title="Flood Monitoring App", version="0.2")

    api_router = build_router(monitor, config_holder)
    app.include_router(api_router, prefix="/api")

    app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

    return app


app = create_app()
