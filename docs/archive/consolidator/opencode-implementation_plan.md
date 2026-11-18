> **Histórico, arquivado em 2026-11-17.** Origem: `consolidator/.opencode/plans/implementation_plan.md`.
> Substituído por: specs/ e docs/adr/ do mywallet-hub (spec 003)
> Conteúdo original abaixo, sem edição.

# Implementation Plan — consolidator

See `implementation_plan.html` at repo root for full detail and
`consolidator/BACKEND_ROADMAP.md` for the phase-by-phase backend log.

## Status

| Phase | Status |
|---|---|
| **0 — Cleanup & Bug Fixes** | ✅ DONE |
| **1 — JWT Authentication** | ✅ DONE |
| **2 — Transaction Management** | ✅ DONE |
| **3 — Portfolio Consolidation** | ✅ DONE |
| **4 — Tests & Polish** | ✅ DONE |
| **5 — Production Persistence & Docker** | 🔄 IN PROGRESS (só logback e validação em Postgres real pendentes) |
| **6 — DevEx Improvements** | ⬜ NOT STARTED |

## Phase 4 — Tests & Polish (done)

- 4.1 Service unit tests — done.
- 4.2 Controller tests — done, mas **não** com `@WebMvcTest`: os resource tests
  usam `@SpringBootTest(webEnvironment = MOCK)` + `@AutoConfigureMockMvc`, com o
  service mockado. O objetivo do item (status HTTP, payload e segurança) está
  coberto.
- 4.3 JWT auth tests — done (`JwtServiceTest`, `JwtAuthFilterTest`,
  `AuthFailureSemanticsTest`).
- 4.4 `BrapiAdapterTest` com `MockRestServiceServer` — done.
- 4.5 MapStruct mapper test (`AssetDataToAssetMapperTest`) — done.
- 4.6 Repository tests (`@DataJpaTest`) — done.
- 4.7 Dockerfile multi-stage — done.
- 4.8 `docker-compose.yml` (app + PostgreSQL) — done.
- 4.9 PUT/DELETE — done para users, wallets, assets e transactions.
- Swagger/OpenAPI — `springdoc-openapi-starter-webmvc-ui` no `pom.xml`, sem
  classe de configuração (auto-config; UI em `/swagger-ui.html`).

## Phase 5 — Production Persistence & Docker (remaining)

- [x] PostgreSQL (`application-prod.properties`, `ddl-auto=validate`)
- [x] Multi-stage Dockerfile
- [x] docker-compose com PostgreSQL
- [x] Segredos por variável de ambiente (`BRAPI_TOKEN`, `APP_JWT_SECRET`,
      `SPRING_DATASOURCE_*`)
- [x] Health checks (`/actuator/health`, `management.endpoints...`)
- [x] Flyway (`db/migration/V1__baseline.sql` a `V4__portfolio_snapshots.sql`,
      `baseline-on-migrate`)
- [ ] Logging configuration (`logback-spring.xml`) — hoje só
      `logging.level.root=INFO` no `application-prod.properties`
- [ ] Validação em PostgreSQL real (`docker compose up` com volume vazio)

## Phase 6 — DevEx Improvements

- [ ] 6.1 Add pgAdmin to docker-compose
  - Image: `dpage/pgadmin4`
  - Port: 5050
  - Auto-configure server connection to `postgres` service
  - Only enabled via `docker-compose --profile dev up`

## Delivered outside the original numbering

### 6.3.2 + 6.3.3 do plano do front — posição zerada e recusa com código (2026-11-04)

Implementado junto com o front; aguardando revisão manual antes do commit.

- `ConsolidationService` ganhou `hasOpenPosition` (`amount > 0`) aplicado em
  `getPortfolioSummary` e `getPortfolioTotals`: ativo vendido por completo sai
  dos totais, da alocação, de `assetCount`, de `missingPrices` e da consulta à
  Brapi. `amount == 0` é posição zerada, não dado faltando — por isso a
  comparação é com zero, não com `null`.
- `BusinessRuleException` com `code` estável (`SELL_BEFORE_PURCHASE`,
  `INSUFFICIENT_POSITION`); o `GenericExceptionHandler` devolve
  `{error, code}` no 400. O `code` é o contrato que permite à tela escolher o
  pop-up sem comparar a mensagem.
- `AssetPositionCalculator` passou a lançar essa exceção, com a mensagem
  `Não é possível vender um ativo antes de sua data de compra.`.
- Testes: `ConsolidationServiceTest` (posição zerada em summary e totals, sem
  chamada à Brapi), `AssetPositionCalculatorTest`, `TransactionServiceTest` e
  `TransactionResourceTest` (400 com `code`). Suíte completa: 303 testes.

### 6.3 do plano do front — Resultado realizado (2026-11-02)

O número vem de `visualizer/IMPLEMENTATION_PLAN.md`; o backend não tinha fase
própria para isso. Entregue junto com o front e commitado.

