"""
Envio de mensagens via Telegram usando python-telegram-bot v20+.
"""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Bot
from telegram.constants import ParseMode

from src import config

logger = logging.getLogger(__name__)

FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")

_TITULOS = {
    "D-7": "Lembrete D\\-7 — Audiência em 7 dias",
    "D-3": "Lembrete D\\-3 — Audiência em 3 dias",
    "D-1": "Lembrete D\\-1 — Audiência amanhã",
    "D-0": "Lembrete D\\-0 — Audiência HOJE",
}


def _escapar(texto: str) -> str:
    """Escapa caracteres especiais do MarkdownV2 do Telegram."""
    caracteres = r"\_*[]()~`>#+-=|{}.!"
    for c in caracteres:
        texto = texto.replace(c, f"\\{c}")
    return texto


def _formatar_mensagem(audiencia: dict, tipo: str) -> str:
    """
    Monta o texto da mensagem de lembrete no formato MarkdownV2.

    Args:
        audiencia: Dicionário com os dados da audiência.
        tipo: Tipo do lembrete ('D-7', 'D-3', 'D-1', 'D-0').

    Returns:
        String formatada para envio via Telegram.
    """
    data_hora = datetime.fromisoformat(audiencia["data_hora"])
    if data_hora.tzinfo is None:
        data_hora = data_hora.replace(tzinfo=FUSO_BRASILIA)
    data_hora = data_hora.astimezone(FUSO_BRASILIA)

    data_str = _escapar(data_hora.strftime("%d/%m/%Y às %Hh%M"))

    previsao_fim = audiencia.get("previsao_fim")
    if previsao_fim:
        fim_dt = datetime.fromisoformat(previsao_fim)
        if fim_dt.tzinfo is None:
            fim_dt = fim_dt.replace(tzinfo=FUSO_BRASILIA)
        fim_str = _escapar(fim_dt.astimezone(FUSO_BRASILIA).strftime("%Hh%M"))
        linha_fim = f"⏱ *Previsão de término:* {fim_str}\n"
    else:
        linha_fim = ""

    link_webconf = audiencia.get("link_webconf")
    linha_link = (
        f"🔗 *Webconferência:* {_escapar(link_webconf)}\n" if link_webconf else ""
    )

    titulo = _TITULOS.get(tipo, f"Lembrete {tipo}")
    processo = _escapar(audiencia.get("num_processo", ""))
    vara = _escapar(audiencia.get("vara", ""))
    evento = _escapar(audiencia.get("evento", ""))
    sala = _escapar(audiencia.get("sala", ""))
    partes = _escapar(audiencia.get("partes", ""))

    return (
        f"🔔 *{titulo}*\n\n"
        f"📋 *Processo:* {processo}\n"
        f"🏛 *Vara:* {vara}\n"
        f"⚖️ *Evento:* {evento}\n"
        f"📅 *Data/hora:* {data_str}\n"
        f"{linha_fim}"
        f"📍 *Sala:* {sala}\n"
        f"👥 *Partes:* {partes}\n"
        f"{linha_link}"
    )


async def enviar_lembrete(audiencia: dict, tipo: str) -> None:
    """
    Envia uma mensagem de lembrete para o chat configurado no .env.

    Args:
        audiencia: Dicionário com os dados da audiência.
        tipo: Tipo do lembrete ('D-7', 'D-3', 'D-1', 'D-0').
    """
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    mensagem = _formatar_mensagem(audiencia, tipo)
    try:
        await bot.send_message(
            chat_id=config.TELEGRAM_CHAT_ID,
            text=mensagem,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        logger.info(
            "Mensagem %s enviada para o chat %s.", tipo, config.TELEGRAM_CHAT_ID
        )
    except Exception:
        logger.exception(
            "Falha ao enviar mensagem Telegram para audiência %s.",
            audiencia.get("num_processo", "desconhecido"),
        )
        raise
