"""
Motor de lembretes: decide quais audiências precisam de notificação hoje
e orquestra o envio via bot Telegram.
"""

import asyncio
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from src import db, bot

logger = logging.getLogger(__name__)

FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")
TIPOS_LEMBRETE = {7: "D-7", 3: "D-3", 1: "D-1", 0: "D-0"}


def calcular_tipo_lembrete(data_hora: datetime) -> str | None:
    """
    Determina se hoje é dia de enviar lembrete para uma audiência.

    Compara a data local (America/Sao_Paulo) da audiência com hoje.
    Retorna o tipo de lembrete correspondente ou None se não for dia de lembrete.

    Args:
        data_hora: Data e hora da audiência (timezone-aware ou naive tratado como Brasília).

    Returns:
        'D-7', 'D-3', 'D-1', 'D-0' ou None.
    """
    if data_hora.tzinfo is None:
        data_hora = data_hora.replace(tzinfo=FUSO_BRASILIA)

    hoje = datetime.now(FUSO_BRASILIA).date()
    data_audiencia = data_hora.astimezone(FUSO_BRASILIA).date()
    delta = (data_audiencia - hoje).days

    return TIPOS_LEMBRETE.get(delta)


def processar_audiencias() -> tuple[int, int]:
    """
    Ciclo principal de notificação:
    1. Busca audiências dos próximos 8 dias no banco.
    2. Para cada uma, verifica se hoje é dia de lembrete.
    3. Filtra as que já foram notificadas no tipo correto.
    4. Envia o lembrete via Telegram e registra no banco.

    Returns:
        Tupla (total_verificadas, total_enviadas).
    """
    audiencias = db.get_audiencias_proximas(dias=8)
    total_verificadas = len(audiencias)
    total_enviadas = 0

    logger.info("Verificando %d audiências próximas.", total_verificadas)

    for audiencia in audiencias:
        try:
            data_hora = datetime.fromisoformat(audiencia["data_hora"])
            tipo = calcular_tipo_lembrete(data_hora)

            if tipo is None:
                continue

            audiencia_id = audiencia["id"]

            if db.ja_notificado(audiencia_id, tipo):
                logger.debug(
                    "Audiência %s já notificada como %s. Pulando.",
                    audiencia["num_processo"],
                    tipo,
                )
                continue

            asyncio.run(bot.enviar_lembrete(audiencia, tipo))
            db.registrar_notificacao(audiencia_id, tipo)
            total_enviadas += 1
            logger.info(
                "Lembrete %s enviado: processo %s.", tipo, audiencia["num_processo"]
            )

        except Exception:
            logger.exception(
                "Erro ao processar audiência %s. Continuando.",
                audiencia.get("num_processo", "desconhecido"),
            )

    logger.info(
        "Ciclo concluído. Verificadas: %d | Enviadas: %d",
        total_verificadas,
        total_enviadas,
    )
    return total_verificadas, total_enviadas
