"""
Testes unitários para as regras de lembrete D-7, D-3, D-1, D-0.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from src.notifier import calcular_tipo_lembrete

BRASILIA = ZoneInfo("America/Sao_Paulo")


def _audiencia_em(dias: int) -> datetime:
    """Cria um datetime N dias no futuro a partir de agora (fuso Brasília)."""
    return datetime.now(BRASILIA) + timedelta(days=dias)


@pytest.mark.parametrize(
    "dias, esperado",
    [
        (7, "D-7"),
        (3, "D-3"),
        (1, "D-1"),
        (0, "D-0"),
    ],
)
def test_tipo_lembrete_correto(dias: int, esperado: str) -> None:
    data = _audiencia_em(dias)
    assert calcular_tipo_lembrete(data) == esperado


@pytest.mark.parametrize("dias", [2, 4, 5, 6, 8, 10, 30])
def test_sem_lembrete_em_dias_fora_do_ciclo(dias: int) -> None:
    data = _audiencia_em(dias)
    assert calcular_tipo_lembrete(data) is None


def test_audiencia_passada_retorna_none() -> None:
    data = _audiencia_em(-1)
    assert calcular_tipo_lembrete(data) is None


def test_naive_datetime_tratado_como_brasilia() -> None:
    """Datetime sem timezone deve ser interpretado como America/Sao_Paulo."""
    agora_local = datetime.now(BRASILIA)
    data_naive = (agora_local + timedelta(days=7)).replace(tzinfo=None)
    assert calcular_tipo_lembrete(data_naive) == "D-7"
