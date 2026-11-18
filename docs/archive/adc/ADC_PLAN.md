> **Histórico, arquivado em 2026-11-17.** Origem: `ADC_PLAN.md`.
> Substituído por: docs/adr/ (decisões do ADC) e specs 011, 012, 013, 016, 017
> Conteúdo original abaixo, sem edição.

# ADC (Asset Data Collector) — Plano de Projeto

> **Status (2026-11-14):** banco (Fase 2) e **coletor Fundamentus (Fase 3)** implementados e validados contra o site e o PostgreSQL do Docker (89 testes). Importador MVP implementado; validação E2E com a planilha real (7.7) pendente. Fase 10 especificada, não iniciada.
> **Ordem revista em 2026-11-14:** a prioridade do usuário são os dados de valuation (indicadores, balanços, proventos), então a Fase 3 passou à frente da Fase 10. Ver D27–D30.
> **Origem:** reconstruído a partir das sessões de 04/10, 06/10 e 27/10/2026; arquitetura de coleta e API detalhada em 30/10/2026.
> **Não confundir com:** `SESSION_PLAN.md` / `PROMPT_NOVA_SESSAO.txt`, que são do MyWallet.
> **Próximo passo:** validar o importador com a planilha real (7.7, depende do usuário); depois a API FastAPI (Fase 6) expondo o que o coletor já grava, e então a Fase 10 (COTAHIST + `/v1/prices`).

## 1. Objetivo

Criar um projeto separado do MyWallet para:

1. **Curto prazo:** importar o histórico de uma carteira a partir de planilha `.xlsx`/`.csv` (abas **Compras** e **Vendas**) para o backend do Consolidator via API.
2. **Médio/longo prazo:** coletar e normalizar dados fundamentalistas de empresas brasileiras e expor esses dados ao Consolidator/Visualizer por uma API interna.
3. **Fonte principal:** Fundamentus, para dados cadastrais, indicadores, Balanço Patrimonial, DRE, proventos e resultados trimestrais.
4. **Exceção de fonte:** CVM, somente para a Demonstração de Fluxo de Caixa (DFC), usada para fluxo de caixa, capex e capital de giro.
5. **Limite de responsabilidade:** o ADC **não calcula valuation, DCF ou projeções**. Ele entrega dados brutos e agregações contábeis simples; o investidor faz o valuation no MyWallet.

O ADC existe para reduzir a dependência e o custo da Brapi, mantendo uma base própria, cacheada, normalizada e com proveniência.

## 2. Escopo

### Dentro do escopo agora (MVP)

- CLI de importação de planilha.
- Login no MyWallet via e-mail/senha.
- Leitura de `.xlsx` e `.csv`, com abas `Compras` e `Vendas`.
- Normalização de datas, números e tickers no padrão brasileiro.
- Resolução de `ticker -> assetId` por carteira.
- Criação de ativo ausente conforme D13.
- Envio cronológico de transações via `POST /transactions`.
- Modos `--dry-run`, `--validate-only` e `--import`.
- Testes de parser, normalização, mapper e validação.

### Dentro do escopo futuro aprovado

- Coletor Fundamentus:
  - identificação da empresa, ticker, tipo, setor e subsetor;
  - cotação, valor de mercado, valor da firma, número de ações e volume médio;
  - indicadores fundamentalistas;
  - Balanço Patrimonial (BP);
  - Demonstrativo de Resultados (DRE);
  - proventos;
  - resultados trimestrais.
- Coletor CVM DFC:
  - DFC-MI consolidada e individual;
  - fluxo de caixa operacional, de investimento e de financiamento;
  - capex e variações de capital de giro;
  - histórico desde 2010.
- Coletor de cotações históricas (Fase 10):
  - série diária de fechamento por ticker a partir do COTAHIST (B3);
  - fechamento bruto e ajustado por split/bonus/inplit;
  - backfill de 5 anos e atualização diária após o fechamento.
- Banco PostgreSQL próprio.
- API interna FastAPI, somente leitura.
- Agendamento, cache, rate limit, retry/backoff e observabilidade.
- Deploy local com Docker Compose.
- Agregações contábeis simples, sem projeções:
  - dívida líquida / patrimônio líquido;
  - margens;
  - dividend yield e payout;
  - `FCF = fluxo de caixa operacional - capex`, quando os dados existirem.

### Fora do escopo

- Ingestão completa de DFP/ITR da CVM.
- Fundamentos de agregadores além do Fundamentus (StatusInvest etc.). A B3 entra **somente** para cotações históricas (COTAHIST), não para fundamentos.
- Download automatizado do Excel de balanços do Fundamentus por causa do CAPTCHA.
- Cálculo de DCF, valuation, preço-teto ou projeções de lucro.
- Endpoint `POST /import/ledger` no backend do MyWallet.
- Qualquer escrita direta no banco do MyWallet.
- Interface visual própria; a visualização fica no Visualizer.
- Persistência de token em disco.

## 3. Decisões já tomadas

