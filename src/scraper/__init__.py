"""
Placeholder para o scraper da Fase 2.

Este pacote deve implementar a extração automática de audiências a partir
do sistema eProc do TJRS usando Playwright para automação do browser.

Interface obrigatória
---------------------
O módulo principal deste pacote deve exportar a função:

    def carregar_audiencias() -> list[dict]:
        ...

O dicionário retornado por audiência deve conter exatamente as mesmas chaves
que o mock em data/mock_audiencias.json:

    {
        "num_processo": str,
        "vara":         str,
        "evento":       str,
        "data_hora":    str,  # ISO 8601, ex: "2026-07-10T14:10:00"
        "previsao_fim": str | None,
        "sala":         str | None,
        "link_webconf": str | None,
        "partes":       str | None,
    }

Para alternar entre mock e scraper, defina USE_MOCK=false no arquivo .env.
O scheduler.py já está preparado para importar carregar_audiencias() deste pacote
quando USE_MOCK for False.

Dependências da Fase 2
----------------------
Adicionar ao requirements.txt:
    playwright>=1.40.0
    beautifulsoup4>=4.12.0

Executar após instalar:
    playwright install chromium
"""
