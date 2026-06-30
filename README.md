# eproc-notifier

Bot de lembretes de audiências do eProc/TJRS via Telegram.

Envia notificações automáticas nos marcos **D-7, D-3, D-1 e D-0** antes de cada audiência agendada.

---

## Passos obrigatórios antes de rodar

### 1. Pré-requisitos de sistema

- Python 3.11 ou superior
- Acesso à internet (para Supabase e Telegram)
- Conta no [Supabase](https://supabase.com) (plano gratuito é suficiente)
- Conta no Telegram

---

### 2. Configuração do Supabase

**a) Crie um projeto** em [supabase.com](https://supabase.com) → "New Project".

**b) Execute o SQL abaixo** no **SQL Editor** do painel Supabase:

```sql
CREATE TABLE audiencias (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  num_processo    TEXT NOT NULL,
  vara            TEXT,
  evento          TEXT,
  data_hora       TIMESTAMPTZ NOT NULL,
  previsao_fim    TIMESTAMPTZ,
  sala            TEXT,
  link_webconf    TEXT,
  partes          TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (num_processo, data_hora, evento)
);

CREATE TABLE notificacoes (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  audiencia_id  UUID REFERENCES audiencias(id) ON DELETE CASCADE,
  tipo          TEXT NOT NULL,
  canal         TEXT DEFAULT 'telegram',
  enviado_em    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (audiencia_id, tipo)
);

CREATE INDEX idx_audiencias_data ON audiencias (data_hora);
CREATE INDEX idx_notificacoes_audiencia ON notificacoes (audiencia_id);
```

**c) Copie as credenciais**: em **Project Settings → API**:
- `Project URL` → valor de `SUPABASE_URL`
- `anon public` key → valor de `SUPABASE_KEY`

---

### 3. Criação do bot no Telegram

**a) Crie o bot**:
1. Abra o Telegram e procure por **@BotFather**
2. Envie `/newbot` e siga as instruções
3. Ao final, o BotFather fornece o **token** → valor de `TELEGRAM_BOT_TOKEN`

**b) Obtenha seu chat_id**:
1. Procure pelo bot que você acabou de criar e inicie uma conversa (envie qualquer mensagem)
2. Acesse no browser: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
3. No JSON retornado, localize `"chat": {"id": 123456789}` → esse número é o `TELEGRAM_CHAT_ID`

---

### 4. Preenchimento do `.env`

```bash
cp .env.example .env
```

Abra `.env` e preencha com os valores obtidos nos passos anteriores:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-anon-key
TELEGRAM_BOT_TOKEN=000000000:AAAAAAAA...
TELEGRAM_CHAT_ID=123456789
USE_MOCK=true
SCHEDULER_HORA=08:00
```

---

### 5. Instalação de dependências

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# ou: .venv\Scripts\activate   # Windows

pip install -r requirements.txt
# Para desenvolvimento/testes:
pip install -r requirements-dev.txt
```

---

### 6. Rodar em modo imediato (para testar)

Executa um ciclo completo (sincroniza mock → banco → envia lembretes) e encerra:

```bash
python -m src.scheduler --run-now
```

> **Atenção**: o mock tem audiências agendadas para datas específicas. Para testar o envio de mensagens sem esperar a data correta, edite temporariamente `data/mock_audiencias.json` e ajuste `data_hora` para amanhã (`D-1`), hoje (`D-0`), etc.

---

### 7. Rodar o scheduler contínuo

Inicia o bot em modo contínuo — executa o ciclo diariamente no horário definido em `SCHEDULER_HORA`:

```bash
python -m src.scheduler
```

Para manter rodando em produção, use `nohup`, `screen`, ou um serviço systemd.

---

## Estrutura do projeto

```
eproc-notifier/
├── data/
│   └── mock_audiencias.json   # Audiências fictícias para Fase 1
├── src/
│   ├── config.py              # Lê e valida variáveis de ambiente
│   ├── db.py                  # Upsert e queries via Supabase
│   ├── loader.py              # Carrega mock JSON (Fase 1)
│   ├── notifier.py            # Motor de lembretes D-7/D-3/D-1/D-0
│   ├── bot.py                 # Envio de mensagens via Telegram
│   ├── scheduler.py           # Agendamento diário com APScheduler
│   └── scraper/               # Placeholder para o scraper da Fase 2
│       └── __init__.py
├── tests/
│   ├── test_notifier.py       # Testes das regras de lembrete
│   └── test_db.py             # Testes de integração com o banco
├── .env.example
├── .gitignore
├── requirements.txt
└── requirements-dev.txt
```

## Testes

```bash
# Apenas os testes unitários (sem conexão com o banco):
pytest tests/test_notifier.py -v

# Testes de integração (requerem .env configurado):
pytest tests/test_db.py -v
```

## Fase 2 — Scraper real

Para substituir o mock pelo scraper do eProc:
1. Implemente `src/scraper/` conforme a docstring em `src/scraper/__init__.py`
2. Defina `USE_MOCK=false` no `.env`
3. Nenhum outro arquivo precisa ser alterado
