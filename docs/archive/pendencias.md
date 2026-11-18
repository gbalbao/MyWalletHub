# Pendências dos planos arquivados

Levantamento feito em 2026-11-17 (spec 003) a partir dos 10 planos em `docs/archive/` e da auditoria `docs/estado-do-projeto.md`. Cada pendência aberta aparece aqui em um de três destinos:
- uma spec do backlog (`docs/backlog-proposto.md`);
- "sem spec": vira card avulso no ClickUp;
- descartada, com o motivo.

## 1. Cobertas por spec do backlog

| Pendência | Plano de origem | Spec |
|---|---|---|
| Swagger/springdoc funcional; contrato OpenAPI | `.opencode` Fase 4 | 001 |
| `PUT/DELETE /users/{id}` sem checagem de dono | auditoria | 002 |
| NPE em `POST /wallet` com `assets` nulo (E2E #3) | E2E_Auth_Fixes | 002 |
| `@PreAuthorize` sem `@EnableMethodSecurity` (E2E #10) | E2E_Auth_Fixes | 002 |
| `DELETE /wallet/{id}` com ativos | auditoria | 002 |
| `Asset.currentValue` com semântica de preço unitário (dívida D3) | BACKEND_ROADMAP | 004 |
| `fairValue` automático por Graham no cadastro | BACKEND_ROADMAP Fase I | 004 |
| `ZoneId.systemDefault()` restantes (6.6 não coberto) | `.opencode` 6.6 | 005 |
| Validação de data futura nos proventos (6.6.4) | visualizer IMPLEMENTATION_PLAN | 005 |
| `lastUpdated` da cotação no portfólio (Phase 5) | visualizer IMPLEMENTATION_PLAN | 006 |
| Falha da Brapi em `getAssetData` vira 400 (ENHANCEMENTS #1) | ENHANCEMENTS | 008 |
| Cache com TTL, `base-url` configurável, remover `priceCache` local (#2, #5) | ENHANCEMENTS | 008 |
| Semáforo, batching e métricas da Brapi (#3, #4, #6) | ENHANCEMENTS | 008 (avaliar) |
| N chamadas à Brapi ao criar carteira | BACKEND_ROADMAP (dívida) | 008 |
| Teste de `getAssetData` (4.4 parcial) | implementation_plan.html | 008 |
| `fileReplacements`, ESLint e target `lint` | visualizer IMPLEMENTATION_PLAN Phase 7 | 009 |
| Fechar 6.1: textos em português no `ErrorInterceptor`, `role="status"` nos spinners | visualizer IMPLEMENTATION_PLAN 6.1 | 009 |
| Administração de usuários para ADMIN (`GET /users`) | frontend-plan | 009 |
| `Asset.assetType` nunca preenchido (regra "FII usa 3mo") | BACKEND_ROADMAP Fase J | 010 |
| API FastAPI do ADC (Fase 6) | ADC_PLAN | 011 |
| COTAHIST, `/v1/prices` e cliente no Consolidator (Fases 9, 10; 6.7.3) | ADC_PLAN, `.opencode` 6.7 | 012 |
| Validação com a planilha real (7.7), documentar o importador (7.8), `auth.resolve_credentials` sem uso | ADC_PLAN | 013 |
| `docker-compose` incompleto, health 401, `logback-spring.xml` (5.6) | implementation_plan.html, `.opencode` Fase 5 | 014 |
| Validação das migrations V1–V4 em PostgreSQL real | SESSION_PLAN, BACKEND_ROADMAP | 014 |
| CORS por propriedade; migration de `total_invested_value` (Fase C) | E2E_Auth_Fixes #1, BACKEND_ROADMAP | 014 |
| Dockerfile e nginx do front, com o conflito do prefixo `/api` | visualizer IMPLEMENTATION_PLAN Phase 7 | 014 |
| CI, Playwright, limiar de cobertura (front) e meta de 80% (ADC) | visualizer Phase 7, ADC_PLAN §22 | 015 |
| Agendamento, lock de job, logs JSON (Fase 8); `resultados_trimestrais.php` | ADC_PLAN | 016 |
| CVM DFC (Fase 4), agregações (Fase 5), `source_aliases` e colunas da §17 (`formula_version`, `period_start`, `fiscal_year`, `is_fixed`) | ADC_PLAN | 017 |

## 2. Sem spec: viram cards avulsos

| Pendência | Origem | Serviços |
|---|---|---|
| Recuperação de senha e refresh token | visualizer IMPLEMENTATION_PLAN (Auth extras), frontend-plan | Consolidator, Visualizer |
| Expor `fairValue` no `PortfolioSummaryDTO` | BACKEND_ROADMAP (dívida) | Consolidator, Visualizer. Reavaliar depois da 004 |
| Gráfico de P&L por ativo ("waterfall") | visualizer IMPLEMENTATION_PLAN Phase 5 | Visualizer |
| `MatSort` e paginator nas tabelas | visualizer IMPLEMENTATION_PLAN (stack) | Visualizer |
| Tela de detalhe de transação (opcional) | visualizer IMPLEMENTATION_PLAN Phase 4 | Visualizer |
| Variação do dia da cotação (`regularMarketChange`), hoje não exposta | integration-reviewer | Consolidator, Visualizer |
| Total de proventos calculado em dois lugares (front e `/dividends/summary`) | integration-reviewer | Visualizer |
| `POST /import/ledger` dedicado (D8 do ADC) | ADC_PLAN | Consolidator, ADC. Só se o envio transação a transação ficar lento |
| Corretagem no custo médio | ADC_PLAN D10 (fora do MVP) | Consolidator, ADC, Visualizer |

## 3. Descartadas

| Pendência | Origem | Motivo |
|---|---|---|
| pgAdmin no compose (6.1) | implementation_plan.html | Conveniência de desenvolvimento, sem valor para o produto. Pode voltar na 014, se for útil |
| `@WebMvcTest` nos controllers (4.2) | implementation_plan.html | O projeto adotou `@SpringBootTest` com MockMvc (16 classes). Trocar não traz ganho |
| Tabela `daily_close` no Consolidator | `.opencode` 6.7 | Delegada ao ADC (ADR 012). A tabela já existe lá |
| Rota `/assets/:id` (asset-detail) | visualizer IMPLEMENTATION_PLAN Phase 3 | O fluxo foi absorvido por `/transactions?assetId=` |
| Campo `fees` e toggle BUY/SELL na transação | visualizer IMPLEMENTATION_PLAN Phase 4 | O backend não tem `fees`; o toggle virou o `sell-form`. A corretagem fica na lista "sem spec" |
| Jest, Angular 18 e configuração de ambiente em runtime | frontend-plan | Superados por Vitest, Angular 22 e configuração em build-time |
| `discovery.py` (descoberta automática de tickers) | ADC_PLAN Fase 3 | Substituído por `--tickers` e `--wallet-id` (§24.1 do plano) |
| D20: banco e API só depois da 7.7 | ADC_PLAN | A ordem foi invertida e o banco e o coletor já existem |
| `@PastOrPresent` no `TransactionDTO` | BACKEND_ROADMAP Fase D | Superado por `FUTURE_TRANSACTION_DATE` |
| "Aguardando revisão manual antes do commit" | `.opencode` | Os commits já entraram |