| # | Decisão | Justificativa |
|---|---|---|
| D1 | Nome do projeto: **ADC (Asset Data Collector)** | Diferencia de `Consolidator` e `Visualizer`. Repositório sugerido: `adc`. |
| D2 | Projeto separado do MyWallet | Isola complexidade de coleta, cache e análise. |
| D3 | Python como linguagem | Melhor ecossistema para ETL, planilhas e análise (pandas). Go descartado para este caso. |
| D4 | Integração **API-first** | Respeita o ledger, custo médio e regras de negócio do Consolidator. Nunca acessar o banco diretamente. |
| D5 | Nenhum script do ADC acessa o banco do MyWallet | Segurança e desacoplamento. |
| D6 | Login via CLI (e-mail/senha) | O token JWT fica em memória durante a execução. Não persistir token em disco. |
| D7 | Planilha com abas separadas `Compras` e `Vendas` | Parser mais simples e menos sujeito a erro. Detecção case-insensitive. |
| D8 | Reaproveitar `POST /transactions` agora | Menos invasivo. `POST /import/ledger` fica planejado para depois. |
| D9 | Ordenar compras + vendas por `transactionDate` crescente | O replay do ledger depende da ordem cronológica. |
| D10 | Corretagem não é considerada no MVP | Decisão do usuário; `Total Investido` serve apenas para conferência. |
| D11 | **Fundamentus como fonte primária; CVM apenas para DFC** | Fundamentus entrega BP, DRE, indicadores e proventos de forma simples. A CVM é usada somente para fluxo de caixa, capex e capital de giro. |
| D12 | Python + FastAPI + pandas + PostgreSQL no futuro | Stack adequada para coleta, normalização e exposição dos dados. |
| D13 | Criar ativo ausente zerado | Payload `{ ticker, walletId, amount: 1 }`, sem `unitPrice`; fallback para a primeira compra. |
| D14 | Enviar transações em ordem cronológica | Juntar compras e vendas, ordenar por data e enviar sequencialmente. |
| D15 | Token JWT apenas em memória | Não persistir credenciais ou token em disco. |
| D16 | Fundamentus como fonte principal | Cobre o núcleo dos dados necessários sem depender de API paga. |
| D17 | CVM somente para DFC | A DFC-MI é oficial, gratuita e aberta (ODbL); evita ingestão completa de DFP/ITR. |
| D18 | ADC não calcula DCF | O ADC é fonte de dados; valuation e projeções são responsabilidade do investidor/MyWallet. |
| D19 | Coletor com adaptadores por fonte | Isola client, parser, normalizador e persistência; permite substituir fonte sem afetar a API. |
| D20 | Banco/API detalhados agora, implementados depois | O foco imediato é fechar o importador E2E; a implementação do banco/API vem em seguida. |
| D21 | Operação local com Docker Compose | ADC, PostgreSQL e agendador em containers no ambiente local. |
| D22 | **Cotações históricas vêm do COTAHIST (B3), não da Brapi** | Fonte oficial, gratuita, sem token e sem rate limit por requisição; cobre ações e FIIs. A Brapi permanece como fallback no Consolidator até a cobertura estabilizar. |
| D23 | `daily_close` guarda bruto **e** ajustado | `close` alimenta a reconstrução patrimonial (valor de mercado do dia); `adjusted_close` alimenta a volatilidade. Split/bonus ajustados por `FATCOT`; proventos **não** entram no ajuste e isso é declarado no contrato. |
| D24 | Universo do COTAHIST é o arquivo inteiro | Ingerir todos os tickers dos `CODBDI` aceitos. O arquivo anual já vem completo; filtrar por carteira acoplaria o ADC ao ledger do MyWallet. |
| D25 | Contrato `/v1/prices` congelado | Lote de até 20 tickers, ticker desconhecido vai para `missing` (não derruba o lote), decimais como string, dias sem pregão **não** são preenchidos. |
| D26 | Carga: 5 anos de backfill + job diário | Primeira execução baixa os ZIPs anuais dos últimos 5 anos; depois, um job após o fechamento. Upsert idempotente por `(ticker, trade_date)`. |
| D27 | **Dados do Fundamentus chaveados por ticker**, não por empresa | O Fundamentus publica por papel e não expõe CNPJ. `companies` fica para o coletor da CVM; `tickers.company_id` é nulo até lá. PETR3 e PETR4 repetem BP/DRE — aceitável. |
| D28 | Proventos usam **data-com** (`com_date`), não data-ex | É a data que o Fundamentus publica. A chave inclui `payment_date` (`NULLS NOT DISTINCT`), porque o mesmo evento pode ser pago em duas datas. |
| D29 | **Série trimestral se acumula por coleta** | O Fundamentus só mostra o último trimestre e os 12 meses. Cada coleta grava o trimestre com `period_end` = data do balanço; trimestres anteriores ao primeiro uso exigiriam CVM ITR/DFP (fase opcional). |
| D31 | **Bancos separados para ADC e Consolidator** | Flyway e Alembic não dividem schema; dados públicos recoletáveis (ADC) e ledger do usuário (Consolidator) têm segurança e backup diferentes; integração só via `/v1`. No deploy, um único servidor Postgres com dois databases e dois usuários sem acesso cruzado é aceitável. |
| D30 | **Brapi só para a cotação ao vivo** | Não há fonte gratuita de cotação em tempo real; Fundamentus e COTAHIST são fim de dia. Indicadores, proventos e histórico saem da Brapi. |

## 4. Arquitetura alvo

```text
adc/
├── apps/
│   ├── importer/                  # CLI principal (MVP atual)
│   │   ├── __init__.py
│   │   ├── cli.py                 # Typer: login, dry-run, validate-only, import
│   │   ├── auth.py                # Login via e-mail/senha (token em memória)
│   │   ├── client.py              # httpx client da API do MyWallet
│   │   ├── parser.py              # Leitura de .xlsx/.csv e abas Compras/Vendas
│   │   ├── mapper.py              # Normalização para TransactionDTO
│   │   ├── validator.py           # Validações e preview
│   │   └── service.py             # Orquestração: resolver, criar ativos, dedup e envio
│   ├── ingest/
│   │   ├── fundamentus/           # Coletor Fundamentus
│   │   │   ├── client.py          # HTTP, cache, rate limit e retry
│   │   │   ├── discovery.py       # Descoberta de tickers
│   │   │   ├── parser.py          # Parsing de HTML
│   │   │   ├── normalizer.py      # Normalização e mapeamento canônico
│   │   │   └── repository.py      # Upserts e persistência
│   │   └── cvm_dfc/               # Coletor DFC da CVM
│   │       ├── downloader.py      # Download e validação do ZIP
│   │       ├── parser.py          # Leitura dos CSVs da DFC
│   │       └── normalizer.py      # Normalização, mapeamento e idempotência
│   └── api/                       # API interna FastAPI
│       ├── main.py
│       ├── dependencies.py
│       └── routers/
├── core/
│   ├── config.py                  # Settings (.env)
│   ├── schemas.py                 # Pydantic schemas compartilhados
│   ├── utils.py                   # Datas BR, números, tickers
│   ├── cache.py                   # Cache de HTML/CSV e TTL
│   └── rate_limit.py              # Rate limit, retry e backoff
├── db/
│   ├── models.py                  # Modelos SQLAlchemy
│   ├── session.py                 # Engine e sessões
│   └── migrations/                # Alembic
├── tests/
├── .env.example
├── pyproject.toml
├── README.md
├── requirements.txt
├── requirements-dev.txt
└── docker-compose.yml
```

### Stack do MVP

- `httpx` — cliente HTTP.
- `typer` — CLI.
- `pandas` + `openpyxl` — leitura de `.xlsx`/`.csv`.
- `pydantic` — schemas e validação.
- `pytest` — testes.
- `ruff` — lint/format.

### Stack futura

- FastAPI — API interna read-only.
- PostgreSQL + SQLAlchemy + Alembic — persistência e migrações.
- BeautifulSoup ou selectolax — parsing de HTML.
- APScheduler ou cron — agendamento.
- Docker Compose — operação local.
- Prometheus/metrics opcional — observabilidade.

## 5. Contrato com o MyWallet (Consolidator)

Base local: `http://localhost:8080`.

### Login

```http
POST /auth/login
Content-Type: application/json

{ "email": "...", "password": "..." }
```

Resposta esperada: `{ "token": "...", "user": { ... } }`.

### Listar ativos da carteira

```http
GET /assets?walletId={id}
Authorization: Bearer <token>
```

Usado para montar o mapa `ticker -> assetId`.

### Criar ativo ausente

```http
POST /assets
Authorization: Bearer <token>
Content-Type: application/json

{
  "ticker": "PETR4",
  "walletId": "1",
  "amount": 1
}
```

O backend exige `amount > 0`, mas **ignora o `amount` quando `unitPrice` está ausente**: o ativo nasce zerado, sem transação de abertura. É assim que o importador cria o ativo sem duplicar posição. Se o backend rejeitar esse payload, o fallback é criar com a primeira compra e pular essa linha no envio.

### Criar transação

```http
POST /transactions
Authorization: Bearer <token>
Content-Type: application/json

{
  "assetId": 123,
  "amount": 10,
  "unitPrice": 35.50,
  "type": "BUY",
  "transactionDate": "2024-01-15T00:00:00.000Z"
}
```

Regras:

- `amount` sempre positivo, inclusive em `SELL`.
- `unitPrice` positivo.
- `type`: `BUY` ou `SELL`.
- `transactionDate` em ISO 8601.

## 6. Mapeamento da planilha

### Aba `Compras`

