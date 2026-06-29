"""
Carrega e valida as variáveis de ambiente do projeto.
Todas as configurações do sistema são expostas como constantes tipadas a partir deste módulo.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _require(var: str) -> str:
    """Lê uma variável de ambiente obrigatória ou lança ValueError."""
    value = os.getenv(var)
    if not value:
        raise ValueError(
            f"Variável de ambiente obrigatória ausente: {var}. "
            f"Verifique o arquivo .env (consulte .env.example)."
        )
    return value


SUPABASE_URL: str = _require("SUPABASE_URL")
SUPABASE_KEY: str = _require("SUPABASE_KEY")
TELEGRAM_BOT_TOKEN: str = _require("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID: str = _require("TELEGRAM_CHAT_ID")

USE_MOCK: bool = os.getenv("USE_MOCK", "true").lower() == "true"

SCHEDULER_HORA: str = os.getenv("SCHEDULER_HORA", "08:00")
