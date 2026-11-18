> **Histórico, arquivado em 2026-11-17.** Origem: `SESSION_PLAN.md`.
> Substituído por: specs/ e ClickUp (pasta MyWallet)
> Conteúdo original abaixo, sem edição.

# Plano de Continuação - MyWallet (Consolidator + Visualizer)

> **Instrução importante:** Este arquivo serve como contexto e planejamento para a próxima sessão.
> **Atualizado em 2026-10-06.** As Etapas 1 a 4 (loop infinito, Fase D, Fase E, Phase 5 do
> front) estão **concluídas**. As seções 2 a 5 abaixo são mantidas como histórico e como
> referência de critérios de regressão — não são trabalho pendente.
> **Fase J concluída** (backend): o pendente agora é o **módulo de análise do front**
> (`features/analysis/`, seção 7 item 7), que depende de 0, H, I e J — todas concluídas.
> Consulte `consolidator/consolidator/BACKEND_ROADMAP.md` (backend) e
> `visualizer/IMPLEMENTATION_PLAN.md` (frontend) para manter consistência.

## 1. Estado Atual

### Backend (Consolidator)
- **Fases A–E concluídas.** Ledger determinístico, preço de aquisição vindo do ledger, carteira derivada, Bean Validation com status HTTP correto (400/403/404) e checagem de propriedade no service layer.
- Suite com **243 testes passando**, `./mvnw clean install` verde.
- A leitura de transação com ownership foi corrigida: `findById(id)` sem e-mail virava `TransactionService.findOwnedById(id, userEmail)`, e o recurso delegou a ele. Não existe mais método público de leitura sem autorização.
- **Fase I concluida:** valor justo persistido por usuário e por método (`V3__asset_valuations.sql` + `AssetValuation` com histórico). Fallback do Graham corrigido (sem PE/EPS, `fairValue` null em vez de preço de mercado) e os `System.out.println` de upside removidos. `ValuationResource` (`POST`/`GET /assets/{id}/valuations`), Graham com PE/EPS do mercado + override, Bazin com os `DividendReceipt` dos 12 meses (target 6% editável) e DCF integral manual com faixa de sensibilidade (D11). Dados insuficientes = 400 com motivo. +28 testes (212 no total). **Pendente:** validação das migrations V1–V3 em PostgreSQL real (sem Docker neste ambiente).
- **Fase H concluida:** proventos em entidade própria (`V2__dividend_receipts.sql` + `DividendReceipt`), sem tocar `TransactionType` nem `AssetPositionCalculator`. `getDividends` na Brapi (403 → "indisponível", dedup por ativo+data+valor), lançamento manual, listagem por ativo/carteira com filtro de ano, agregado por ano e `DELETE` de manual.
- **Fase 0 (Flashback do bloqueador de produção) — resolvida:** o schema virou responsabilidade do Flyway nos dois ambientes. Dev e teste saíram de `ddl-auto=update`/`create-drop` e passaram a usar a `V1__baseline.sql` com `validate`; prod ganhou as propriedades de baseline (`baseline-on-migrate`, `baseline-version=1`). `docker compose up` sobe agora com o volume `postgres_data` vazio. A validação em PostgreSQL real continua pendente: não há Docker neste ambiente, e os enums nativos (`CREATE TYPE`) são o único trecho que o H2 não prova de forma idêntica.
- **Fase G concluida:** `POST /auth/login` devolve `{ token, user }` com id, e-mail, nome e role reais; o workaround `userFromToken()` foi removido do front. No caminho, 401 e 403 deixaram de ser o mesmo status — o backend agora responde **401** para token ausente/invalido e **403** para autenticado-sem-permissao, e o front desloga so no 401. Antes, um 403 de ownership derrubava a sessao de quem estava autenticado e legitimo.
- **Fase J concluída:** evolução patrimonial. Reconstrução do ledger até a data
  de corte (`findByAssetIdAndTransactionDateLessThanEqualOrderBy...` + replay por
  dia do `AssetPositionCalculator`) multiplicada pelo fechamento histórico da
  Brapi (`getHistoricalPrices`, v1, `range=3mo` p/ FII e `5y` p/ o resto) +
  snapshots diários (`V4__portfolio_snapshots.sql`, `@EnableScheduling`, job
  `0 30 18 * * MON-FRI` em `America/Sao_Paulo` e backfill upsert). D13
  materializado: a resposta declara o que não reconstruiu (`warnings` +
  `points[].missingTickers`/`complete`) em vez de truncar. `GET/POST
  /wallet/{id}/history` e `/history/snapshots`. Código em
  `PortfolioHistoryService`/`PortfolioSnapshotService`/`PortfolioHistoryResource`.