| Coluna | Destino | Observação |
|---|---|---|
| `Data` | `transactionDate` | Aceitar DD/MM/AAAA e ISO. |
| `Ticker` | `ticker` | Uppercase e trim. |
| `Quantidade` | `amount` | Inteiro positivo. |
| `Preço de Compra` | `unitPrice` | Aceitar vírgula decimal. |
| `Total Investido` | conferência | Comparar com `Quantidade * Preço`. Não enviar. |

### Aba `Vendas`

| Coluna | Destino | Observação |
|---|---|---|
| `Data` | `transactionDate` | Aceitar DD/MM/AAAA e ISO. |
| `Ticker` | `ticker` | Uppercase e trim. |
| `Quantidade` | `amount` | Inteiro positivo. |
| `Preço de Venda` | `unitPrice` | Preço efetivo da venda. |
| `Preço medio` | ignorado | Calculado pelo ledger. |
| `Prejuizo/Lucro` | ignorado | Calculado pelo ledger. |

### Normalizações

- Ticker: `petr4 ` -> `PETR4`.
- Data: `15/01/2024` -> `2024-01-15T00:00:00.000Z`.
- Número: `35,50` -> `35.50`; remover separador de milhar quando aplicável.
- Linhas vazias ou de totalizador devem ser descartadas com log.
- `type` derivado da aba no `.xlsx`; em `.csv`, de uma coluna `Tipo`/`Type` ou da flag `--csv-type`.

## 7. Fluxo do importador

```text
1. CLI recebe --file, --wallet-id, --api-url e credenciais (ou lê do .env).
2. Auth: POST /auth/login -> token em memória.
3. Parser: abre .xlsx/.csv, localiza abas "Compras" e "Vendas".
4. Normaliza colunas, datas, números e tickers.
5. Resolve carteira/ativos: GET /assets?walletId= -> mapa ticker->assetId.
6. Para tickers ausentes: cria ativo conforme decisão D13.
7. Mapper: gera transações BUY/SELL com assetId.
8. Junta tudo e ordena por transactionDate crescente.
9. Valida: amount > 0, unitPrice > 0, assetId resolvido, data válida.
10. Executa:
    - --validate-only: apenas valida e reporta.
    - --dry-run: mostra tabela preview sem enviar.
    - --import: envia POST /transactions em sequência, com progresso e log.
```

### CLI proposta

```bash
python -m apps.importer.cli \
  --file "./carteira.xlsx" \
  --wallet-id 1 \
  --api-url "http://localhost:8080" \
  --dry-run
```

Modos:

- `--dry-run`
- `--validate-only`
- `--import`

Credenciais:

- `ADC_EMAIL` / `ADC_PASSWORD` no `.env`, ou flags `--email` / `--password`.
- Nunca commitar `.env`.

## 8. Fases do projeto

| Fase | Objetivo | Status |
|---|---|---|
| **0. Descoberta & Fontes** | Mapear Fundamentus, CVM DFC, ToS, limitações e riscos. | Concluída (pesquisa em 2026-10-30) |
| **1. Scaffolding** | Criar `adc/`, `pyproject.toml`, `.env.example`, README, ruff/pytest. | Concluída |
| **2. Modelagem + Banco** | Modelos PostgreSQL, SQLAlchemy e migrações Alembic. | **Concluída em 2026-11-14** (`0001_baseline`, todas as tabelas da §17) |
| **3. Ingestão Fundamentus** | Coletar e normalizar detalhes, BP, DRE, indicadores e proventos. | **Concluída em 2026-11-14** (ações, bancos e FIIs; resultados trimestrais e agendamento ficam para depois) |
| **4. Ingestão CVM DFC** | Baixar e normalizar DFC-MI para fluxo de caixa, capex e capital de giro. | Planejada |
| **5. Indicadores** | Agregações contábeis simples, sem projeções nem DCF. | Planejada |
| **6. API Interna** | FastAPI read-only para o MyWallet. | Planejada |
| **7. Importador de Planilha** | **MVP atual.** CLI de importação via API. | **MVP implementado; E2E pendente (7.7)** |
| **8. Agendamento + Hardening** | Scheduler, rate limit, logs, métricas, testes e Docker. | Futuro |
| **9. Integração MyWallet** | Cliente HTTP no Consolidator para consumir o ADC. | Futuro |
| **10. Cotações Históricas** | Coletor COTAHIST, tabela `daily_close` e `/v1/prices` (§25/§26). | **Especificada em 2026-11-13; implementação não iniciada** |

### Ordem recomendada

`0 -> 1 -> 7 -> 2 -> 3 -> 6 -> 10 -> 9 -> 4 -> 5 -> 8` (revista em 2026-11-14)

Antes era `… 2 -> 10 -> 3 …`. A Fase 3 subiu porque o objetivo do MyWallet é valuation e os
dados fundamentalistas são o que mais falta; a API (6) vem logo depois para o Consolidator
poder consumir o que já está no banco.

A Fase 7 é independente da coleta e pode ser validada imediatamente. A Fase 2 vem antes das Fases 3, 4 e 10 porque os coletores dependem do modelo de dados. A Fase 10 pode correr em paralelo às Fases 3–5: ela só depende da Fase 2 e não compartilha tabela com fundamentos. Ela traz também a **fatia mínima da Fase 2** (`daily_close` e `ingestion_runs` com Alembic) e o **esqueleto da Fase 6** (FastAPI + token + `/health`), que as fases seguintes reaproveitam.

## 9. Sub-etapas de implementação do importador (Fase 7)

| Etapa | Ação | Critério de conclusão | Status |
|---|---|---|---|
| 7.1 | Criar estrutura `adc/` e configuração do projeto | `python -m apps.importer.cli --help` funciona | Concluída |
| 7.2 | Config + Auth | Login retorna token e é usado nas chamadas | Concluída (código) |
| 7.3 | Parser `.xlsx`/`.csv` | Lê abas `Compras`/`Vendas` e normaliza colunas | Concluída |
| 7.4 | Client HTTP | Métodos de login, listar ativos, criar ativo e criar transação | Concluída (código) |
| 7.5 | Resolver + Mapper | Mapa `ticker -> assetId` e transações no contrato do backend | Concluída |
| 7.6 | Validator + CLI | `--dry-run`, `--validate-only`, `--import`, ordenação e logs | Concluída |
| 7.7 | Testes com planilha real | Dry-run confere com a planilha; importação replica o histórico | Pendente |
| 7.8 | Documentar `POST /import/ledger` | Proposta registrada no `BACKEND_ROADMAP.md` (sem implementar) | Pendente |

## 10. Decisões detalhadas

### D13. Como criar ativo ausente? — DECIDIDO em 2026-10-29

**Decisão:** tentar criar **zerado**. O contrato atual exige `amount > 0`, mas ignora esse valor quando `unitPrice` está ausente; portanto o payload é `{ ticker, walletId, amount: 1 }`, sem `unitPrice`, e o ativo nasce sem transação. Se o backend rejeitar, usar a primeira compra da planilha como abertura e marcar essa linha como já aplicada, pulando-a no envio.

### D14. Ordem de envio — DECIDIDO em 2026-10-29

**Decisão:** sempre juntar compras e vendas, ordenar por `transactionDate` crescente e enviar sequencialmente via `POST /transactions`.

### D15. Token — DECIDIDO em 2026-10-29

**Decisão:** manter apenas em memória durante a execução; não gravar em disco.

### D16. Fonte principal — Fundamentus — DECIDIDO em 2026-10-30