- `GET /transactions/results` com `walletId`, `from` e `to` opcionais.
  `from` depois de `to` responde 400; posse da carteira validada pelo
  `TransactionService` (carteira alheia é 403).
- `RealizedResultService`: resultado por venda, totais (vendido, lucro,
  prejuízo, líquido) e compensação cronológica de prejuízos.
  `openingLossBalance` carrega o prejuízo anterior a `from`, para que filtrar um
  mês não apague o histórico.
- `AssetPositionCalculator`: o replay passou a devolver
  `ReplayResult`/`RealizedSale`, com o custo médio **vigente no ponto da venda**
  (não o preço médio atual, que só vale para a prévia do formulário).
- `TransactionResponseDTO.realizedResult` preenchido em create, list, get e
  update; `null` em compra.
- Testes: `RealizedResultServiceTest`, `TransactionResourceTest` (rota
  `/results` convivendo com `/{id}`, validação de período) e
  `AssetPositionCalculatorTest` (replay por venda).

## Backlog

### Datas de negociação — ENTREGUE (6.6 do plano do front, 2026-11-04)

Detalhe completo no plano do front, item **6.6**. Aguardando revisão manual.

**Decisão: data de transação é dia, não instante.**

- O contrato da API ficou date-only: `TransactionDTO.transactionDate` e
  `AssetCreateDTO.acquisitionDate` são `LocalDate` (JSON `2026-11-01`), e
  `TransactionResponseDTO.transactionDate` também. O front manda e recebe dia.
- A coluna continua `timestamp`: trocar para `date` exigiria migração com SQL
  diferente em H2 e PostgreSQL (`ddl-auto=validate` nos dois). O instante
  gravado é a meia-noite UTC do dia — a mesma forma que as linhas antigas já
  tinham, então **não houve migração de dados**.
- `common/utils/TradingDay` concentra a conversão: `today()` em
  `America/Sao_Paulo` (calendário do usuário e do pregão), `toDay`/`startOfDay`
  em meia-noite UTC (envelope de armazenamento), `rejectFuture`.
- `common/utils/LedgerOrder`: ordem canônica **dia → BUY antes de SELL → id**,
  compartilhada por `TransactionService` e `RealizedResultService`. Era a
  ausência dela que fazia uma venda “hoje” cair antes de uma compra de abertura
  do mesmo dia.
- `AssetService` deixou de abrir posição com `new Date()`; usa
  `TradingDay.today()`.
- **Fase D entrou junto**: data futura é recusada no servidor com o código
  `FUTURE_TRANSACTION_DATE`. Não usei `@PastOrPresent` porque a anotação usa o
  fuso padrão da JVM (aceitaria ou recusaria conforme o servidor rodasse em UTC
  ou BRT).
- Correção colateral: o corte do histórico passou de `<=` meia-noite do dia
  para `<` meia-noite do dia seguinte — antes a transação do dia seguinte
  vazava para o dia anterior (`TransactionRepository`,
  `PortfolioHistoryService`).
- Testes: `TradingDayTest`, `LedgerOrderTest`, venda no mesmo dia da compra
  (`AssetOpeningTransactionTest`), data futura (`TransactionServiceTest`),
  contrato date-only (`TransactionResourceTest`, `AssetResourceTest`) e corte
  exclusivo (`TransactionRepositoryTest`, `PortfolioHistoryServiceTest`).
  Suíte completa: **316 testes**.

**Fica de fora:** `PortfolioSnapshotService` e `DividendService` ainda derivam
dia com `ZoneId.systemDefault()`. Não fazem parte do caminho de transação e
mexer nos snapshots mudaria a chave de upsert dos existentes; revisitar junto
com a 6.7.

### Evolução patrimonial por fechamento

Detalhe completo no plano do front, item **6.7**.

- **Persistir fechamentos diários** (tabela `daily_close`, preenchida no mesmo
  job do snapshot) para o gráfico de evolução deixar de depender do `range` da
  Brapi a cada requisição. O `BrapiAdapter.getHistoricalPrices` e o
  `PortfolioHistoryService` já reconstroem a série; o que falta é guardá-la.
- Decisão em aberto: esperar o microservice ADC ser a fonte canônica de preços
  ou resolver no próprio consolidator enquanto ele não existe.
- Declarar na resposta até onde a cobertura da fonte chega (~3 meses para FIIs,
  até ~5 anos para ações, dependendo do plano) — nunca preencher o buraco com
  zero.

### Outros

- **6.3.2 do plano do front — posições zeradas fora do Portfólio.**
  ✅ Implementado em 2026-11-04 (`hasOpenPosition` em `ConsolidationService`),
  aguardando revisão.
- `GET /wallet/{id}` continua devolvendo o ativo zerado de propósito: a lista de
  Ativos o esconde no front e o histórico/resultado dependem dele.
