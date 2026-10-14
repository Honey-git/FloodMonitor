from __future__ import annotations

from fastapi import APIRouter
from typing import Dict, Any

from ..config import AppConfig, deep_update


# Cria as rotas da API para monitoramento e configuração do sistema
def build_router(monitor, config_holder):
    # Inicializa um roteador para organizar os endpoints da API
    router = APIRouter()

    # Rota GET para consultar o status atual do sistema
    @router.get("/status")
    def get_status() -> Dict[str, Any]:
        # Retorna as informações atuais do monitoramento
        return monitor.get_status()

    # Rota GET para consultar a configuração atual do sistema
    @router.get("/config")
    def get_config() -> Dict[str, Any]:
        # Retorna as configurações armazenadas no formato de dicionário
        return config_holder["cfg"].model_dump()

    # Rota POST para atualizar as configurações do sistema
    @router.post("/config")
    def update_config(patch: Dict[str, Any]) -> Dict[str, Any]:
        # Obtém as configurações atuais e as converte em um dicionário
        raw = config_holder["cfg"].model_dump()

        # Combina as configurações atuais com as novas alterações recebidas
        merged = deep_update(raw, patch)

        # Valida os dados atualizados e cria um novo objeto de configuração
        cfg = AppConfig.model_validate(merged)

        # Armazena a nova configuração no gerenciador de configurações
        config_holder["cfg"] = cfg

        # Atualiza o monitoramento com as novas configurações
        monitor.update_config(cfg)

        # Retorna uma confirmação e as configurações atualizadas
        return {"ok": True, "config": cfg.model_dump()}

    # Retorna o roteador com todas as rotas configuradas
    return router