**Decisão:** usar o Fundamentus como fonte primária de dados cadastrais, indicadores, BP, DRE, proventos e resultados trimestrais. O site não oferece API oficial nem SLA; a coleta será feita por HTML com parser isolado, cache, rate limit e tratamento de mudanças.

### D17. CVM somente para DFC — DECIDIDO em 2026-10-30

**Decisão:** usar a DFC-MI da CVM apenas para fluxo de caixa, capex e capital de giro. Não haverá ingestão completa de DFP/ITR. A CVM é gratuita e aberta, com licença ODbL; a fonte oficial elimina a dependência de gráficos do Fundamentus para esses dados.

### D18. ADC não calcula DCF — DECIDIDO em 2026-10-30

**Decisão:** o ADC não calcula valuation, DCF, preço-teto ou projeções. Ele coleta, normaliza e expõe os dados. Agregações contábeis simples, como `FCF = CFO - capex`, dívida líquida/PL e margens, são permitidas porque não envolvem projeção.

### D19. Adaptadores por fonte — DECIDIDO em 2026-10-30

**Decisão:** cada fonte terá client, parser, normalizador e repositório próprios. HTML/CSV bruto será armazenado com hash, URL, data de coleta e versão do parser para permitir reprocessamento sem nova requisição.

### D20. Banco/API detalhados agora, implementados depois — DECIDIDO em 2026-10-30

**Decisão:** o schema, os endpoints e as migrações serão documentados agora, mas a implementação começa depois da validação E2E do importador (Etapa 7.7).

### D21. Docker Compose local — DECIDIDO em 2026-10-30

**Decisão:** a operação futura será local, com containers para API, PostgreSQL e agendador, volumes persistentes, healthchecks e migrações no start.

### D22. Cotações históricas vêm do COTAHIST — DECIDIDO em 2026-11-13

**Decisão:** a série diária de fechamentos é coletada do **COTAHIST** (arquivo anual
da B3), não da Brapi.

**Contexto:** o Consolidator hoje chama `/quote/{ticker}/historical` a cada
requisição — e a volatilidade faz uma segunda chamada por ticker. Isso mantém o
custo por visita e amarra o gráfico ao range que a fonte aceita (5 anos para
ações, ~3 meses para FIIs no plano atual).

**Consequências:**
- A Brapi deixa de ser caminho normal no Consolidator e vira fallback até a
  cobertura do ADC estabilizar (ver §23).
- O ADC passa a ser a fonte canônica de preço histórico; o Consolidator só
  calcula (posição, patrimônio, volatilidade).
- Se a B3 mudar layout ou URL, só o coletor muda — o contrato `/v1/prices`
  permanece.

### D23. Bruto e ajustado na mesma tabela — DECIDIDO em 2026-11-13

**Decisão:** `daily_close` guarda `close` (bruto) e `adjusted_close` (ajustado
por `FATCOT`).

**Motivo:** os dois consumidores querem coisas diferentes. A reconstrução
patrimonial precisa do preço de mercado do dia (bruto); a volatilidade precisa de
uma série contínua, porque um split 1:10 não é um retorno de −90%.

**Limite explícito:** `FATCOT` cobre split, bonificação e inplit — **não** cobre
provento. O contrato expõe `adjusted` por série: `true` quando todos os pontos da
janela tinham fator disponível, `false` caso contrário. O consumidor declara o que
recebeu em vez de supor que está tudo ajustado.

### D24. Universo = arquivo inteiro — DECIDIDO em 2026-11-13

**Decisão:** ingerir todos os tickers dos `CODBDI` aceitos (lote padrão e FII,
lista configurável), sem filtrar pelas carteiras do usuário.

**Motivo:** o COTAHIST é anual e já vem completo; filtrar por carteira exigiria o
ADC conhecer o ledger, o que contraria D4/D5. O volume é trivial para Postgres
(~250 pregões × poucos milhares de tickers por ano).

### D25. Contrato `/v1/prices` congelado — DECIDIDO em 2026-11-13

**Decisão:** o contrato da §26 é a interface oficial entre ADC e Consolidator.
Mudanças exigem atualização desta seção e do cliente HTTP no Consolidator.

**Regras que não podem ser quebradas:**
- lote de até 20 tickers por chamada;
- ticker desconhecido no lote vai para `missing`, com status 200;
- preços como string decimal (`"38.420000"`), nunca float;
- dia sem pregão é ausente da série, nunca preenchido com o fechamento anterior;
- `from > to` é 400.

### D26. Backfill de 5 anos + job diário — DECIDIDO em 2026-11-13

**Decisão:** a primeira execução baixa os ZIPs anuais dos últimos 5 anos e grava
tudo; depois, um job após o fechamento grava o dia corrente.

**Motivo:** 5 anos é o horizonte que a Brapi entrega hoje para ações, então é o
máximo que o gráfico já mostra. Upsert idempotente por `(ticker, trade_date)`
permite reprocessar um arquivo sem duplicar linha.

## 11. Critérios de aceite do MVP

> Itens marcados foram implementados e cobertos por testes unitários. A validação
> end-to-end com backend e planilha real ainda está pendente (Etapa 7.7).

- [x] CLI autentica com e-mail/senha (código).
- [x] Lê `.xlsx` e `.csv`.
- [x] Detecta abas `Compras` e `Vendas` (case-insensitive).
- [x] Normaliza datas BR, números com vírgula e tickers.
- [x] Gera preview em `--dry-run` (código).
- [x] Resolve `ticker -> assetId` por carteira (código).
- [x] Trata ativo ausente conforme D13.
- [x] Envia transações em ordem cronológica (código).
- [x] Não duplica transações já aplicadas (código).
- [x] Mensagens de erro claras para aba/coluna ausente.
- [x] Testes automatizados para parser, normalização, mapper e validação.
- [x] Nenhum segredo no repositório.
- [ ] Validação end-to-end com backend e planilha real.

## 12. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Fundamentus não tem API oficial nem SLA | Adaptador isolado, cache, testes com fixtures e detecção explícita de mudança de HTML. |
| HTML do Fundamentus muda sem aviso | Parser versionado, seletores centralizados, golden files e alerta em falha de parsing. |
| Bloqueio por excesso de requisições | Requisições sequenciais, rate limit conservador, jitter, backoff e cache por TTL. |
| CAPTCHA no download de balanços | Não automatizar o Excel; usar os dados estruturados das páginas e a DFC da CVM. |
| Termos de uso e acesso automatizado | Uso local e conservador; revisar os termos antes de operação contínua; não contornar proteções. |
| Divergência entre Fundamentus e CVM | Guardar fonte, URL, hash e versão; não mesclar silenciosamente; priorizar a fonte definida por campo. |
| Restatements e versões da CVM | Armazenar `VERSAO`, manter histórico e usar a versão mais recente por padrão. |
| Mapeamento CNPJ/código CVM/ticker incompleto | Chave por CNPJ, `CD_CVM` e ticker; tabela de aliases e revisão manual de exceções. |
| Dados ausentes ou `null` | Representar ausência explicitamente; não preencher com zero; registrar lacunas. |
| Duplicar posição ao criar ativo | D13, dry-run e chave de deduplicação. |
| Planilha com formato inconsistente | Parser tolerante, validação com relatório de linhas inválidas. |
| Ordem cronológica errada | Ordenação obrigatória antes do envio. |
| Mudança de contrato no backend | Client centralizado e testes de contrato. |
| Token expirado | Login no início; mensagem clara em 401. |

