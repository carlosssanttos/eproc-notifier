"""
Camada de acesso ao banco de dados via Supabase.
Todos os upserts e queries passam por este módulo.
"""

import logging
from datetime import datetime, timezone, timedelta

from supabase import create_client, Client

from src import config

logger = logging.getLogger(__name__)

_client: Client | None = None


def get_client() -> Client:
    """Retorna o client Supabase, inicializando-o na primeira chamada."""
    global _client
    if _client is None:
        _client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    return _client


def upsert_audiencia(audiencia: dict) -> str:
    """
    Insere uma audiência ou ignora se já existir (deduplicação por num_processo + data_hora + evento).

    Args:
        audiencia: Dicionário com os campos da audiência conforme o schema da tabela.

    Returns:
        UUID da audiência inserida ou existente.
    """
    client = get_client()
    response = (
        client.table("audiencias")
        .upsert(audiencia, on_conflict="num_processo,data_hora,evento", ignore_duplicates=True)
        .execute()
    )

    if response.data:
        return response.data[0]["id"]

    # Se foi ignorada por conflito, busca o registro existente
    existing = (
        client.table("audiencias")
        .select("id")
        .eq("num_processo", audiencia["num_processo"])
        .eq("data_hora", audiencia["data_hora"])
        .eq("evento", audiencia["evento"])
        .single()
        .execute()
    )
    return existing.data["id"]


def get_audiencias_proximas(dias: int) -> list[dict]:
    """
    Retorna audiências agendadas dentro dos próximos N dias.

    Args:
        dias: Número de dias a partir de hoje para buscar audiências.

    Returns:
        Lista de dicionários com os dados das audiências.
    """
    client = get_client()
    agora = datetime.now(timezone.utc)
    limite = agora + timedelta(days=dias)

    response = (
        client.table("audiencias")
        .select("*")
        .gte("data_hora", agora.isoformat())
        .lte("data_hora", limite.isoformat())
        .order("data_hora")
        .execute()
    )
    return response.data or []


def ja_notificado(audiencia_id: str, tipo: str) -> bool:
    """
    Verifica se já foi enviada uma notificação do tipo especificado para a audiência.

    Args:
        audiencia_id: UUID da audiência.
        tipo: Tipo do lembrete ('D-7', 'D-3', 'D-1', 'D-0').

    Returns:
        True se já foi notificado, False caso contrário.
    """
    client = get_client()
    response = (
        client.table("notificacoes")
        .select("id")
        .eq("audiencia_id", audiencia_id)
        .eq("tipo", tipo)
        .execute()
    )
    return len(response.data) > 0


def registrar_notificacao(audiencia_id: str, tipo: str) -> None:
    """
    Registra que uma notificação foi enviada para evitar reenvios.

    Args:
        audiencia_id: UUID da audiência.
        tipo: Tipo do lembrete ('D-7', 'D-3', 'D-1', 'D-0').
    """
    client = get_client()
    client.table("notificacoes").insert(
        {"audiencia_id": audiencia_id, "tipo": tipo, "canal": "telegram"}
    ).execute()
