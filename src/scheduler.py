"""
Agendador de tarefas: executa o ciclo de notificações diariamente via APScheduler.
Também suporta execução imediata via flag --run-now para testes.
"""

import argparse
import logging
import sys

from apscheduler.schedulers.blocking import BlockingScheduler

from src import config, db, loader, notifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def sincronizar_e_notificar() -> None:
    """
    Tarefa principal agendada:
    1. Carrega audiências da fonte configurada (mock ou scraper).
    2. Faz upsert de cada uma no banco.
    3. Roda o motor de notificações.
    """
    logger.info("=== Iniciando ciclo do pauta-bot ===")

    if config.USE_MOCK:
        audiencias = loader.carregar_audiencias()
    else:
        # Fase 2: importar e usar o scraper real
        from src.scraper import carregar_audiencias  # type: ignore[import]
        audiencias = carregar_audiencias()

    logger.info("Sincronizando %d audiências com o banco...", len(audiencias))
    for audiencia in audiencias:
        try:
            db.upsert_audiencia(audiencia)
        except Exception:
            logger.exception(
                "Erro ao fazer upsert da audiência %s.",
                audiencia.get("num_processo", "desconhecido"),
            )

    verificadas, enviadas = notifier.processar_audiencias()
    logger.info(
        "=== Ciclo finalizado. Verificadas: %d | Enviadas: %d ===",
        verificadas,
        enviadas,
    )


def main() -> None:
    """Ponto de entrada: modo imediato (--run-now) ou scheduler contínuo."""
    parser = argparse.ArgumentParser(description="pauta-bot — notificador de audiências")
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Executa o ciclo imediatamente e encerra (útil para testes).",
    )
    args = parser.parse_args()

    if args.run_now:
        logger.info("Modo --run-now ativado. Executando ciclo único.")
        sincronizar_e_notificar()
        sys.exit(0)

    hora, minuto = config.SCHEDULER_HORA.split(":")
    logger.info(
        "Scheduler iniciado. Ciclo diário às %s (America/Sao_Paulo).",
        config.SCHEDULER_HORA,
    )

    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(
        sincronizar_e_notificar,
        trigger="cron",
        hour=int(hora),
        minute=int(minuto),
        id="ciclo_diario",
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler encerrado pelo usuário.")


if __name__ == "__main__":
    main()
