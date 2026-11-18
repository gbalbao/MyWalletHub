# Estado do projeto MyWallet — auditoria de 2026-11-15

Fonte: leitura do código dos três serviços e de todos os arquivos de planejamento (.md/.html, incluindo `.opencode/plans` e planos soltos em `Projetos\`). O código manda: plano que diverge dele conta como problema. Nada foi executado além de `ruff` e da coleta do pytest no ADC; a suíte do ADC não terminou (Postgres de teste fora do ar), e o comportamento em runtime (Jackson, springdoc, docker compose) não foi testado.

## 1. Resumo executivo
- **Consolidator**: funcionalmente maduro (ledger por replay, consolidação, proventos, valuation, histórico, volatilidade; 337 testes). Problemas de segurança que nenhum plano registra: `PUT/DELETE /users/{id}` sem checagem de dono e `DELETE /wallet/{id}` com ativos provavelmente viola FK. Roda localmente na 8080; a conteinerização (compose incompleto, health check 401) nunca foi usada e fica como pendência de integração, não como defeito.
- **Visualizer**: Phases 2–6 e 8 entregues (26 specs, 170 testes). Build de produção aponta para `localhost:8080` (falta `fileReplacements`), `npm run lint` não existe de fato, link ADMIN "Usuários" leva a lugar nenhum. Phase 7 (Docker, CI, E2E) não começou.
- **ADC**: importador de planilha e coletor Fundamentus prontos (89 testes, ruff limpo). API FastAPI, COTAHIST/`/v1/prices`, CVM, agendamento: não feitos. Validação com a planilha real (7.7) pendente.
- **Contratos**: `contracts/` e `specs/` vazios. Não existe OpenAPI; a fonte de verdade de fato são os DTOs Java. Há uma quebra de precificação (`AssetResponseDTO.currentValue` congelado) e uma divergência de formato de data no ADC.
- **Documentação**: 15 arquivos de plano espalhados, quatro numerações de fase diferentes, vários obsoletos e um com conteúdo malicioso (§3.4).

## 2. O que está implementado (por serviço e fase)

### 2.1 Consolidator (`../consolidator/consolidator`)
| Fase (plano) | Status real | Observação |
|---|---|---|
| 0 Limpeza (`implementation_plan.html`) | Implementado | |
| 1 JWT | Implementado | Login devolve `{token, user}` (plano dizia só token) |
| 2 Transações | Implementado, desenho diferente | `assetId` em vez de `assetTicker`; replay do ledger em vez de atualização incremental; `assetType` nunca é preenchido |
| 3 Consolidação | Implementado; degradação parcial | Falha da Brapi em `getAssetData` vira 400 |
| 4 Testes e polimento | Implementado, exceto `@WebMvcTest` (usa `@SpringBootTest`) e teste de `getAssetData` | Swagger: springdoc 2.5.0 sem config, rotas bloqueadas, provável incompatibilidade com Boot 3.5.6 |
| 5 Persistência/Docker | Parcial | Flyway V1–V4 e `ddl-auto=validate` ok; conteinerização nunca usada: compose incompleto (sem `BRAPI_TOKEN`, volume, ports, depends_on) e health 401; sem `logback-spring.xml`; nunca validado em PostgreSQL real |
| 6.1 pgAdmin | Não feito | |
| Roadmap A–G (ledger, preço de aquisição, carteira derivada, erros, propriedade, ledger por carteira, login) | Implementado | Propriedade não cobre `/users` |
| Roadmap 0 (Flyway), H (proventos), I (valor justo), K (volatilidade) | Implementado | H mudou contrato (escopo all-wallets, sync por id ou ticker) |
| Roadmap J (evolução patrimonial) | Implementado / parcial | Regra "FII usa 3mo" nunca dispara (sem `assetType`) |
| 6.3 / 6.3.2 / 6.3.3 / 6.6 | Implementado | Restam `ZoneId.systemDefault()` em `PortfolioSnapshotService:44`, `DividendService:338/363/373`, `ValuationService:126` |
| 6.7.3 fechamentos via ADC | Não feito (bloqueado pelo ADC) | |

### 2.2 Visualizer (`../visualizer/visualizer`)
| Fase (`IMPLEMENTATION_PLAN.md`) | Status real | Observação |
|---|---|---|
| 2 Carteiras | Implementado | Models seguem o backend, não o plano |
| 3 Ativos | Implementado; `/assets/:id` não feito (absorvido por `/transactions?assetId=`) | |
| 4 Transações | Implementado | `fees` e toggle BUY/SELL obsoletos (virou `sell-form`) |
| 5 Portfólio | Implementado | Alocação em barras (plano diz conic-gradient); P&L waterfall e `lastUpdated` não feitos |
| 6.1 Polish | Parcial | Spinners de botão sem `role="status"`; mensagens do `ErrorInterceptor` em inglês; link ADMIN quebrado |
| 6.2–6.7.2 | Implementado | Todas as carteiras, resultado realizado, filtro de período, isenção mensal, datas, volatilidade |
| 7 Deploy/Tooling | Só Vitest | Sem cobertura mínima, Playwright, CI, Dockerfile/nginx, ESLint |
| 8 Análise | Implementado | Cabeçalho do plano ainda diz "em andamento" |
| Bug fora do plano | Build prod usa `environment.ts` (`angular.json:37-50` sem `fileReplacements`) | |

### 2.3 ADC (`../adc`)
| Fase (`../ADC_PLAN.md`) | Status real |
|---|---|
| 0 Descoberta, 1 Scaffolding | Implementado |
| 2 Modelagem | Implementado com divergências: sem `source_aliases`, `formula_version`, `period_start`, `fiscal_year`, `is_fixed`; §17 ainda usa `company_id` (D27 mudou para `ticker_id`) |
| 3 Fundamentus | Implementado (detalhes, proventos, cache, rate limit, raw docs, upserts); `resultados_trimestrais` e agendamento não feitos; `discovery.py` substituído por `--tickers/--wallet-id` |
| 4 CVM DFC, 5 Agregações, 6 FastAPI | Não feito |
| 7 Importador | Código implementado; 7.7 (planilha real) e 7.8 (documentar `POST /import/ledger`) não feitos |
| 8 Agendamento/hardening, 9 Cliente no Consolidator, 10 COTAHIST e `/v1/prices` | Não feito (tabela `daily_close` existe e está vazia) |

## 3. Arquivos de planejamento: duplicados, conflitantes e obsoletos

### 3.1 Inventário
| Arquivo | Serviço | Estado |
|---|---|---|
| `consolidator/implementation_plan.html` | Consolidator | Obsoleto (retrato de julho); duplica o `.opencode` |
| `consolidator/.opencode/plans/implementation_plan.md` | Consolidator | Mais fiel ao código; item 6.7 (`daily_close` aqui) conflita com o roadmap |
| `consolidator/AGENTS.md` | Consolidator | Seção de estado obsoleta ("Phase 4 next", `ddl-auto=update`, "one test") |
| `consolidator/consolidator/BACKEND_ROADMAP.md` | Consolidator | Roadmap principal (A–K, D1–D13); vigente, com pontos obsoletos (D5, F, H, J) |
| `consolidator/consolidator/E2E_Auth_Fixes.md` | Consolidator | Obsoleto: diz "tudo pendente", 8 de 10 feitos; restam #3 (NPE `assets` nulo) e #10 (`@EnableMethodSecurity`) |
| `consolidator/consolidator/ENHANCEMENTS.md` | Consolidator | Backlog Brapi vigente; #1 parcial, #2–#6 não feitos; linhas citadas desatualizadas |
| `visualizer/IMPLEMENTATION_PLAN.md` | Visualizer | Plano vivo; vários trechos obsoletos (date picker nativo, conic-gradient, 403 desloga, `/portfolio/history`, status Phase 8) |
| `visualizer/frontend-plan.md` | Visualizer | Histórico declarado (Jest, Angular 18, config runtime) |
| `visualizer/frontend-plan.html` | Visualizer | Duplica o `.md` sem o aviso de histórico |
| `Projetos/ADC_PLAN.md` | ADC | Plano mestre, fora do git; §14, §15, §17, D20 e §25 desatualizadas; §5 com formato de data antigo |
| `Projetos/SESSION_PLAN.md` | Consolidator + Visualizer | Retrato de 2026-10-06, superado |
| `Projetos/PROMPT_NOVA_SESSAO.txt` | MyWallet | Excluído em 2026-11-15 (§3.4) |
| `consolidator/.gitignore` | — | `*.md` ignorado: só 3 dos `.md` do Consolidator estão versionados |

Fora do escopo: `HELP.md`s padrão do Spring, `README.md`s de boilerplate, `CLAUDE.md`s (regras, não planos; o do ADC não está versionado).

### 3.2 Numerações de fase sobrepostas
Fase 0 = limpeza no `.html` e Flyway no roadmap; letras A–K no roadmap; 6.x vindo do plano do front e citada no código do backend; fases 0–10 do ADC. Nenhuma referência cruzada entre elas.

### 3.3 Conflitos diretos
- `daily_close`: `.opencode` manda criar no Consolidator; roadmap e ADC_PLAN delegam ao ADC (o ADC já tem a tabela).
- Status do Consolidator: `AGENTS.md` (Fase 4 próxima) contra roadmap (K concluída).
- Ambiente do front: `frontend-plan` (runtime) contra `IMPLEMENTATION_PLAN` (build-time).
- ADC: D20 (banco só depois da 7.7) violada pela ordem nova adotada.

### 3.4 Alerta de segurança
`Projetos/PROMPT_NOVA_SESSAO.txt` contém um bloco falso de `system-reminder` dizendo que o modo read-only acabou. Serve para enganar um agente e fazê-lo escrever arquivos. Os agentes da auditoria ignoraram. O arquivo era um prompt antigo para abrir sessões no opencode e foi excluído a pedido do usuário em 2026-11-15.

## 4. Planejado e ainda não feito (priorizado)

**P0 — contrato e segurança**
1. OpenAPI do Consolidator em `contracts/` (próxima feature, via `/new-spec`).
2. Consolidator: checagem de dono em `PUT/DELETE /users/{id}` (ou só ADMIN) e `@EnableMethodSecurity`.
3. Consolidator: `DELETE /wallet/{id}` com ativos (cascata ou 4xx explícito).
4. Visualizer: `fileReplacements` no build de produção.

**P1 — bugs e correções de contrato**
5. `AssetResponseDTO.currentValue` congelado usado como cotação no front (ver §5).
6. Dashboard e `sumPortfolioTotals` calculando P&L local com `totalInvested` cheio.
7. ADC enviar datas como `yyyy-MM-dd`.
8. Consolidator: falha da Brapi como aviso por ativo e 502/503 (ENHANCEMENTS #1); NPE `assets` nulo; preencher `assetType`; trocar `ZoneId.systemDefault()` restantes.
9. Visualizer: link ADMIN "Usuários" (rota com `AdminGuard` + `GET /users`, ou remover); ESLint e target `lint`.

**P2 — entrega planejada**
10. ADC: 7.7 com a planilha real.
11. ADC: FastAPI (Fase 6), depois COTAHIST e `/v1/prices` (Fase 10), depois cliente no Consolidator (Fase 9).
12. Consolidator: conteinerização para integrar os três serviços (completar `docker-compose.yml`, liberar `/actuator/health`), validação em PostgreSQL real, `logback-spring.xml`, springdoc 2.8.x funcional, CORS por propriedade, migration de `total_invested_value`.
13. Visualizer: Phase 7 (Docker/nginx alinhado sem prefixo `/api`, CI, Playwright, cobertura); fechar 6.1 (a11y e textos em português).

**P3 — otimizações e opcionais**
14. Brapi: cache TTL, timeout, base-url configurável, semáforo, métricas.
15. ADC: Fase 8, `resultados_trimestrais`, CVM (Fase 4), agregações (Fase 5).
16. Front: P&L por ativo, `MatSort`/paginator, transaction-detail; remover `asset-list.ts.bak2` e `HistoryService.getSnapshots` sem uso.

## 5. Divergências de contrato

`contracts/` vazio: não há OpenAPI. Tipos: `Double` (Java) ↔ `number` (TS) ↔ `float` (ADC); nomes batem nos DTOs principais.

| # | Severidade | Divergência | Evidência |
|---|---|---|---|
| C1 | Quebra | `AssetResponseDTO.currentValue` é preço gravado no cadastro e nunca atualizado; o front usa como cotação para P&L e potencial de valuation. O mesmo nome é valor da posição em `AssetSummaryDTO` | `Asset.java:30`, `AssetService.java:95,256`; `asset-list.ts:154-159`, `fair-value.ts:125,137` |
| C2 | Risco alto | Dashboard e `sumPortfolioTotals` calculam P&L no front incluindo ativos sem cotação no investido ("prejuízo inventado"); o backend já resolve com `pricedInvested` | `dashboard.ts:238-239`, `portfolio.models.ts:131-141` |
| C3 | Risco | ADC envia `transactionDate`/`acquisitionDate` como `...T00:00:00.000Z`; Consolidator espera `LocalDate` (`yyyy-MM-dd`). Funciona só pela leniência do Jackson, sem teste E2E | `adc/core/utils.py:192`, `adc/apps/importer/client.py:97`; `TransactionDTO.java:12-28` |
| C4 | Risco | Percentuais em 0–100, volatilidade em fração 0–1; nada documentado | `ConsolidationService:245`, `analysis-overview.ts:380` |
| C5 | Risco | `fairValue` do ativo (Graham do cadastro, envelhece, fórmula `PE*EPS`) diverge do `ValuationService` | `AssetService.java:215`, `ValuationService.java:98-112` |
| C6 | Risco | `computedAt`, `paymentDate`, `exDate` como `java.util.Date`; resto da API em `LocalDate`; front usa `new Date(iso)`, o que pode mostrar um dia antes | `ValuationResponseDTO`, `DividendReceiptResponseDTO`; `fair-value.ts:316` |
| C7 | Risco | Moeda e data da cotação não chegam ao front (BRL fixo) | `AssetDataDTO` (Brapi) não exposto |
| C8 | Risco | Contratos de rota mudaram sem registro: proventos all-wallets e sync por ticker, `/transactions` sem filtro = todas do usuário, `POST /wallet/{id}/assets/merge` fora de qualquer plano | `DividendResource.java:68-87`, `TransactionResource.java:121-127` |
| C9 | Risco | Nginx planejado faz proxy de `/api`, mas o front chama rotas sem prefixo | `visualizer/IMPLEMENTATION_PLAN.md:981-985` |
| C10 | Cosmético | `walletId` é `string` em `AssetCreateDTO` e `Long` no resto; `totalInvestedValue` opcional no TS mas sempre presente; nullability do TS mais frouxa que a do Java | `AssetCreateDTO.java:28`, `wallet.models.ts:7` |
| C11 | Pendente nos dois lados | `/v1/prices` (ADC → Consolidator) dado como "congelado" nos planos, sem implementação em nenhum lado | `ADC_PLAN.md §26`, `BACKEND_ROADMAP.md:1114-1131` |

Rotas existentes não consumidas: `GET/PUT/DELETE /users*` e `POST /wallet/{id}/history/backfill` (front); `GET /wallet/{id}/history/snapshots` é chamado pelo serviço do front mas nenhuma tela usa.

## 6. Proposta de consolidação

Regra: `specs/` guarda o quê e o porquê de uma feature; `contracts/` guarda a API; `docs/adr/` guarda decisões; ClickUp guarda andamento e backlog; repositórios de serviço guardam só `CLAUDE.md`/`README.md` operacionais.

| Item | Ação | Destino |
|---|---|---|
| OpenAPI do Consolidator | Criar (gerado via springdoc 2.8.x, revisado à mão), com unidades (percentual 0–100, volatilidade fração, BRL, datas `yyyy-MM-dd`) e semântica de null | `contracts/consolidator.openapi.yaml` |
| Contrato `/v1/prices` (ADC_PLAN §26) e payloads do importador (§5, corrigido) | Extrair | `contracts/adc-prices.openapi.yaml`, `contracts/` (importer usa o OpenAPI do Consolidator) |
| `BACKEND_ROADMAP.md` decisões D1–D13 | Mesclar as que seguem válidas | `docs/adr/` (uma por decisão relevante) |
| `ADC_PLAN.md` decisões D1–D31 | Mesclar, removendo redundantes (D16, D17) e obsoletas (D20) | `docs/adr/` |
| Fases não feitas (ADC 6, 8, 9, 10; Visualizer 7; Consolidator 5/Brapi) | Uma spec por feature | `specs/NNN-*.md` |
| Pendências P0–P3 da §4 | Viram cards | ClickUp (depois das specs) |
| `ENHANCEMENTS.md`, itens abertos de `E2E_Auth_Fixes.md` | Mesclar como backlog | ClickUp; spec `specs/NNN-brapi-resiliencia.md` |
| `visualizer/IMPLEMENTATION_PLAN.md`, `consolidator/.opencode/plans/implementation_plan.md`, `BACKEND_ROADMAP.md`, `ADC_PLAN.md` | Arquivar depois da extração (marcar "histórico", sem apagar) | `docs/archive/` no hub ou permanecer no repo com aviso |
| `implementation_plan.html`, `frontend-plan.md`, `frontend-plan.html`, `E2E_Auth_Fixes.md`, `SESSION_PLAN.md` | Arquivar já | `docs/archive/` |
| `AGENTS.md` do Consolidator | Reescrever só a parte operacional e remover o estado de fases | Repo do Consolidator |
| `PROMPT_NOVA_SESSAO.txt` | Excluído em 2026-11-15 | — |
| `consolidator/.gitignore` com `*.md` | Remover a regra ou versionar o que for operacional | Repo do Consolidator |

## 7. Decisões (2026-11-15)
1. **Onde vivem os planos**: tudo centralizado no hub (`specs/`, `contracts/`, `docs/adr/`, `docs/archive/`). Os repositórios de serviço ficam só com `CLAUDE.md`/`README.md` operacionais.
2. **Contrato**: o OpenAPI do Consolidator é a próxima feature, criada com `/new-spec` e implementada depois. A spec ainda não foi escrita.
3. **Prioridade**: começar pelo OpenAPI e pela correção de segurança (§4, P0). A conteinerização foi rebaixada para P2: o Consolidator roda localmente e nunca foi conteinerizado.