- **Próximas fases:** módulo de análise do front (`features/analysis/`, item 7
  da seção 7), com gráficos de proventos e de evolução patrimonial
  (`ngx-charts@25.0.2`).

### Frontend (Visualizer)
- **Contratos alinhados com backend.** Build limpo, `npx ng test --watch=false` com **19/19 testes** verdes.
- **Loop infinito corrigido na raiz.** `effect()` foi movido de `ngOnInit` para o construtor em `AssetList`, `WalletTransactionList` e `TransactionList`, com guard `lastLoadedId`/`lastLoadedContext`. O sintoma real era `NG0203`: escrita em signal dentro do `ngOnInit`, que roda fora do contexto de injeção. `asset-list.spec.ts` cobre a regressão e comprova exatamente **1** `GET /assets` por abertura de carteira.
- `WalletService` compartilha `all$` com `shareReplay({ bufferSize: 1, refCount: false })` e `invalidate()` após mutações.
- **Phase 5 concluída:** `/portfolio` com cartões, totais, detalhe, alocação em CSS puro e tabela de P&L; dashboard lendo `GET /wallet/{walletId}/summary`.
- **Página em branco com `NG0201`** foi diagnosticada como cache Vite/Angular obsoleto, não bug: limpar `.angular/cache` e reiniciar resolveu. Se reaparecer, suspecte do cache antes do código.
- **Lockout de autenticação corrigido (2026-10-05).** Com token velho no `localStorage`, o cadastro respondia 403 e não dava para nem criar conta nem entrar. Causa dupla: o `JwtAuthFilter` chamava `loadUserByUsername` antes de validar a assinatura, derrubando a requisição em rota `permitAll`; e o front anexava token a tudo sem limpar a sessão no 403. Detalhes em `BACKEND_ROADMAP.md`, seção "Falha corrigida — travao de autenticacao".

### Ambiente de dev (importante)

O `spring-boot-devtools` está no `pom.xml` com escopo `runtime`. **Editar código
recarrega o contexto no mesmo JVM e apaga o H2 em memória.** Consequência prática:
contas e carteiras somem do nada ao mexer no código, e é normal. Para persistir
dados entre reinícios, subir com PostgreSQL em vez do H2.
- **Problema em aberto (PRIORITÁRIO): Loop infinito.** Nas abas "Ativos" e "Transações" do detalhe da carteira, o carregamento fica em loop infinito. O HAR mostrou **zero** chamadas `GET /assets?walletId={id}` para o backend, indicando que o `effect` está re-disparando repetidamente antes (ou impedindo) que a requisição HTTP seja feita.

## 2. Correção do Loop Infinito (Etapa 1) — ✅ CONCLUÍDO

A causa raiz mais provável é que o `effect` que dispara o carregamento é re-executado sempre que algum signal alterado pela própria carga (`assets`, `loading`, `errorMessage`) muda. Mesmo com `untracked()`, isso pode causar reavaliações. A solução é eliminar disparos redundantes com um **guard por ID/carregamento já realizado**.

### 2.1 AssetList (`src/app/features/assets/asset-list/asset-list.ts`)

1. Adicionar `private lastLoadedId = signal<string | null>(null)`.
2. No `effect` que dispara o carregamento, ler `override`/`routeId`, calcular `walletId`. **Só** chamar `loadAssetsFor(walletId)` se `walletId !== lastLoadedId()`.
3. Dentro de `untracked()`, setar `this.lastLoadedId.set(walletId)` **no momento da decisão de carregar** (idealmente antes de chamar `loadAssetsFor(walletId)`), para evitar corridas entre reavaliações do `effect`.
4. Utilizar a função `loadAssetsFor(walletId: string)` já extraída, garantindo que não leia signals desnecessários que poderiam re-trigar o `effect` de disparo.