## 13. Restrições do projeto

- **Nunca** acessar o banco do MyWallet diretamente.
- **Nunca** commitar `.env`, tokens ou credenciais.
- **Nunca** commitar alterações automaticamente; só quando solicitado.
- **Nunca** contornar CAPTCHA, bloqueios ou proteções do Fundamentus.
- Não fazer scraping massivo ou paralelo; usar rate limit conservador e cache.
- Respeitar `robots.txt` e Termos de Uso das fontes.
- Não calcular DCF, valuation ou projeções no ADC.
- Manter proveniência de todos os dados coletados.
- Manter o ADC desacoplado do Consolidator e do Visualizer.

## 14. Próximos passos

1. ~~Confirmar D13 e D14.~~ Concluído.
2. ~~Executar as Etapas 7.1 a 7.6.~~ Concluído.
3. Testar com a planilha real em `--validate-only` e depois `--dry-run`.
4. Rodar `--import` em uma carteira de teste e conferir o ledger no MyWallet.
5. Documentar a proposta de `POST /import/ledger` no `BACKEND_ROADMAP.md`.
6. Implementar o schema PostgreSQL e as migrações Alembic (Fase 2), já com `daily_close`.
7. **Implementar a Fase 10**: coletor COTAHIST, ajuste por `FATCOT`, `daily_close` e `/v1/prices` (§25/§26). Pode ser o primeiro endpoint a subir, criando o esqueleto da API.
8. Implementar o coletor Fundamentus com cache, rate limit e fixtures.
9. Implementar o coletor CVM DFC.
10. Implementar as agregações contábeis simples.
11. Completar a API FastAPI read-only com os demais endpoints.
12. Empacotar com Docker Compose e configurar o agendador.
13. Integrar no Consolidator: cliente `/v1/prices` com timeout, retry e cache curto; Brapi como fallback.

## 15. Estado da implementação (2026-10-30)

### O que existe

```text
Projetos/
├── ADC_PLAN.md
└── adc/
    ├── pyproject.toml
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── .env.example
    ├── README.md
    ├── apps/importer/
    │   ├── cli.py
    │   ├── auth.py
    │   ├── client.py
    │   ├── parser.py
    │   ├── mapper.py
    │   ├── validator.py
    │   └── service.py
    ├── core/
    │   ├── config.py
    │   ├── schemas.py
    │   └── utils.py
    └── tests/
```

### Verificação

```bash
cd adc
.venv/Scripts/python.exe -m pytest       # 40 passed
.venv/Scripts/ruff.exe check .           # All checks passed
.venv/Scripts/python.exe -m apps.importer.cli --help
```

### Decisões de implementação

- O parser ignora linhas acima do cabeçalho (título) e encontra `Data` + `Ticker`
  nas primeiras 30 linhas.
- `Total Investido` é usado apenas para conferência, com tolerância de 0,5%.
- Ativos ausentes são criados zerados com `amount=1` e sem `unitPrice`.
- O fallback para a primeira compra só ocorre em `400` na criação zerada.
- A deduplicação usa `ticker + data + quantidade + preço + tipo`.
- `--validate-only` não autentica e não faz chamadas HTTP.
- `--dry-run` autentica e consulta ativos/transações, mas não grava.
- O token JWT fica apenas em memória.
- O coletor CVM DFC e a API ainda **não** foram implementados.

### Atualização 2026-11-14 — banco + coletor Fundamentus

Novos módulos:

```text
adc/
├── docker-compose.yml             # postgres:16-alpine na porta 5433, volume adc_pgdata
├── alembic.ini
├── db/{models,session}.py, db/migrations/versions/0001_baseline.py
├── core/{cache,rate_limit}.py     # cache de HTML com TTL + intervalo mínimo com jitter
└── apps/ingest/
    ├── cli.py                     # adc-ingest fundamentus --tickers ... | --wallet-id N
    └── fundamentus/{client,parser,normalizer,repository,service}.py
```

Verificação real (2026-11-14): PETR4 (ação), ITUB4 (banco) e HGLG11 (FII) coletados do site.
Valores conferidos contra a página; a segunda execução não criou nenhuma linha nova
(idempotente); `XPTO9` caiu como `not_found` sem derrubar o lote.

Decisões de implementação:

- O parser lê pares rótulo/valor por **seção** e **ocorrência**, nunca por posição: o layout
  muda entre ação, banco e FII. Na DRE, a 1ª ocorrência do rótulo é `ttm` e a 2ª, `quarterly`.
- Rótulo desconhecido vira aviso no `ingestion_run`; ticker, cotação e data da cotação
  ausentes derrubam o papel (mudança de layout).
- Ticker inexistente: o site responde 200 com "Nenhum papel encontrado" → `not_found`.
- Proventos de FII vêm de `fii_proventos.php`, com outras colunas; a tabela é lida pelo
  cabeçalho.
- 403 interrompe a coleta na hora; 429/5xx têm retry com backoff, e 429 persistente também
  interrompe. Os papéis não processados ficam em `stats_json.skipped`.
- O Fundamentus não publica `robots.txt` (404). O ritmo continua conservador (~3 s + jitter).
- Bancos: o site mostra `0,0%` em margem líquida e EBIT/Ativo. O valor é gravado como está;
  quem consome deve ignorar essas métricas para bancos.
- Testes de banco (`@pytest.mark.db`) rodam num banco separado `adc_test`, migrado
  automaticamente, e são pulados se o PostgreSQL não estiver no ar.

## 16. Catálogo de dados

| Categoria | Dados | Fonte | Uso |
|---|---|---|---|
| Identificação | Ticker, tipo, empresa, setor, subsetor | Fundamentus | Cadastro e segmentação |
| Mercado | Cotação, valor de mercado, valor da firma, número de ações, volume médio, mínima/máxima 52 semanas | Fundamentus | Contexto de valuation |
| Indicadores | P/L, P/VP, PSR, DY, P/EBIT, P/Ativos, P/Cap. Giro, P/Ativ. Circ. Liq., EV/EBITDA, EV/EBIT, LPA, VPA, margens, ROE, ROIC, liquidez, dívida líquida/PL, crescimento de receita | Fundamentus | Análise fundamentalista |
| Balanço Patrimonial | Ativo total, ativo circulante, disponibilidades, dívida bruta, dívida líquida, patrimônio líquido | Fundamentus | Estrutura de capital |
| DRE | Receita líquida, EBIT, lucro líquido (TTM e trimestre) | Fundamentus | Rentabilidade |
| DFC | Fluxo operacional, investimento, financiamento, capex e capital de giro | CVM DFC-MI | Fluxo de caixa e FCF |
| Proventos | Data ex, data de pagamento, valor, tipo, proporção por ação | Fundamentus | Dividendos e payout |
| Resultados trimestrais | Data de referência, documento, status de processamento | Fundamentus | Histórico e atualização |
| Documentos brutos | HTML/CSV original, URL, hash, data e versão do parser | Fundamentus/CVM | Auditoria e reprocessamento |
| Cotações históricas | Fechamento diário bruto e ajustado (split/bonus) por ticker | COTAHIST (B3) | Reconstrução patrimonial e volatilidade |
| Agregações simples | Dívida líquida/PL, margens, DY, payout, `FCF = CFO - capex` | Cálculo interno | Apoio ao investidor, sem projeções |

### Granularidade

