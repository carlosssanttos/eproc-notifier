"""
Testes de integração para upsert e deduplicação no banco Supabase.

ATENÇÃO: estes testes fazem chamadas reais ao Supabase.
Requerem variáveis SUPABASE_URL e SUPABASE_KEY configuradas no .env.
Execute com: pytest tests/test_db.py -v
"""

import uuid
from datetime import datetime, timezone

import pytest

from src import db

_PROCESSO_TESTE = f"TEST-{uuid.uuid4().hex[:8].upper()}"
_DATA_TESTE = "2099-12-31T23:59:00+00:00"
_EVENTO_TESTE = "Audiência de teste automatizado"

_AUDIENCIA_BASE = {
    "num_processo": _PROCESSO_TESTE,
    "vara": "Vara de Testes Automatizados",
    "evento": _EVENTO_TESTE,
    "data_hora": _DATA_TESTE,
    "previsao_fim": "2099-12-31T23:59:00+00:00",
    "sala": "Sala de Testes",
    "link_webconf": None,
    "partes": "SISTEMA (Autor) x TESTE (Réu)",
}


@pytest.fixture(scope="module")
def audiencia_id() -> str:
    """Insere a audiência de teste e retorna o UUID gerado."""
    return db.upsert_audiencia(_AUDIENCIA_BASE)


def test_upsert_retorna_uuid(audiencia_id: str) -> None:
    assert isinstance(audiencia_id, str)
    assert len(audiencia_id) == 36  # formato UUID


def test_upsert_deduplicacao(audiencia_id: str) -> None:
    """Segunda inserção do mesmo registro deve retornar o mesmo UUID."""
    id_repetido = db.upsert_audiencia(_AUDIENCIA_BASE)
    assert id_repetido == audiencia_id


def test_ja_notificado_falso(audiencia_id: str) -> None:
    assert db.ja_notificado(audiencia_id, "D-7") is False


def test_registrar_e_verificar_notificacao(audiencia_id: str) -> None:
    db.registrar_notificacao(audiencia_id, "D-7")
    assert db.ja_notificado(audiencia_id, "D-7") is True


def test_outros_tipos_nao_afetados(audiencia_id: str) -> None:
    """Registrar D-7 não deve marcar D-3, D-1 ou D-0 como notificados."""
    assert db.ja_notificado(audiencia_id, "D-3") is False
    assert db.ja_notificado(audiencia_id, "D-1") is False
    assert db.ja_notificado(audiencia_id, "D-0") is False