### 2.2 WalletTransactionList (`src/app/features/transactions/transaction-list/wallet-transaction-list.ts`)

1. Adicionar um guard semelhante: rastrear `lastWalletId` e/ou uma chave baseada em `assetsInput()` (ex.: `walletId|assetIds` concatenados). **Só** recarregar quando o contexto mudar de fato.
2. Evitar setar `loading.set(false)` prematuramente quando `assets.length === 0`. Isso causa um "estado falso de vazio" enquanto o pai ainda carrega. Ao invés disso: só dispara carga quando há ativos **ou** quando `walletIdInput()` muda, e só marca como carregado após a requisição completar (inclusive no caso de retorno com array vazio pelo backend).

### 2.3 Otimização de chamadas de carteiras

- Em `WalletService.getAll()`, retornar o observable com `shareReplay(1)` (com gerenciamento adequado de subscrição) para que múltiplos componentes (`Dashboard`, `WalletList`, `AssetList`) compartilhem a mesma resposta. Isso reduz GETs recorrentes que podem contribuir com o loop em cadeia.

### Critério de Aceite (Loop Corrigido)
- Ao abrir o detalhe da carteira com ativos, aparece **exatamente 1** `GET /assets?walletId={id}` no HAR (não zero, nem múltiplos).
- A aba "Ativos" carrega e exibe os ativos criados, **sem** ficar em spinner infinito.
- A aba "Transações" carrega uma única vez por troca de contexto, sem flicker infinito.
- O Dashboard continua mostrando os totais reais.
- Build do frontend (`ng build --configuration development`) sem erros.

## 3. Backend - Fase D (Validação/Status HTTP Consistentes) - Etapa 2 — ✅ CONCLUÍDO

Após estabilizar o frontend, **continue** com a Fase D. Consulte o `BACKEND_ROADMAP.md` para manter alinhamento com as decisões já documentadas.

### 3.1 Auditoria e Padronização
- **Controllers:** Revisar `AssetResource`, `WalletResource`, `TransactionResource`, `AuthResource` para padronizar códigos HTTP (400 em validação, 404 quando não encontrado, 403 quando sem permissão, 422 quando aplicável).
- **Exception Handling:** Verificar `@ControllerAdvice`/`GlobalExceptionHandler` existente. Padronizar payload de erro (mensagens claras, sem vazar stack traces desnecessariamente em dev/prod).
- **Contratos e Validações:** Revisar DTOs com anotações de validação. Garantir que campos desconhecidos sejam rejeitados onde já foi decidido (ex.: `AssetUpdateDTO` com `@JsonAnySetter` rejeitando campos não editáveis).

### 3.2 Testes
- Ajustar/expandir testes de controller para cobrir casos de status HTTP (regressões esperadas).
- Manter comportamento existente sempre que não conflitar com as decisões do roadmap.

### 3.3 Documentação
- Atualizar `BACKEND_ROADMAP.md` com as mudanças da Fase D, critérios de aceite e decisões tomadas.

## 4. Backend - Fase E (Propriedade/Autorização) - Etapa 3 — ✅ CONCLUÍDO

**Continue** com a Fase E após concluir a Fase D. Consulte `BACKEND_ROADMAP.md`.

### 4.1 Escopo por Usuário
- Garantir que `Wallet`, `Asset`, `Transaction` sejam acessados **apenas** pelo dono/autorizado.
- Implementar checagens na **camada de Service** (domínio) para evitar vazamento de recursos por ID.

### 4.2 Restrição de Acesso a Assets
- Revisar `GET /assets`. Atualmente aceita `walletId` opcional. **Ajustar para não expor todos os ativos globalmente.** Exigir `walletId` válido pertencente ao usuário autenticado **OU** retornar apenas ativos do escopo do usuário logado.

### 4.3 Proteção de Mutações
- POST/PUT/DELETE devem validar propriedade. Para recursos não pertencentes ao usuário: **retornar 404 Not Found** por padrão (para não vazar existência). Reservar **403 Forbidden** para o caso em que o usuário está autenticado, mas não possui permissão explícita para aquele recurso (distinção de casos).
- Esta abordagem prioriza _security through obscurity_ no caso de enumeração de IDs.