- BP e DRE: anual e trimestral, conforme disponibilidade.
- Indicadores: último balanço processado e TTM.
- DFC: anual e trimestral, consolidada e individual.
- Proventos: evento a evento.
- Mercado: snapshot na data da coleta.
- Cotações históricas: um ponto por ticker por pregão; dias sem negociação ficam ausentes da série, nunca repetidos do dia anterior.

## 17. Modelo de dados e persistência

Banco previsto: PostgreSQL. Acesso via SQLAlchemy e migrações Alembic. Valores monetários em `numeric(20,6)`, datas em `date`/`timestamptz`, metadados em `jsonb`.

### Tabelas

| Tabela | Campos principais | Chaves e índices |
|---|---|---|
| `companies` | `id`, `cnpj`, `cvm_code`, `name`, `sector`, `subsector`, `created_at`, `updated_at` | `cnpj` único quando existir; `cvm_code` indexado |
| `tickers` | `id`, `company_id`, `ticker`, `type`, `is_active` | `ticker` único; FK para `companies` |
| `market_snapshots` | `id`, `company_id`, `ticker_id`, `reference_date`, `price`, `market_cap`, `enterprise_value`, `shares_outstanding`, `volume_avg_2m`, `source`, `raw_document_id` | único por `ticker_id + reference_date + source` |
| `daily_close` | `id`, `ticker`, `trade_date`, `close`, `adjusted_close`, `source`, `ingested_at` | único por `ticker + trade_date`; índice por `trade_date` |
| `financial_statements` | `id`, `company_id`, `statement_type`, `period_type`, `period_start`, `period_end`, `fiscal_year`, `version`, `source`, `source_url`, `raw_document_id`, `parser_version`, `ingested_at` | único por `company_id + statement_type + period_type + period_end + version + source` |
| `statement_lines` | `id`, `statement_id`, `account_code`, `label`, `value`, `currency`, `scale`, `line_order`, `is_fixed` | único por `statement_id + account_code`; índice por `account_code` |
| `dividends` | `id`, `ticker_id`, `com_date`, `payment_date`, `amount`, `type`, `shares_ratio`, `source`, `raw_document_id` | único por `ticker_id + com_date + type + amount + payment_date` (`NULLS NOT DISTINCT`, D28) |
| `indicators` | `id`, `company_id`, `reference_date`, `name`, `value`, `source`, `formula_version` | único por `company_id + reference_date + name + source` |
| `raw_documents` | `id`, `source`, `url`, `content_hash`, `storage_path`, `fetched_at`, `http_status`, `parser_version` | único por `source + content_hash` |
| `ingestion_runs` | `id`, `source`, `job_name`, `started_at`, `finished_at`, `status`, `stats_json`, `error` | índice por `source + started_at` |
| `source_aliases` | `id`, `source`, `alias`, `company_id`, `ticker_id` | único por `source + alias` |

### Regras

- Toda linha deve ter proveniência: `source`, `source_url`, `raw_document_id`, `ingested_at`.
- O documento bruto deve ser preservado antes do parsing.
- Upserts devem ser idempotentes por chave natural + hash.
- Restatements da CVM devem gerar nova versão, sem sobrescrever o histórico.
- Campos ausentes devem ser `NULL`, nunca zero inventado.
- `daily_close` usa o **ticker** como chave natural e não depende de `companies`/`tickers` estar populado: o COTAHIST pode trazer papel que o Fundamentus não cobre. O vínculo é resolvido depois, sem bloquear a ingestão.
- `daily_close` nunca preenche dia sem pregão; a ausência é a informação.
- Não há escrita no banco do MyWallet.

## 18. Ingestão Fundamentus

### Páginas utilizadas

- `detalhes.php?papel={ticker}` — identificação, mercado, indicadores, BP e DRE resumidos.
- `proventos.php?papel={ticker}&tipo=2` — histórico de proventos.
- `resultados_trimestrais.php?papel={ticker}&tipo=1` — resultados trimestrais e links de documentos.
- `balancos.php?papel={ticker}` — página de download de Excel; **não automatizar** por causa do CAPTCHA.

### Fluxo

```text
1. Descobrir tickers ativos.
2. Para cada ticker, buscar as páginas em sequência.
3. Salvar HTML bruto com URL, hash e data.
4. Parsear tabelas e campos canônicos.
5. Normalizar números, datas, percentuais e nulos.
6. Upsert de empresa, ticker, mercado, BP, DRE, indicadores e proventos.
7. Registrar métricas e falhas em ingestion_runs.
```

### Política de requisições

- Uma requisição por vez; sem paralelismo por padrão.
- Intervalo conservador entre requisições, com jitter.
- `User-Agent` identificável.
- Timeout curto e retry com backoff exponencial para `429` e `5xx`.
- Parar o job em `403`/`429` repetido e registrar o motivo.
- Cache de HTML com TTL:
  - detalhes: 24h;
  - proventos: 12h;
  - resultados trimestrais: 24h.
- Não contornar CAPTCHA nem bloqueios.

### Parsing e normalização

- Respeitar o encoding ISO-8859-1 das páginas.
- Converter `1.234,56` para `1234.56`; `12,3%` para `12.3`.
- Tratar `-`, vazio e valores indisponíveis como `NULL`.
- Mapear rótulos para nomes canônicos, sem depender de posição fixa.
- Detectar mudanças de HTML por seletores obrigatórios e falhar de forma explícita.
- Versionar o parser e manter fixtures/golden files.

### Limitações

- O Fundamentus não oferece DFC em tabela; o fluxo de caixa é suprido pela CVM.
- Não há API oficial, SLA ou garantia de estabilidade.
- Não há histórico completo de todos os campos em formato aberto.
- O Excel de balanços exige CAPTCHA e fica fora do escopo automatizado.

## 19. Ingestão CVM DFC

### Fonte

- Dataset: `https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/`
- Arquivo anual: `dfp_cia_aberta_AAAA.zip`
- Arquivos usados:
  - `dfp_cia_aberta_DFC_MI_con_AAAA.csv` — consolidado;
  - `dfp_cia_aberta_DFC_MI_ind_AAAA.csv` — individual.
- Licença: ODbL.
- Atualização: semanal, incluindo reapresentações.

### Colunas relevantes

`CNPJ_CIA`, `DT_REFER`, `VERSAO`, `DENOM_CIA`, `CD_CVM`, `GRUPO_DFP`, `MOEDA`, `ESCALA_MOEDA`, `ORDEM_EXERC`, `DT_INI_EXERC`, `DT_FIM_EXERC`, `CD_CONTA`, `DS_CONTA`, `VL_CONTA`, `ST_CONTA_FIXA`.

### Fluxo

```text
1. Descobrir anos disponíveis.
2. Baixar o ZIP anual para o cache.
3. Validar ZIP e hash.
4. Extrair apenas os CSVs da DFC-MI.
5. Parsear CSV com separador ; e encoding latin-1.
6. Normalizar CNPJ, código CVM, datas, moeda, escala e valores.
7. Mapear empresa/ticker por CNPJ e CD_CVM.
8. Upsert de financial_statements e statement_lines, mantendo versão.
9. Calcular/registrar capex e FCF como campos derivados simples.
10. Registrar ingestion_run com contagens e erros.
```

### Regras

