# FASE 1: fonte mock. Na Fase 2, substituir pelo scraper em src/scraper/
"""
Carrega audiências a partir do arquivo mock JSON.
Na Fase 2, este módulo é substituído pelo scraper real em src/scraper/,
que deve exportar a mesma interface: carregar_audiencias() -> list[dict].
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_MOCK_PATH = Path(__file__).parent.parent / "data" / "mock_audiencias.json"


def carregar_audiencias() -> list[dict]:
    """
    Lê o arquivo mock e retorna a lista de audiências.

    Returns:
        Lista de dicionários com os dados das audiências no mesmo formato
        que o scraper da Fase 2 irá retornar.
    """
    logger.info("Carregando audiências do mock: %s", _MOCK_PATH)
    with open(_MOCK_PATH, encoding="utf-8") as f:
        audiencias = json.load(f)
    logger.info("%d audiências carregadas do mock.", len(audiencias))
    return audiencias