### 4.4 Testes
- Adicionar casos negativos (acesso cross-user) e positivos (acesso ao próprio recurso).
- Garantir que os testes existentes continuam verdes (109 testes base). Rodar suíte completa após alterações.

### 4.5 Documentação
- Atualizar `BACKEND_ROADMAP.md` com Fase E concluída, decisões de autorização/status HTTP adotadas e eventuais pendências.

## 5. Frontend - Consolidação (Linha da Phase 5) - Etapa 4 — ✅ CONCLUÍDO

Após estabilizar loop + concluir D/E no backend (ou em paralelo conforme apropriado), **continue** com a evolução do frontend, alinhado com `IMPLEMENTATION_PLAN.md`.

### 5.1 Dashboard - P&L Real
- Calcular **Total P&L** real no Dashboard, utilizando carteiras + ativos + preços atuais (via `ConsolidationService`/`summary` quando disponível). Atualmente está fixado em `R$ 0,00`.

### 5.2 Portfolio/Summary
- Aproveitar `GET /wallet/{id}/summary` (já existente no backend) para enriquecer a tela de Portfólio e o Dashboard, evitando múltiplos GETs por ativo.

### 5.3 Otimizações
- Com `shareReplay(1)` e os guards implementados, revisar listagens para evitar requisições redundantes entre navegações.
- Refinamentos de UX (estados vazios, mensagens de erro) coerentes com o novo comportamento.

## 6. Requisitos Gerais (Importantes)

- **Backend:** Nunca pular testes. Rodar `./mvnw clean install` com `JAVA_HOME` configurado corretamente (`C:/Program Files/Java/jdk-17` no ambiente Windows). Baseline atual: **212 testes** (front: 19).
- **Frontend:** Garantir build limpo (`ng build --configuration development`) antes de testar na UI. Testar com HAR para validar o número de requisições HTTP (critério de 1 GET `/assets?walletId` por abertura de carteira).
- **Documentação:** Atualizar `BACKEND_ROADMAP.md` e `IMPLEMENTATION_PLAN.md` conforme avança com as implementações. Mantenha-os sincronizados com o que foi feito.
- **Commits:** **NUNCA** commitar alterações automaticamente. Somente commitar quando **explicitamente solicitado** pelo usuário (conforme instruções do projeto).
- **Siga as convenções:** Mimicar estilo de código existente, não adicionar comentários desnecessários, seguir boas práticas de segurança (nunca commitar secrets/keys).

## 7. Ordem de Execução Recomendada

As Etapas 1 a 4 da seção anterior estão concluídas. O que sigue, em ordem:

1. **[FEITA]** **Fase F** — `GET /transactions?walletId=` elimina o N+1 do
   ledger. Concluída em 2026-10-05, +11 testes (139 no total). O
   `WalletTransactionList` trocou o `forkJoin` por uma requisição só, e o
   `catchError` que convertia falha de rede em tabela vazia sem aviso foi
   removido: "carteira sem transações" continua significando carteira sem
   transações.
2. **[FEITA]** **Fase G** — `LoginResponseDTO` passou a devolver `user` com id,
   e-mail, nome e role. O front grava o usuario da resposta e
   `userFromToken()`/`decodeToken()` sumiram. O `UserResponseDTO` ganhou `role`
   porque o `AdminGuard` e a sidebar dependem dela. O `AuthController` busca a
   entidade `User` (o `UserDetails` nao tem id nem nome). Concluida em
   2026-10-05, +10 testes (149 no total), mais 12 no front.
   **Correlatos:** 401 e 403 foram separados no `SecurityConfig`, e o
   `JwtInterceptor` passou a tratar `/users` por metodo (so o POST e publico —
   o GET e listagem de ADMIN e estava perdendo o token).
3. **[FEITA]** **Fase 0** — schema versionado com Flyway. `V1__baseline.sql`
   unica (sem split `common`/`vendor`, usando `BIGINT GENERATED BY DEFAULT AS
   IDENTITY`, `DOUBLE PRECISION` e enums nativos via `CREATE TYPE`), o dev e o
   teste saíram de `ddl-auto=update`/`create-drop` para `validate` com a
   migration como única criadora de schema, e `prod` ganhou
   `baseline-on-migrate` com `baseline-version=1`. Concluida em 2026-10-06,
   +3 testes (152 no total, `FlywayBaselineTest`). **Pendente:** validar em
   PostgreSQL real (sem Docker neste ambiente — enums nativos são o único trecho
   que o H2 nao prova de forma identica).