- Preferir a demonstração consolidada; usar individual quando a consolidada não existir e registrar a escolha.
- Guardar `VERSAO` e `ORDEM_EXERC`; não sobrescrever versões anteriores.
- Normalizar `VL_CONTA` pela `ESCALA_MOEDA` para reais.
- Identificar capex pelas contas de investimento em imobilizado/intangível; manter também as linhas brutas.
- `FCF = fluxo de caixa operacional - capex` é agregação simples, não projeção.
- Backfill desde 2010; atualização semanal.
- Se o mapeamento CNPJ/ticker falhar, registrar pendência em vez de descartar o dado.

## 20. API interna

API FastAPI, somente leitura, voltada ao Consolidator/Visualizer.

### Autenticação

- Token interno via header `X-ADC-Token`, configurado por ambiente.
- Comparação em tempo constante.
- Sem login de usuário final.
- API não exposta publicamente por padrão.

### Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/health` | Status da API, banco e última ingestão. |
| GET | `/v1/companies` | Lista empresas com busca, setor e paginação. |
| GET | `/v1/companies/{ticker}` | Detalhe da empresa e tickers relacionados. |
| GET | `/v1/companies/{ticker}/market` | Snapshots de mercado. |
| GET | `/v1/companies/{ticker}/statements` | BP, DRE ou DFC por período. |
| GET | `/v1/companies/{ticker}/dividends` | Proventos por intervalo. |
| GET | `/v1/companies/{ticker}/indicators` | Indicadores por data de referência. |
| GET | `/v1/prices/{ticker}` | Série diária de fechamentos (bruto e ajustado) de um ticker. |
| GET | `/v1/prices` | Mesma série para um lote de até 20 tickers. Contrato na §26. |
| GET | `/v1/ingestion/runs` | Histórico e status das ingestões. |

### Parâmetros

- `type=BP|DRE|DFC`
- `period=annual|quarterly`
- `from`, `to`
- `tickers` (lote do `/v1/prices`, separado por vírgula)
- `page`, `page_size`
- `search`, `sector`

### Convenções

- JSON em `snake_case`.
- Datas em ISO 8601.
- Valores monetários como string decimal para evitar erro de ponto flutuante.
- Toda resposta inclui `source`, `reference_date` e `ingested_at` quando aplicável.
- Paginação com metadados `page`, `page_size`, `total`.
- `ETag`/`Cache-Control` para respostas estáveis.
- Erros padronizados: `code`, `message`, `details`.
- OpenAPI em `/docs` e `/openapi.json`.
- Nenhum endpoint calcula DCF ou projeções.

## 21. Operação, agendamento e deploy

### Docker Compose

Serviços previstos:

- `postgres` — PostgreSQL com volume persistente.
- `adc-api` — FastAPI.
- `adc-scheduler` — jobs de ingestão.

### Variáveis de ambiente

- `DATABASE_URL`
- `ADC_API_TOKEN`
- `FUNDAMENTUS_BASE_URL`
- `FUNDAMENTUS_RATE_LIMIT_SECONDS`
- `COTAHIST_BASE_URL`
- `COTAHIST_BACKFILL_YEARS` (default `5`)
- `CACHE_DIR`
- `LOG_LEVEL`
- `TZ`

### Jobs

- Fundamentus: diário.
- CVM DFC: semanal.
- Indicadores: após cada ingestão bem-sucedida.
- Cotações (COTAHIST): diário após o fechamento (18:30 BRT); backfill de 5 anos na primeira execução, sempre idempotente.
- Limpeza de cache: periódica.

### Regras operacionais

- Lock de job no PostgreSQL para evitar execuções concorrentes.
- Retry com backoff; falha persistente gera status `failed` e permite reprocessamento manual.
- Logs estruturados em JSON.
- Métricas: requisições, sucessos, falhas, itens processados, duração e última execução.
- Healthcheck da API e do banco.
- Migrações Alembic no start do container da API.
- Backup do PostgreSQL via `pg_dump`.
- Retenção de documentos brutos configurável.
- Deploy local; sem premissa de cloud.

## 22. Testes e qualidade

- Unitários:
  - normalização de datas, números, percentuais e tickers;
  - parsing de HTML e CSV;
  - parsing do COTAHIST (registros de 245 bytes, `TIPREG`, `CODBDI`, `CODNEG`, `PREULT`, `FATCOT`);
  - deduplicação e idempotência;
  - rate limit, retry e backoff;
  - mapeamento CNPJ/código CVM/ticker.
- Golden files:
  - páginas do Fundamentus;
  - trechos de CSV da DFC;
  - arquivo COTAHIST real com pregão de split/bonus conhecido, para fixar o sentido do ajuste por `FATCOT`.
- Contrato:
  - schemas Pydantic da API, incluindo `/v1/prices` e `/v1/prices?tickers=`;
  - respostas e erros.
- Integração:
  - PostgreSQL via container;
  - migrações Alembic;
  - upserts e restatements.
- Qualidade de dados:
  - campos obrigatórios;
  - períodos duplicados;
  - escala/moeda;
  - valores nulos;
  - divergência entre fontes.
- CI sem acesso à internet; smoke tests opcionais e controlados.
- Meta inicial: 80% de cobertura nos módulos de parsing e normalização.
- `ruff check` e `ruff format --check` obrigatórios.

## 23. Integração com o MyWallet

- O ADC é um serviço de dados read-only; o Consolidator consome via HTTP.
- Nenhuma escrita direta no banco do MyWallet.
- O cliente do Consolidator deve ter timeout, retry e cache local curto.
- A API entrega dados normalizados e metadados de proveniência/frescor.
- O Visualizer usa os dados para análise; o investidor faz as projeções e o valuation.
- O fallback temporário para Brapi pode ser mantido até a cobertura do ADC estabilizar.
- **Preço histórico:** `/v1/prices` é a fonte canônica de fechamentos. O Consolidator consulta em lote os tickers com posição na janela, usa `close` para reconstruir o patrimônio e `adjusted_close` para a volatilidade. Se o ADC não responder, cai para a Brapi; se as duas falharem, o dia/ticker é declarado como indisponível (`null` + aviso), nunca zero.
- **Ao integrar**, o Consolidator deixa de fazer uma chamada por ticker por endpoint: a mesma resposta do lote alimenta histórico e volatilidade.
- Versionamento da API via `/v1`.
- Consistência eventual: a resposta deve indicar `reference_date` e `ingested_at`.
- Autenticação por token interno; sem exposição pública.

## 24. Pendências de definição antes da implementação

1. ~~Universo inicial de tickers para **fundamentos**~~ — **decidido em 2026-11-14:** tickers informados (`--tickers`) e/ou das carteiras do usuário (`--wallet-id`, via API). Varrer a B3 inteira fica fora.
2. Profundidade histórica desejada para BP/DRE: últimos 5 anos, 10 anos ou desde 2010?
3. Preferência por demonstração consolidada ou individual quando ambas existirem?
4. Frequência desejada de atualização do Fundamentus: diária ou semanal?
5. Quais indicadores entram no MVP da API?
6. Retenção de HTML/CSV bruto: indefinida, 1 ano ou permanente?
7. O campo `FCF` deve ser exposto pela API ou calculado no Consolidator/Visualizer?
8. A API será consumida apenas localmente ou também por outros dispositivos da rede?

## 25. Ingestão de cotações históricas (Fase 10)

**Status:** especificada em 2026-11-13; implementação não iniciada.

### Objetivo

Ser a fonte canônica do fechamento diário por ticker, para que o Consolidator
pare de chamar a Brapi a cada requisição — hoje são duas chamadas por ticker em
`/analysis` (histórico + volatilidade).

### Fonte

- **COTAHIST** (B3): arquivo anual `COTAHIST_A{YYYY}.ZIP`, com um TXT de
  registros de largura fixa (245 caracteres), encoding latino.
- URL base configurável em `COTAHIST_BASE_URL` — o layout é estável, o endereço
  não é; a URL efetiva deve ser confirmada na primeira execução e registrada no
  README.
- O documento bruto (ZIP/TXT) é preservado em `CACHE_DIR` com hash, como as
  demais fontes.

### Campos usados

| Campo do COTAHIST | Uso |
|---|---|
| `TIPREG` | `01` = registro de cotação; `00`/`99` são header/trailer |
| `DATA` | `trade_date` (YYYYMMDD → date) |
| `CODBDI` | filtro de mercado: `02` (lote padrão) e `12` (FII), configurável |
| `TPMERC` | `010` = mercado à vista |
| `CODNEG` | `ticker` |
| `PREULT` | `close` (fechamento bruto) |
| `FATCOT` | fator de cotação, base do `adjusted_close` |
| `QUATOT` / `VOLTOT` | volume — armazenar se barato, não é requisito |

### Ajuste por `FATCOT`

- `FATCOT` é `1.000000000` na maioria dos pregões e assume o fator no dia do
  evento (split, bonificação, inplit).
- O coletor deve aplicar o fator acumulado de forma que a série fique
  **contínua** na data do evento: o retorno daquele dia não pode ser o salto
  artificial do split.
- **A direção do ajuste (multiplicar ou dividir) deve ser confirmada com um
  split real e fixada em teste golden antes de a fase ser considerada
  concluída.** Não implementar "no olho".
- Provento **não** é ajustado (D23). O contrato expõe `adjusted` para o
  consumidor saber exatamente o que recebeu.

### Fluxo

```text
1. Descobrir os anos a ingerir (backfill de 5 anos ou ano corrente no job diário).
2. Baixar o ZIP anual para o cache, validando hash.
3. Extrair o TXT.
4. Ler linha a linha, filtrando TIPREG=01, TPMERC=010 e CODBDI aceitos.
5. Normalizar data, ticker e preços (escala 2 do arquivo → numeric(20,6)).
6. Calcular adjusted_close a partir do fator acumulado.
7. Upsert em daily_close por (ticker, trade_date).
8. Registrar ingestion_run com contagens, anos processados e erros.
```

### Regras

- Upsert idempotente: reprocessar um ano não duplica nem "corrige" para trás sem
  que o arquivo mude.
- Dia sem pregão não gera linha.
- Ticker que não existe no Fundamentus continua sendo gravado: `daily_close` não
  depende de `companies`/`tickers`.
- Falha em um ano não aborta os demais; o `ingestion_run` registra o que passou.
- Job com lock no PostgreSQL; retry com backoff na camada de download.

### Critérios de aceite

- [ ] Fatia mínima da Fase 2 implementada: `daily_close` e `ingestion_runs` com Alembic. As tabelas de fundamentos ficam para as Fases 3/4.
- [ ] `daily_close` com ~5 anos, contagem por ano registrada no `ingestion_run`.
- [ ] Repetir a ingestão do mesmo ano mantém a contagem de linhas.
- [ ] Golden test de split: série contínua e retorno do dia do evento dentro do
  esperado.
- [ ] `GET /v1/prices/{ticker}` e `GET /v1/prices?tickers=` conforme a §26.
- [ ] Ticker desconhecido: `missing` no lote, 404 no endpoint individual.
- [ ] `ruff check`, `ruff format --check` e pytest verdes.
- [ ] `README` e `.env.example` com `COTAHIST_BASE_URL` e
  `COTAHIST_BACKFILL_YEARS`.

---

## 26. Contrato `/v1/prices` (congelado em 2026-11-13)

Interface oficial entre ADC e Consolidator (D25). Qualquer mudança exige atualizar
esta seção **e** o cliente HTTP no Consolidator.

### Autenticação e base

- Header `X-ADC-Token`, igual aos demais endpoints.
- Base: `/v1`, JSON `snake_case`, datas ISO `yyyy-MM-dd`.

### Série individual

```http
GET /v1/prices/PETR4?from=2024-01-01&to=2024-01-31
X-ADC-Token: <token>
```

```json
{
  "ticker": "PETR4",
  "from": "2024-01-01",
  "to": "2024-01-31",
  "source": "COTAHIST",
  "ingested_at": "2026-11-13T02:10:00Z",
  "adjusted": true,
  "coverage": { "first_date": "2021-11-16", "last_date": "2026-11-12" },
  "points": [
    { "date": "2024-01-02", "close": "38.420000", "adjusted_close": "38.420000" },
    { "date": "2024-01-03", "close": "38.910000", "adjusted_close": "38.910000" }
  ]
}
```

### Lote

```http
GET /v1/prices?tickers=PETR4,VALE3&from=2024-01-01&to=2024-01-31
X-ADC-Token: <token>
```

```json
{
  "from": "2024-01-01",
  "to": "2024-01-31",
  "series": [
    { "ticker": "PETR4", "source": "COTAHIST", "ingested_at": "...", "adjusted": true,
      "coverage": { "first_date": "...", "last_date": "..." }, "points": [ ... ] },
    { "ticker": "VALE3", "source": "COTAHIST", "ingested_at": "...", "adjusted": false,
      "coverage": { "first_date": "...", "last_date": "..." }, "points": [ ... ] }
  ],
  "missing": ["XPTO3"]
}
```

### Regras

- `from`/`to` opcionais; ausentes devolvem a cobertura inteira (máximo de 10
  anos por chamada; acima disso, 400).
- Lote de **até 20 tickers**; acima disso, 400 `too_many_tickers`.
- Ticker desconhecido no lote vai para `missing` com status **200** — um papel
  problemático não derruba a resposta.
- Ticker desconhecido no endpoint individual → **404** `ticker_not_found`.
- `points` em ordem crescente de data, sem duplicata e **sem preencher** dias sem
  pregão.
- Preços como **string decimal com 6 casas** (`"38.420000"`); nunca float.
- `adjusted` é `true` somente quando todos os pontos da janela tinham `FATCOT`.
  Quando `false`, `adjusted_close` continua presente e igual a `close` — o
  consumidor declara "não ajustado" em vez de supor.
- `coverage` reflete o **banco**, não a janela pedida: é o que permite distinguir
  "não houve pregão" de "não foi ingerido".
- `from > to` → 400 `invalid_range`.
- Erros no envelope padrão: `{ "code", "message", "details" }`.
- `ETag`/`Last-Modified` derivados de `ingested_at` + janela;
  `Cache-Control: private, max-age=3600`.
- O endpoint **só entrega preço**: não calcula retorno, volatilidade, valuation
  nem projeção (D18).

### Uso no Consolidator

| Necessidade | Campo |
|---|---|
| Reconstrução patrimonial (patrimônio do dia) | `close` |
| Volatilidade por ativo | `adjusted_close` + `adjusted` |
| Avisos de cobertura | `coverage` + `missing` |
| Frescor do dado | `ingested_at` |

Este contrato substitui a heurística atual do Consolidator ("a série inteira tem
`adjustedClose`?"): a resposta diz explicitamente se está ajustada.