4. **[FEITA]** **Fase H** — proventos. `DividendReceipt` como entidade
   separada (`V2__dividend_receipts.sql`), sem tocar `TransactionType` nem
   `AssetPositionCalculator`. `BrapiAdapter.getDividends` traduz o 403 dos FIIs
   em "indisponível" (D12) e o sync grava com dedup por ativo+data+valor.
   Endpoints: `POST /dividends` (manual) · `GET /dividends?assetId|walletId&year`
   · `GET /dividends/summary?walletId` · `POST /dividends/sync/{assetId}` ·
   `DELETE /dividends/{id}` (só manual). `deleteAsset` limpa dividendos antes de
   apagar o ativo. Concluída em 2026-10-06, +32 testes (184 no total).
   **Pendente:** validação em PostgreSQL real (sem Docker neste ambiente).
5. **[FEITA]** **Fase I** — valor justo por usuário. `V3__asset_valuations.sql`
   + `AssetValuation` com histórico (nunca sobrescreve). Fallback do Graham
   corrigido (sem PE/EPS, `fairValue` null) e `System.out.println` de upside
   removidos. `ValuationResource`: `POST`/`GET /assets/{id}/valuations` —
   Graham com PE/EPS do mercado (+ override), Bazin com os `DividendReceipt`
   dos 12 meses (target 6% editável) e DCF integral manual; resultado sempre
   como faixa de sensibilidade (D11) e dados insuficientes = 400 com motivo.
   Concluída em 2026-10-06, +28 testes (212 no total). **Pendente:** validação
   em PostgreSQL real (sem Docker neste ambiente).
6. **[FEITA]** **Fase J** — evolução patrimonial. Reconstrução pelo ledger mais
   snapshot diário. `findByAssetIdAndTransactionDateLessThanEqualOrderBy...` +
   `AssetPositionCalculator.calculateByDate`; `BrapiAdapter.getHistoricalPrices`
   (v1, `range=3mo` p/ FII e `5y` p/ o resto); `PortfolioHistoryService` com D13
   declarado; `V4__portfolio_snapshots.sql` + `PortfolioSnapshot` (upsert por
   carteira+data) com `@EnableScheduling` na aplicação e job
   `@Scheduled(cron="0 30 18 * * MON-FRI", zone="America/Sao_Paulo")`; endpoints
   `GET/POST /wallet/{id}/history` e `/history/snapshots`. Concluída em
   2026-10-06, +31 testes (243 no total). **Pendente:** validação em PostgreSQL
   real (sem Docker neste ambiente).
7. **[SEGUINTE]** **Front: módulo de análise** (`features/analysis/`). Gráficos de
   proventos e de evolução patrimonial consumindo `GET /dividends` e
   `GET /wallet/{id}/history`; `ngx-charts@25.0.2` (suporta Angular 22).

Cada fase só começa com a anterior verde.

### Módulo de análise do front (depende de 0, H, I e J)

`features/analysis/` com gráficos de proventos e de evolução patrimonial, usando
`ngx-charts@25.0.2` (suporta Angular 22). O DCF entra com padrões **editáveis**:
todo valor pré-preenchido aparece marcado como premissa, a fórmula fica visível e
o resultado sai como faixa de sensibilidade — nunca como número único com
aparência de verdade.

### Restrições conhecidas da Brapi (medidas em 2026-10-05, plano gratuito)

| Recurso | Ações | FIIs |
|---|---|---|
| Preço, P/E, EPS | sim | sim |
| Dividendos | sim (desde 2001) | **403 — exige plano Startup** |
| Série histórica | até `5y` | **só até `3mo`** |

Detalhes: parte dos registros vem **sem `paymentDate`** (de 176 do PETR4 só 121
servem); `assetIssued` vem como ISIN (`BRPETRACNPR6`), não como ticker; não
existe endpoint dedicado de dividendos. H e J **servem do banco**, nunca chamam a
Brapi por render.

**Não pare ao concluir a Fase 0.** Continue para a Fase H e siga a sequência,
conforme este planejamento.
