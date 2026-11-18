> **Histórico, arquivado em 2026-11-17.** Origem: `visualizer/IMPLEMENTATION_PLAN.md`.
> Substituído por: specs do backlog (009, 015) e docs/archive/pendencias.md
> Conteúdo original abaixo, sem edição.

# Visualizer Frontend — Implementation Plan (Phases 2–8)

## Tech Stack Decisions (Confirmed)

| Decision | Choice | Notes |
|----------|--------|-------|
| Charts | **ngx-charts `@25.0.2`** | Angular-native, D3-based, declarative API. Versão fixada em 2026-10-05: a 25.0.2 declara `peerDependencies` em `^22.0.0`, e o projeto já tem `@angular/cdk` e `@angular/animations`. Instalada e em uso na Phase 8 (proventos, evolução e valor justo) e no gráfico de Resultados da 6.3 |
| Date picker | **Native `<input type="date">`** | Better mobile UX (OS picker), lighter; Material datepicker works but opens full-screen dialog on mobile |
| Table | **Material Table** | Built-in sort, pagination, filtering |
| State | **Signals + Services** | Sufficient for scope; no NgRx |
| Env config | **Build-time `environment.ts`** | Same Docker image across envs |
| Auth extras | Register / Forgot password | Not needed |

---

## Phase 2 — Wallets CRUD

### Files to Create

```
src/app/features/wallets/
├── wallet.models.ts           # DTOs & interfaces
├── wallet.service.ts          # API service
├── wallet-list/
│   ├── wallet-list.ts
│   ├── wallet-list.html
│   └── wallet-list.scss
├── wallet-form/
│   ├── wallet-form.ts
│   ├── wallet-form.html
│   └── wallet-form.scss
└── wallet-detail/
    ├── wallet-detail.ts
    ├── wallet-detail.html
    └── wallet-detail.scss
```

### Details

**`wallet.models.ts`**
```ts
export interface WalletDTO {
  id: number;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateWalletDTO {
  name: string;
  description?: string;
}

export interface UpdateWalletDTO {
  name?: string;
  description?: string;
}
```

**`wallet.service.ts`**
- `getAll(): Observable<WalletDTO[]>`
- `getById(id: number): Observable<WalletDTO>`
- `create(dto: CreateWalletDTO): Observable<WalletDTO>`
- `update(id: number, dto: UpdateWalletDTO): Observable<WalletDTO>`
- `delete(id: number): Observable<void>`
- Base URL: `${environment.apiUrl}/wallet`

**`wallet-list`**
- Material Table with columns: Name, Description, Created At, Actions
- Row click → `/wallets/:id`
- FAB → `/wallets/new`
- Empty state with CTA

**`wallet-form`**
- Reactive form: `name` (required, max 100), `description` (optional, max 500)
- Dialog (MatDialog) or standalone page
- Reused for create & edit (check route param `id`)
- On success: snackbar + navigate to detail

**`wallet-detail`**
- Header: name + edit/delete buttons
- MatTabGroup: **Assets**, **Transactions**, **Portfolio**
- Assets tab: embed `AssetList` with `walletId` input
- "Add Asset" button → `/assets/new?walletId=:id`

---

## Phase 3 — Assets CRUD

### Files to Create

```
src/app/features/assets/
├── asset.models.ts
├── asset.service.ts
├── asset-list/
├── asset-form/
└── asset-detail/
```

### Details

**`asset.models.ts`**
```ts
export interface AssetDTO {
  id: number;
  walletId: number;
  symbol: string;
  name: string;
  quantity: number;
  avgPrice: number;
  currentPrice?: number;
  currentValue?: number;
  pnl?: number;
  pnlPercent?: number;
  warning?: boolean;
  createdAt: string;
}

export interface CreateAssetDTO {
  walletId: number;
  symbol: string;
  name: string;
  quantity: number;
  avgPrice: number;
}

export interface UpdateAssetDTO {
  symbol?: string;
  name?: string;
  quantity?: number;
  avgPrice?: number;
}
```

**`asset.service.ts`**
- `getByWallet(walletId: number): Observable<AssetDTO[]>`
- `getById(id: number): Observable<AssetDTO>`
- `create(dto: CreateAssetDTO): Observable<AssetDTO>`
- `update(id: number, dto: UpdateAssetDTO): Observable<AssetDTO>`
- `delete(id: number): Observable<void>`
- Base URL: `${environment.apiUrl}/assets`

**`asset-list`** (used in wallet detail)
- Input: `walletId`
- Table: Symbol, Name, Qty, Avg Price, Current Price, Value, P&L %, Actions
- P&L cell: `ProfitLossPipe` (green/red + icon)
- Row click → `/assets/:id` (detail with transactions)
- "Add Asset" → `/assets/new?walletId=`

**`asset-form`**
- Reactive form: symbol (required, uppercase), name, quantity (min 0.000001), avgPrice (min 0)
- Pre-fill `walletId` from query param or parent route
- Dialog or page

**`asset-detail`**
- Header: symbol + name + edit/delete
- Transactions tab: embed `TransactionList` with `assetId`
- "Add Transaction" → `/transactions/new?assetId=:id`

---

## Phase 4 — Transactions CRUD

### Files to Create

```
src/app/features/transactions/
├── transaction.models.ts
├── transaction.service.ts
├── transaction-list/
├── transaction-form/
└── transaction-detail/
```

### Details

**`transaction.models.ts`**
```ts
export type TransactionType = 'BUY' | 'SELL';

export interface TransactionDTO {
  id: number;
  assetId: number;
  type: TransactionType;
  quantity: number;
  price: number;
  fees: number;
  total: number;
  date: string;
  createdAt: string;
}

export interface CreateTransactionDTO {
  assetId: number;
  type: TransactionType;
  quantity: number;
  price: number;
  fees: number;
  date: string; // ISO date
}

export interface UpdateTransactionDTO {
  type?: TransactionType;
  quantity?: number;
  price?: number;
  fees?: number;
  date?: string;
}
```

**`transaction.service.ts`**
- `getByAsset(assetId: number): Observable<TransactionDTO[]>`
- `getById(id: number): Observable<TransactionDTO>`
- `create(dto: CreateTransactionDTO): Observable<TransactionDTO>`
- `update(id: number, dto: UpdateTransactionDTO): Observable<TransactionDTO>`
- `delete(id: number): Observable<void>`
- Base URL: `${environment.apiUrl}/transactions`

**`transaction-list`**
- Input: `assetId`
- Table: Date, Type (badge: BUY=green, SELL=red), Qty, Price, Fees, Total, Actions
- Sort by date desc default

**`transaction-form`**
- Reactive form:
  - `type`: MatSelect (BUY/SELL)
  - `quantity`: number, step=0.000001, min=0.000001
  - `price`: number, step=0.01, min=0
  - `fees`: number, step=0.01, min=0, default=0
  - `date`: `<input type="date">`, default=today
- Pre-fill `assetId` from query param
- **Validation**: if SELL, max qty = asset.availableQty (fetch from AssetService)
- Compute `total = quantity * price + fees` preview

**`transaction-detail`** (optional)
- Read-only view with all fields
- Edit/Delete actions

---

## Phase 5 — Portfolio Summary

### Files to Create

```
src/app/features/portfolio/
├── portfolio.models.ts
├── portfolio.service.ts
├── portfolio/
│   ├── portfolio.ts
│   ├── portfolio.html
│   └── portfolio.scss
└── portfolio-detail/
    ├── portfolio-detail.ts
    ├── portfolio-detail.html
    └── portfolio-detail.scss
```

### Details

**`portfolio.models.ts`**
```ts
export interface AssetSummaryDTO {
  id: number;
  symbol: string;
  name: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  currentValue: number;
  invested: number;
  pnl: number;
  pnlPercent: number;
  allocationPercent: number;
  warning: boolean;
}

export interface PortfolioSummaryDTO {
  walletId: number;
  walletName: string;
  totalInvested: number;
  currentValue: number;
  totalPnL: number;
  totalPnLPercent: number;
  assets: AssetSummaryDTO[];
  lastUpdated: string;
}
```

**`portfolio.service.ts`**
- `getSummary(walletId: number): Observable<PortfolioSummaryDTO>`
- Endpoint: `GET /wallet/{id}/summary`

**`portfolio` (list)**
- Grid of wallet summary cards
- Each card: wallet name, total invested, current value, P&L (green/red)
- Click → `/portfolio/:id`

**`portfolio-detail`**
- Header: wallet name, last updated, refresh button
- **Summary cards row**: Total Invested, Current Value, Total P&L, P&L %
- **Allocation Chart** (ngx-charts): Pie chart by `allocationPercent`
- **P&L Waterfall** (ngx-charts): Bar chart showing each asset's P&L contribution
- **Assets Table**: Symbol, Name, Qty, Avg Price, Current Price, Value, P&L, P&L %, Allocation %, Warning badge
- Warning assets highlighted (row color + icon)

**ngx-charts Setup**
```bash
npm install @swimlane/ngx-charts
```
- Import `NgxChartsModule` in portfolio feature
- Use `PieChartModule`, `BarVerticalModule`, `ColorHelper`

---

### Phase 5 Implementation Status (2026-10-03)

Rota `/portfolio` ligada em `app.routes.ts`; item "Portfólio" já existia em
`NAV_SECTIONS`, então não houve mexer no menu.

**Arquivos criados**
- `src/app/features/portfolio/portfolio.models.ts` — espelha o
  `PortfolioSummaryDTO` real, com `null` para ticker que falhou no Brapi.
- `src/app/features/portfolio/portfolio.service.ts` — `getSummary(walletId)` e
  `getSummaries(walletIds)` (forkJoin, um GET por carteira).
- `src/app/features/portfolio/portfolio/` — grid de cartões por carteira +
  faixa de totais.
- `src/app/features/portfolio/portfolio-detail/` — totais, alocação e tabela por
  ativo.
- `src/app/shared/pipes/currency-brl.pipe.ts`,
  `percentage-signed.pipe.ts`, `profit-loss-state.pipe.ts` — itens da Phase 6,
  antecipados porque dashboard e portfólio precisam dos três.

**Divergência do plano, em favor do backend**
O DTO descrito acima no plano não bate com o que o `ConsolidationService`
devolve. Foi o contrato real que virou a interface:
- `AssetSummaryDTO`: `assetId`, `ticker`, `symbol`, `quantity` → `amount`,
  `avgPrice` → `mediumPrice`, `pnl` → `profitLoss`, `pnlPercent` →
  `profitLossPercentage`, `allocationPercent` → `allocationPercentage`,
  `currentValue` é o **preço unitário** da Brapi (o valor da posição é
  `amount * currentPrice`), e há `warningMessage`.
- `PortfolioSummaryDTO`: `totalPnL` → `totalProfitLoss`, `currentValue` →
  `totalCurrentValue`, e **não existe `lastUpdated`** — o backend não expõe
  timestamp de Preis.

Preço e resultado são `null` quando o ticker falhou. Ativo sem preço entra com
`warning` e **fora dos totais**: ticker morto virar preço zero inventaria
prejuízo.

**ngx-charts não foi instalado**
O plano pedia `PieChartModule` + `BarVerticalModule`. A alocação virou um
`conic-gradient` com legenda, e o P&L por ativo está na tabela — sem
dependência nova, sem risco de incompatibilidade com o Angular 22 do projeto, e
sem 300 kB de vendor para dois gráficos. Se a Phase 6 quiser os gráficos de
verdade, é o momento de instalar a biblioteca.

**P&L real no painel**
`Dashboard` usava `AssetService.getByWallet` por carteira e tinha `'R$ 0,00'`
hard-coded em `Total P&L`. Agora consome os summaries: totais, contagem de ativos
e P&L vêm do mesmo endpoint, com preço vivo. `Total P&L` também troca ícone e
cor conforme o sinal. Percentual sobre investido zero retorna `0%`, nunca
`Infinity`.

**Correção do `shareReplay` na Etapa 1**
O `shareReplay(1)` desta sessão estava dentro de `WalletService.getAll()`, o que
cria um multicast **novo a cada chamada** — dashboard, lista e detalhe seguiam
disparando um GET cada, que é exatamente o loop a Etapa 1 deveria eliminar.
Movido para o campo `all$` (`refCount: false`) e criado `invalidate()`, chamado
após create/update/delete de carteira. Sem ele o `shareReplay` continuaria
servindo lista antiga depois de uma mutação.

**Verificação**
- `ng build --configuration development`: OK. Único aviso é o
  `@import "tailwindcss"` do Sass, pré-existente.
- Sem validação de browser/HAR ainda: o critério de "exatamente 1 GET
  `/assets?walletId`" da Etapa 1 continua sem evidência de rede.

---

## Phase 6 — Polish, navegação, análise consolidada e resultados

**Status:** 6.1, 6.2, 6.3, 6.3.1, 6.3.2, 6.3.3, 6.6, 6.4, 6.5, 6.7.1 e 6.7.2
implementados e commitados. A 6.7.3 foi **delegada ao ADC** (ver abaixo) e não
será implementada no consolidator. Cada bloco termina com build e testes verdes,
seguido de revisão manual do usuário antes do commit.

**Ordem:** 6.1 → 6.2 → 6.3 → 6.3.1 → 6.3.2/6.3.3 → **6.6** → **6.4 ✅** → **6.5**
→ 6.7. A 6.6 subiu na fila porque é correção de bug (data exibida errada e venda
“hoje” recusada) e é pré-requisito da Fase D do backend; 6.4 e 6.5 são
funcionalidades novas. Não iniciar um bloco sem o anterior aprovado.

### 6.1 — Polish + navegação + validações

**Decisões de UX**
- Navbar e sidebar voltam à estrutura simples anterior, com **fundo branco e
  detalhes em azul**.
- Remover breadcrumbs, rótulos de seção e o botão de colapso da sidebar.
- Menu hambúrguer apenas no mobile; no desktop a sidebar fica fixa.
- No desktop a sidebar é um trilho de 72px **só com ícones**; o nome da tela
  aparece em tooltip ao passar o mouse. No mobile o drawer abre com ícone e
  nome, porque não há hover no toque.
- Manter os links atuais: Painel, Carteiras, Ativos, Transações, Portfólio e
  Análise; Administração continua separada para ADMIN.
- Item ativo com pílula azul clara e indicador lateral; foco visível e alvos de
  toque de 44–48px.
- Usar variáveis CSS de tema para permitir testar novos templates depois sem
  reescrever os componentes.

**Validações**
- Manter `uniqueWalletName`.
- Remover qualquer validação de ticker duplicado: o mesmo ticker pode existir
  em mais de uma carteira.
- Dentro da mesma carteira, o backend já absorve o ticker existente e soma a
  posição via ledger (`AssetService.absorbInto`), recalculando o preço médio.
- Ao tentar adicionar um ticker que já existe em **outra carteira**, mostrar
  aviso inline **e** um popup de confirmação (`ConfirmDialog` com tom
  `warning`) antes de salvar. A mensagem deve explicar que ativos iguais em
  carteiras diferentes fragmentam preço médio, proventos e desempenho, e
  recomendar lançar na mesma carteira.
- `ConfirmDialog` ganhou tons `info`, `warning` e `danger`, com ícone e cor
  próprios, para diferenciar aviso, exclusão e confirmação neutra.
- Na mesma carteira, não avisar: é o fluxo esperado de soma.

**Acessibilidade e responsividade**
- Skip link para o conteúdo principal e landmark `main`.
- `aria-live="polite"` + `role="status"` em todos os loaders inline.
- Empty states padronizados em `mat-card`.
- Tabelas de transações e proventos viram cards abaixo de 600px.
- Tabelas restantes com rolagem horizontal no card.
- FAB de nova transação no portfólio mobile.
- Textos de loading, notificações e botões auxiliares em português.

**Limpeza**
- Remover CSS global e por feature duplicado/morto.
- Não reintroduzir `.page-header` global: o componente `PageHeader` é a fonte
  única do cabeçalho de página.

**Critérios de aceite**
- `npx ng build` e `npx ng test --watch=false` verdes.
- Navbar/sidebar funcionam em desktop e mobile, sem menu hambúrguer redundante
  no desktop.
- Carteira com nome duplicado bloqueia o submit.
- Ticker duplicado na mesma carteira soma a posição; em outra carteira, exige
  confirmação.
- Nenhum loader sem `role`/`aria-live`.

### 6.2 — Análise com “Todas as carteiras”

**Objetivo:** ver patrimônio total, total investido e proventos totais do
usuário, sem escolher uma carteira.

**Backend**
- `GET /wallet/summary` (rota estática, sem `walletId`) devolve
  `PortfolioTotalsDTO`: `generatedAt`, `walletCount`, `assetCount`,
  `pricedAssetCount`, `totalInvested`, `pricedInvested`, `totalCurrentValue`,
  `totalProfitLoss`, `totalProfitLossPercentage`, `complete`, `missingPrices[]`
  e `wallets[]` (breakdown por carteira).
- O P&L consolidado usa **apenas** o custo das posições com preço
  (`pricedInvested`). Ticker que falhou na Brapi entra em `missingPrices` e
  deixa `complete=false`; nunca vira preço zero. Com zero posições precificadas,
  `totalProfitLossPercentage` é `null`.
- `GET /dividends/summary` com `walletId` opcional: sem filtro, agrega todas as
  carteiras do usuário autenticado.
- `GET /dividends` sem `assetId` nem `walletId` devolve todas as receitas do
  usuário (opcionalmente filtradas por `year`).
- `GET /wallet/history?walletId=&from=&to=`: `walletId` opcional. Sem ele, a
  série soma as carteiras por data e devolve `walletId: null`. A resposta mantém
  `warnings`, `complete` e `missingTickers`; o cache de fechamentos é por
  `ticker|range` para não repetir a Brapi quando o mesmo ticker aparece em mais
  de uma carteira.
- Todos os caminhos derivam o usuário do token (nunca de um id da request) e
  têm testes de service/controller, incluindo ownership e a precedência de
  `/wallet/summary` e `/wallet/history` sobre `/wallet/{id}`.

**Frontend**
- Componente compartilhado `WalletScopeSelect` + tipo
  `WalletScope = 'all' | number`. `?walletId=` ausente/inválido significa
  `'all'`; o parâmetro some da URL ao voltar para “Todas as carteiras”.
- **Ativos:** escopo padrão `'all'`, coluna “Carteira” (nome vindo de
  `WalletDTO.assets`, sem request extra) e “Adicionar posição” abrindo o
  formulário sem carteira pré-preenchida — o formulário pergunta a carteira.
  Deep link `?walletId=` mantém o recorte por carteira e esconde a coluna.
- **Análise — Visão geral:** cards de patrimônio total, total investido,
  proventos totais e resultado consolidado. O resultado mostra percentual sobre
  `pricedInvested` e um aviso declara `missingPrices` quando a Brapi falha.
  Gráficos de proventos e evolução usam as rotas agregadas em `'all'` e as rotas
  por carteira no recorte individual.
- **Análise — Proventos:** escopo padrão `'all'`, seletor de ativo com opção
  “Todos os ativos”, tabela consolidada de receitas com coluna “Carteira” e
  yield sobre o patrimônio do escopo. Ao escolher um ativo, as receitas são as
  do ativo e o yield usa o summary da carteira dona; sincronização e lançamento
  manual continuam disponíveis apenas nesse modo.
- Aba de valor justo continua por ativo/carteira; não entra no agregado nesta
  fase.

**Critérios de aceite**
- Usuário com duas carteiras vê a soma correta em análise e em ativos, e a
  análise abre em “Todas as carteiras” por padrão.
- Carteira individual continua funcionando como antes via `?walletId=`.
- Falha de preço da Brapi aparece como aviso, nunca como valor zero inventado.
- `npx ng build` e `npx ng test --watch=false` verdes.

### 6.3 — Resultado realizado e compensação de prejuízos

**Status:** entregue em 2026-11-02 (backend e front), revisado e commitado.

**Objetivo:** registrar e exibir lucro/prejuízo realizado nas vendas e manter
um saldo de prejuízo a compensar. **Sem caixa real nesta fase.**

**Backend — entregue**
- `GET /transactions/results` com `walletId`, `from` e `to` opcionais. `from`
  depois de `to` responde 400, e a posse da carteira continua validada pelo
  `TransactionService` (carteira alheia é 403).
- O resultado por venda é derivado do ledger, não de tabela nova:
  `(preço de venda − custo médio no ponto da venda) × quantidade`. Editar ou
  excluir uma transação recalcula tudo, sem risco de divergência.
- `AssetPositionCalculator` passou a devolver, além da posição, as vendas que a
  produziram (`ReplayResult`/`RealizedSale`). O custo médio usado é o **daquele
  ponto do replay**, não o preço médio atual: numa venda retroativa, é o custo
  da data que vale.
- `RealizedResultService` totaliza valor vendido, lucro, prejuízo, resultado
  líquido e faz a compensação cronológica de prejuízos. O recorte de período
  filtra as vendas, mas não a compensação: `openingLossBalance` carrega o
  prejuízo anterior a `from`, então filtrar novembro não apaga o prejuízo
  acumulado até outubro.
- `TransactionResponseDTO.realizedResult` vem preenchido em create, list, get e
  update; é `null` em compra, que não realiza resultado.
- Testes: `RealizedResultServiceTest`, `TransactionResourceTest` (incluindo a
  convivência de `/results` com `/{id}` e o 400 de período) e
  `AssetPositionCalculatorTest`.

**Frontend — entregue**
- A aba **Resultados** mora em **Transações**, com as abas “Transações” e
  “Resultados”. Rota `/transactions/results`; o link antigo `/analysis/results`
  redireciona para lá.
- Cards de lucro realizado, prejuízo realizado, resultado líquido, após
  compensação, prejuízo a compensar e total vendido, mais a tabela de vendas e o
  aviso de controle gerencial.
- Gráfico de **colunas** com o resultado por data de venda (vendas do mesmo dia
  somadas). Acumulado responderia outra pergunta, que a tabela não detalha.
- Filtro por ano e mês; o recorte vai para o servidor em `from`/`to` porque a
  compensação depende do histórico anterior.
- Formulário de venda dedicado em `/transactions/sell`, sem toggle de tipo:
  carteira, ativo com posição, quantidade, preço, data, total estimado e
  resultado estimado. `/transactions/new` redireciona (`type=BUY` →
  `/assets/new`, o resto → `/transactions/sell`), preservando a query.
- O formulário de transação virou **somente edição**: quantidade, preço e data.
  Tipo, carteira e ativo aparecem visíveis e travados.
- Header de Transações com “Adicionar posição” e “Vender ativo”; “Nova
  transação” saiu. A aba de transações da carteira e o FAB do portfólio seguem
  a mesma regra.
- Posições zeradas (`amount <= 0`) somem da lista de Ativos, do contador da
  carteira e do seletor de venda. O ativo continua no backend por causa do
  histórico e do resultado; uma nova compra o reabre.
- `goBack` (`shared/navigation/go-back.ts`) faz Cancelar e o retorno pós-salvar
  usarem o histórico do browser quando existe navegação in-app, com fallback
  explícito em acesso direto por link.
- `npx ng build` e `npx ng test --watch=false` verdes: 98 testes em 19 arquivos.

**Decisões desta rodada**
- **Resultados pertencem a Transações.** O plano original pedia a aba em
  Análise; como o resultado é derivado do ledger, a tela foi para junto das
  compras e vendas, e Análise ficou com o que é análise de posição.
- **Vender é uma tela, não um tipo.** O toggle Compra/Venda era um remendo: o
  formulário tentava ser duas telas e a opção “Compra” continuava visível num
  fluxo de venda. O tipo virou consequência da tela.
- **Compra é “Adicionar posição”.** O backend já absorve o ticker existente e
  soma via ledger, então não há um segundo caminho de compra a manter.
- **Posição zerada não é posição.** O ativo é preservado no backend, mas não
  aparece em lista de posições, seletor de venda nem contadores.

**Critérios de aceite — verificados**
- Venda de posição inteira e parcial mostram resultado correto.
- Prejuízo acumulado reduz o resultado tributável seguinte.
- Editar/excluir uma venda ou compra recalcula os cards e a tabela.
- Nenhum valor de caixa é inventado; a tela fala em resultado realizado, não
  em saldo disponível.

#### 6.3.1 — Cores e rótulos no gráfico de Resultados

**Status:** entregue em 2026-11-04 e commitado.

- Barra verde (`--positive`) para lucro, vermelha (`--negative`) para prejuízo e
  cinza neutro quando o resultado do dia é exatamente zero — zero não é lucro.
- Valor de cada coluna impresso na barra em `1.234,56` (duas casas, sem `R$`,
  que já aparece no eixo Y e no tooltip).
- As cores ficam no `customColors` como valores literais porque `fill` de SVG
  não resolve `var(--positive)`; os rótulos são centralizados por
  `::ng-deep .textDataLabel`.

#### 6.3.2 — Posições zeradas fora do Portfólio

**Status:** entregue em 2026-11-04 e commitado.

- A correção fica no backend, em `ConsolidationService` (`getPortfolioSummary` e
  `getPortfolioTotals`), e não no componente: o mesmo resumo alimenta a aba
  “Portfólio” da carteira, `/portfolio/:id` e os cartões da listagem.
- Filtrar no front resolveria só a tabela; `assetCount`, `missingPrices`,
  `warningCount` e o banner de duplicados continuariam contando a posição
  morta, e a Brapi continuaria sendo consultada por ela.
- Implementado com um único predicado, `hasOpenPosition` (`amount > 0`), nos
  dois métodos. `amount == 0` é posição vendida por completo, não dado
  faltando: por isso a comparação é com zero e não com `null`.
- Testes: carteira com PETR4 (100) e VALE3 (0, sem preço) devolve só PETR4,
  VALE3 não aparece em `missingPrices` nem em `assetCount`, e a Brapi não é
  consultada para o ticker zerado.
- Fora deste item: `GET /wallet/{id}` continua devolvendo o ativo zerado — a aba
  Ativos já o esconde no front (`AssetList` filtra `amount > 0`) porque ali o
  histórico importa. O que muda aqui é só o resumo consolidado, que é o que
  alimenta Portfólio, `/portfolio/:id` e os cartões.

#### 6.3.3 — Recusa de venda antes da compra em pop-up

**Status:** entregue em 2026-11-04 e commitado.

- Só este caso vira `MatDialog` (título `Venda não permitida`, corpo
  `Não é possível vender um ativo antes de sua data de compra.`, botão `Entendi`,
  tom de aviso). As demais recusas de venda (posição insuficiente na data, falha
  de rede) continuam no snackbar + `app-error-display`.
- O front reconhece o caso por **código**, não por texto: o backend devolve
  `{"error": "...", "code": "SELL_BEFORE_PURCHASE"}` e o `sell-form` abre o
  diálogo quando `code` bate. Comparar a mensagem quebraria na primeira mudança
  de copy.
- Sem componente novo: o `ConfirmDialog` ganhou `acknowledgeOnly` (um botão só)
  e o `ConfirmService` ganhou `alert(title, message)`.
- A mensagem do backend mudou para o texto exato acima; o código também cobre
  `INSUFFICIENT_POSITION`, que o front segue tratando como aviso comum.

### 6.4 — Filtro de data na lista de transações

**Status:** entregue em 2026-11-10 e commitado (`129f6ab` no backend,
`6c97b77` no front).

- Reaproveitar o recorte de período que Resultados já usa (ano/mês ou
  `from`/`to`) na lista de transações.
- A lista hoje é filtrada por URL (`?walletId=`); o filtro de data entra como
  parâmetro de query para continuar linkável e sobreviver ao refresh.
- `GET /transactions` ganhou `from`/`to` opcionais, inclusivos e comparados pelo
  dia (`TradingDay.toDay`), com `from > to` respondendo 400. O filtro recorta só
  as linhas devolvidas: o resultado realizado continua sendo calculado sobre o
  ledger inteiro antes do corte, porque o custo médio de uma venda depende de
  compras fora do período.
- O front guarda o recorte em `?year=&month=`, reutiliza `shared/date/period.ts`
  e busca o ledger sem filtro uma vez por escopo para montar as opções de ano.
  A aba de transações da carteira ficou como estava: ela não tem estado de URL,
  e a visão por ativo já é coberta por `?assetId=`.
- Testes: backend **323**; front **154 em 26 arquivos**, build limpo.

### 6.5 — Isenção mensal de ações à vista

**Status:** entregue em 2026-11-11 e commitado (`2709451` no front).

- O backend já devolve `totalProceeds` em `/transactions/results` justamente
  porque a isenção depende do volume vendido, não do resultado.
- A tela deve mostrar “vendido no mês × limite de isenção” e declarar
  explicitamente que não calcula imposto nem separa swing trade, day trade ou
  FIIs.
- A faixa entra em Resultados, abaixo dos cards, e só compara quando ano e mês
  estão selecionados. Sem mês, mostra instrução; com carteira específica, mostra
  o valor como escopo parcial, sem veredito de dentro/acima, porque a isenção é
  por CPF.
- Limite fixo de **R$ 20.000,00**, inclusivo (`≤`). `totalProceeds` inclui
  todas as vendas do período, não só ações: `Asset.assetType` existe no schema
  mas nunca é preenchido, então filtrar por tipo seria outro slice de backend.
  O rodapé declara essa limitação e que não há apuração de imposto.
- `totalProceeds` nulo aparece como `—` com aviso; nunca vira zero.
- Testes: front **160 em 26 arquivos**, build limpo.

### 6.6 — Convenção de datas de negociação

**Status:** entregue em 2026-11-04 e commitado (`e83a10f` no backend,
`0a74b51` no front). **Fase D do backend entrou junto** (validação de data
futura no servidor).

**Sintoma relatado pelo usuário:** a data de compra exibida nas transações
aparece um dia antes da preenchida no formulário, e uma venda “hoje” é recusada
como anterior à compra.

**Decisão: data é dia, não instante.**

- A data de negociação é um **dia de calendário**, então ela **não cruza a
  API como instante**: `transactionDate` e `acquisitionDate` viram `LocalDate`
  (JSON `2026-11-01`) na requisição e na resposta. Nenhum fuso entra no
  contrato, e o front não tem mais como perder um dia no `DatePipe`.
- No banco, a coluna continua `timestamp` (não `date`): trocar o tipo exigiria
  migração com SQL diferente em H2 e PostgreSQL, porque o schema é do Flyway
  nos dois ambientes e `ddl-auto=validate` recusaria divergência. O instante
  guardado é sempre a **meia-noite UTC do dia escolhido** — que é exatamente o
  que as linhas criadas pelo formulário já contêm, então não há migração de
  dados.
- A comparação e a ordenação passam a ser **por dia** (`TradingDay.toDay`), não
  por instante. Com isso a hora residual de uma compra de abertura criada no
  passado não afeta mais nada.
- “Hoje” é o dia em `America/Sao_Paulo` (`TradingDay.today()`): é o calendário
  do usuário e do pregão. Meia-noite UTC é só a forma de armazenar o dia.
- A normalização fica em `common/time/TradingDay`: um único lugar sabe
  converter dia ↔ instante. Se um dia a coluna virar `date`, só esse arquivo
  muda.

#### 6.6.1 — Data exibida um dia antes da preenchida

- `transaction-list.html` e `wallet-transaction-list.html` usam
  `{{ row.transactionDate | date:'dd/MM/yyyy' }}`.
- O backend enviava `2026-11-01T00:00:00.000Z`; o `DatePipe` convertia o
  instante para o fuso local (BRT, UTC−3) e mostrava `31/10/2026`.
- Correção: helper único `shared/date/format-day.ts`, aplicado em todas as
  listas que mostram data de transação. Ele formata o **dia** da string, sem
  passar por fuso — a mesma ideia do `formatDay()` que a aba Resultados já
  usava, agora compartilhada.

#### 6.6.2 — O contrato de data é instante, mas a regra é diária

- O backend, quando `acquisitionDate` era nulo, criava a compra de abertura com
  `new Date()` — **com hora** (`AssetService`, linhas 131 e 167).
- Duas transações do mesmo dia ordenavam diferente conforme a hora, e o replay
  (`TransactionService.sort`, por data e depois por `id`) fazia uma venda “hoje”
  cair **antes** de uma compra de abertura do mesmo dia, sendo recusada como
  “venda antes da compra”. Era a causa do “não consigo vender hoje”.
- Correções: abertura usa o dia de hoje (sem hora); a ordenação canônica é
  `dia → BUY antes de SELL → id`; vender no mesmo dia da compra passa a ser
  permitido porque a comparação é por dia.

#### 6.6.3 — `todayInput()` usa UTC

- `new Date().toISOString().slice(0, 10)` devolvia o dia UTC. Depois das 21h em
  BRT já era o dia seguinte.
- Efeitos: o formulário abria com uma data “de amanhã”, o `[max]` do datepicker
  e o `notInFuture` permitiam esse dia, e o rótulo “Não pode ser futura” mentia.
- Correção: `todayInput()` calcula o dia em `America/Sao_Paulo`.

#### 6.6.4 — Validação de data futura no servidor (Fase D)

- Antes só o formulário barrava data futura; um `POST` direto passava.
- A validação entra no serviço, contra `TradingDay.today()`, e não via
  `@PastOrPresent`: a anotação usa o fuso padrão da JVM, então a mesma data
  seria aceita ou recusada conforme o servidor rodasse em UTC (container) ou em
  BRT (máquina de desenvolvimento).
- Fica de fora por ora: validar data futura para os dividendos, que têm
  contrato de data próprio.

#### 6.6.5 — O datepicker lia `yyyy-MM-dd` como instante UTC

- Com o contrato date-only, o controle do formulário passou a valer
  `2026-11-05` (string). O `NativeDateAdapter` deserializa string ISO com
  `new Date(value)`, isto é, **meia-noite UTC** — que em BRT é 04/11 21:00.
- Consequências: o campo abria mostrando **ontem** enquanto o modelo era hoje
  (a data exibida como “ontem” era gravada como hoje); o calendário destacava o
  dia anterior; e o `[max]="today"` virava ontem 21:00, **bloqueando o dia de
  hoje** na seleção e reprovando-o no validador `matDatepickerMax` sem mostrar
  mensagem.
- Correção em `shared/date/iso-date.adapter.ts`: `deserialize`/`parse` montam
  `new Date(ano, mês - 1, dia)`, meia-noite **local**; ISO completo vale pela
  parte UTC, que é o envelope antigo do dia. `toIso8601` também serializa o dia
  local, porque o `max`/`min` nativos saem daí.
- O modelo do formulário continua `yyyy-MM-dd`: o `MatDatepicker` não escreve no
  controle ao receber `writeValue`, então `inputToIsoDay` segue valendo.
- Testes: `iso-date.adapter.spec.ts` (dia local, ISO legado, 31/02 recusado,
  `toIso8601`).

**Implementação — backend**
- `common/utils/TradingDay`: único lugar que converte dia ↔ instante
  (`today()` em São Paulo, `toDay`/`startOfDay` em meia-noite UTC,
  `rejectFuture`).
- `common/utils/LedgerOrder`: ordem canônica `dia → BUY antes de SELL → id`,
  usada por `TransactionService` e `RealizedResultService`.
- `TransactionDTO.transactionDate` e `AssetCreateDTO.acquisitionDate` são
  `LocalDate`; `TransactionResponseDTO.transactionDate` também, então o JSON é
  `2026-11-01` e o front não converte fuso.
- Compra de abertura usa `TradingDay.today()` em vez de `new Date()`; criação e
  edição normalizam o dia e recusam data futura com o código
  `FUTURE_TRANSACTION_DATE`.
- O corte do histórico passou de `<=` meia-noite do dia para `<` meia-noite do
  dia seguinte: com `<=` a transação do dia seguinte vazava para o dia anterior.
- Sem migração: a coluna continua `timestamp` e o envelope gravado é o mesmo
  das linhas antigas (meia-noite UTC do dia). O que mudou é que nada mais lê a
  hora.
- Testes: `TradingDayTest`, `LedgerOrderTest`, venda no mesmo dia da compra em
  `AssetOpeningTransactionTest`, data futura em `TransactionServiceTest`,
  contrato `yyyy-MM-dd` em `TransactionResourceTest`/`AssetResourceTest`, e o
  corte exclusivo em `TransactionRepositoryTest`/`PortfolioHistoryServiceTest`.
  Suíte: **316 testes**.

**Implementação — front**
- `shared/date/format-day.ts` (`formatDay`) substitui `DatePipe` nas listas de
  transações; a aba Resultados passou a usar o mesmo helper em vez da cópia
  local.
- `todayInput()` calcula o dia em `America/Sao_Paulo` via `Intl`, com o relógio
  injetável para teste.
- Formulários de venda/edição/abertura mandam `yyyy-MM-dd` (`inputToIsoDay`);
  `inputToIsoInstant` ficou só para dividendos, cujo contrato ainda é instante.
- `isoDayFromIsoInstant` virou `isoDayOf`, aceitando tanto `2026-11-01` quanto
  linhas antigas em ISO completo.
- `IsoDateAdapter` passou a deserializar dia como meia-noite local (6.6.5): o
  calendário, o `[max]` e a validação passam a concordar com o valor exibido.
- Aba Resultados: o eixo X do gráfico agrupa por dia e ordena pelo ISO. Antes
  ordenava pela label `dd/MM/yyyy`, que é lexicográfica — `01/12/2026` vinha
  antes de `05/11/2026` e o eixo deixava de ser cronológico.
- Testes: `date-utils.spec.ts` (virada de dia 00:30Z = 21:30 BRT e
  `notInFuture`), `format-day.spec.ts`, `iso-date.adapter.spec.ts`, a ordem do
  gráfico em `results.spec.ts` e o campo exibindo hoje em `sell-form.spec.ts`.
  Suíte na época: **130 testes em 24 arquivos** (hoje 154 em 26).

### 6.7 — Evolução patrimonial por fechamento diário

**Status:** 6.7.1 e 6.7.2 concluídas e commitadas em 2026-11-13; a 6.7.3 foi
delegada ao ADC.

**O que já existe (não começar do zero)**
- `BrapiAdapter.getHistoricalPrices(ticker, range)` consome
  `/quote/{ticker}/historical?range=..&interval=1d` e devolve os fechamentos.
- `PortfolioHistoryService.buildHistory` reconstrói **um ponto por dia** desde
  o início do ledger, usando esses fechamentos, com `warnings` para dias
  incompletos (`PortfolioPointDTO.complete = false`). Decisão D13: nunca
  inventar preço, sempre declarar o que não foi reconstruído.
- `PortfolioSnapshotService` persiste/backfilla um snapshot por dia, e
  `/portfolio/history` já alimenta o gráfico de evolução em `/analysis`.
- O recorte já começa na primeira compra: com `from` ausente, `clampFrom`
  devolve `ledgerStart`; um `from` anterior à primeira transação é clampado
  com warning.
- 6.7.1: o aviso de histórico incompleto declara o primeiro ponto com valor
  completo; o eixo X é resumido (uma marca por ano quando a série cobre mais de
  um ano, até seis `dd/MM` quando cabe em um só) e o dia exato aparece no
  tooltip; pontos com `totalValue` nulo são omitidos da linha em vez de virarem
  zero.
- 6.7.2: `GET /wallet/{id}/volatility` e `GET /wallet/volatility` devolvem uma
  linha por ticker com posição na janela. Métrica: desvio-padrão **amostral**
  dos retornos diários **logarítmicos** × √252, mínimo de **20** retornos
  (`null` abaixo disso), buracos > 5 dias corridos descartados e
  `adjustedClose` quando a série inteira o traz (fallback para `close` com
  aviso). No front, tabela ordenada da maior para a menor volatilidade, com
  `observations` e a janela de fechamentos; `null` vira “—”, nunca 0%.

**O que falta**
- **6.7.3 — persistência dos fechamentos: delegada ao ADC (decidido em
  2026-11-13).** O consolidator não terá tabela `daily_close`.

**Decisão tomada (ADC)**
- A série diária de fechamentos sai do consolidator e vai para o **ADC**
  (Asset Data Collector), coletada do **COTAHIST** (B3), com tabela
  `daily_close` e endpoints `GET /v1/prices/{ticker}` e
  `GET /v1/prices?tickers=` — contrato congelado em `ADC_PLAN.md` §26.
- Até a integração existir, o consolidator continua chamando a Brapi por
  request (duas chamadas por ticker em `/analysis`). Isso é dívida conhecida,
  não bug: fica registrada e some quando o cliente `/v1/prices` entrar.
- O ADC entrega `close` (patrimônio) e `adjusted_close` + `adjusted`
  (volatilidade), o que também substitui a heurística atual de "a série inteira
  tem `adjustedClose`".
- A integração (cliente HTTP no consolidator, cache curto e fallback Brapi) é a
  **Fase 9 do ADC** e só começa quando o endpoint estiver de pé.

### Fora de escopo por agora

- Caixa real com aportes, saques, compras, vendas, proventos e impostos
  (`CashMovement`).
- Separação fiscal por swing trade, day trade e FIIs.
- Novos templates globais de UX: depois da 6.3.2, testar um template piloto
  (dashboard) antes de aplicar no restante.

### Componentes compartilhados existentes

```
src/app/shared/components/
├── confirm-dialog/       # confirmação reutilizável
├── page-header/          # título, subtítulo e slots de ação
├── wallet-scope-select/  # “Todas as carteiras” + `WalletScope`
└── notification/         # snackbar centralizado
```

Pipes já existentes: `currency-brl`, `percentage-signed` e `profit-loss-state`.

Helpers de navegação: `shared/navigation/go-back.ts` (volta pelo histórico
quando há navegação in-app; senão navega para a URL de fallback). Usado por
`sell-form` e `transaction-form`.

Abas de feature: `transactions-tabs` (Transações/Resultados) e `analysis-tabs`
(Visão geral/Proventos/Valor justo). Ficam na feature, não em `shared`, porque
carregam as rotas de cada área.

### Auth extras (continua bloqueado)

- Registro existe.
- Recuperação/reset de senha e refresh silencioso dependem de endpoints do
  backend que ainda não existem.

---

## Phase 7 — Deploy & Tooling

### Testing

**Unit (Vitest — já adotado)**
- `ng test` roda Vitest via builder do Angular 22; não há `jest.config.ts`.
  A instalação de Jest/Testing Library prevista aqui não foi usada.
- Specs de services, guards, pipes, componentes e DTOs; os specs de componente
  usam `TestBed` + `RouterTestingHarness` e `provideNoopAnimations`.
- Baseline atual: **170 testes em 26 arquivos**, com
  `npx ng test --watch=false` e `npx ng build` verdes. Nesta máquina, a suíte
  completa precisa de `testTimeout: 30000` e `hookTimeout: 30000` via
  `--runner-config` (specs de componente passam dos 5s/10s padrão sob carga
  paralela).
- [ ] Coverage threshold e script dedicado de cobertura.

**E2E (Playwright — não iniciado)**
```
npm install -D @playwright/test
npx playwright install
```
- `playwright.config.ts`
- Specs:
  - `auth.spec.ts` — login, logout, guard redirect
  - `wallets.spec.ts` — CRUD flow
  - `assets.spec.ts` — CRUD within wallet
  - `transactions.spec.ts` — compra, venda e edição
  - `portfolio.spec.ts` — summary view, charts render
- `npm run e2e`

### CI/CD

`.github/workflows/ci.yml`
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: checkout → setup-node → npm ci → npm run lint
  
  test:
    runs-on: ubuntu-latest
    steps: checkout → setup-node → npm ci → npm run test -- --ci --coverage
  
  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps: checkout → setup-node → npm ci → npm run build
  
  e2e:
    runs-on: ubuntu-latest
    needs: build
    steps: checkout → setup-node → npm ci → npx playwright install → npm run e2e
  
  docker:
    runs-on: ubuntu-latest
    needs: [build, e2e]
    if: github.ref == 'refs/heads/main'
    steps: checkout → docker/build-push-action → ghcr.io/user/visualizer
```

### Docker

**`Dockerfile`**
```dockerfile
# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build -- --configuration production

# Runtime stage
FROM nginx:alpine
COPY --from=build /app/dist/visualizer/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**`nginx.conf`**
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://app:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    gzip on;
    gzip_types text/css application/javascript application/json;
}
```

**`docker-compose.yml`** (add to root)
```yaml
services:
  frontend:
    build:
      context: ./visualizer
      dockerfile: Dockerfile
    ports:
      - "4200:80"
    depends_on:
      - app
    environment:
      - API_URL=http://app:8080
```

### Runtime Env Config

Build-time only via `environment.ts` (no `window.__ENV`).

---

## Phase 8 — Análise de Portfólio

**Status:** em andamento (2026-10-08) — slices 1, 2 e 3 entregues: `/analysis`
(visão geral), `/analysis/dividends` (proventos por ativo, sincronização Brapi e
lançamento manual) e `/analysis/fair-value` (valor justo por ativo com Graham,
Bazin e DCF, premissas editáveis, fórmula visível, resultado como faixa de
sensibilidade e histórico). A consolidação de tickers duplicados também foi
entregue: `POST /wallet/{id}/assets/merge` no backend (criação de ativo absorve
ticker duplicado, rename colidente bloqueado) e, no front, banner "Posições
duplicadas" em `/portfolio/{id}` com ação de consolidar e recálculo do preço
médio.

### Objetivo

Três telas que hoje não existem: proventos por ativo e por carteira, evolução
patrimonial da carteira, e preço justo por ativo e por método.

### Dependências de backend

Sem isso a tela nasce sem dado:

| Backend | O que entrega |
|---|---|
| **Fase 0** | Flyway, para as tabelas novas existirem em produção — **entregue** |
| **Fase F** | `GET /transactions?walletId=` — a Fase J faz replay do ledger |
| **Fase G** | `user` no login, para as telas pertencerem ao usuário — **entregue** |
| **Fase H** | Proventos. **Ações: automático. FIIs: 403 → aviso + lançamento manual** — **entregue** |
| **Fase I** | Graham, Bazin e DCF com as premissas do usuário — **entregue** |
| **Fase J** | Reconstrução do ledger + snapshot diário — **entregue** |

### Dependência de gráfico

`ngx-charts@25.0.2` entra aqui, e não antes — a Phase 5 provou que alocação em
CSS puro resolve o que ela pedia, e dois gráficos temporais com eixo e tooltip
não são razoáveis em CSS.

### Telas

1. **`/analysis`** — visão geral da carteira: gráfico de colunas de proventos
   por ano, total recebido, e gráfico de colunas de evolução patrimonial.
2. **Proventos por ativo** — colunas por ano, dividend yield, e formulário de
   lançamento manual que aparece quando a Brapi não tem o dado (FII).
3. **Valor justo por ativo** — seletor de método (Graham / Bazin / DCF),
   premissas editáveis, fórmula visível, resultado como **faixa de
   sensibilidade** e histórico dos cálculos.

### Regra de exibição do DCF

Nenhum número aparece como verdade. Todo valor pré-preenchido é marcado como
premissa editável, a fórmula fica visível, e o resultado sai como faixa. A Brapi
não fornece fluxo de caixa livre, crescimento nem taxa de desconto — o usuário
informa tudo, então a interface não pode sugerir autoridade que não existe.

### Avisos que a tela precisa exibir

- FII sem dado automático de dividendos → aviso + caminho para lançar manual.
- Histórico patrimonial incompleto → declarar o que não foi reconstruído, nunca
  truncar em silêncio (decisão D13 do roadmap).

---

## Execution Order

```
1. Phase 2 (Wallets) — foundation for Assets/Transactions     ✅
2. Phase 3 (Assets)  — depends on WalletService                ✅
3. Phase 4 (Transactions) — depends on AssetService            ✅
4. Phase 5 (Portfolio) — depends on all services               ✅
5. Phase 6 (Polish) — 6.1–6.6 ✅; 6.7.1 ✅; 6.7.2 ✅; 6.7.3 delegada ao ADC  🔄
6. Phase 7 (Deploy) — last                                     ⏳
7. Phase 8 (Análise) — só depois das fases backend 0, F, G, H, I, J  🔄 (slices 1-3: `/analysis` + `/analysis/dividends` + `/analysis/fair-value`) ✅
```

### Phase 2-4 Implementation Status (Frontend)

- **Lockout de autenticação corrigido (2026-10-05).** Com um token velho no `localStorage`, `POST /users` e `POST /auth/login` respondiam 403 — o usuário não conseguia nem criar conta nem entrar, e não havia caminho de recuperação. Duas causas: o `JwtInterceptor` anexava o token a **todas** as requisições (inclusive rotas públicas), e o `ErrorInterceptor` tratava 403 como simples mensagem, sem limpar a sessão. O `JwtInterceptor` passou a ignorar `/auth/` e `/users`, e 403 com token em mãos agora faz logout e redireciona para o login. A outra metade da correção foi no backend (`JwtAuthFilter`). Detalhes em `BACKEND_ROADMAP.md`.
- **Ambiente:** `spring-boot-devtools` recarrega o contexto no mesmo JVM ao editar código e **apaga o H2 em memória**. Contas somem sozinhas durante o desenvolvimento; não é bug.

- **AssetList infinite loop fix** (2026-10-03): Added `lastLoadedId` guard to prevent re-dispatching effects when walletId unchanged; load only when ID actually changes. Used `untracked()` to set guard before API call. 
- **WalletTransactionList infinite loop fix** (2026-10-03): Added context guard (`walletId|assetIds`) to reload only when context changes; fixed empty assets case to properly set loading to false.
- **WalletService** (2026-10-03): `shareReplay` adicionado a `getAll()`. **Corrigido depois**: dentro do método o multicast nascia a cada chamada, então o compartilhamento não existia de fato; o `shareReplay` foi para o campo `all$` com `refCount: false` e nasceu o `invalidate()` para as mutações de carteira. Ver Phase 5 Implementation Status.

---

## Estimated Effort

| Phase | Components | Services | Est. Days |
|-------|------------|----------|-----------|
| 2 | 3 | 1 | 2-3 ✅ |
| 3 | 3 | 1 | 2-3 ✅ |
| 4 | 3 | 1 | 2-3 ✅ |
| 5 | 2 | 1 | 2-3 ✅ |
| 6 | 5+ | 2 | 3-4 |
| 7 | Config | - | 2-3 |
| 8 | 3 | 1 | 3-4 |
| **Total** | **~22** | **7** | **16-23** |

---

## Next Steps

1. **6.7.2 — volatilidade por ativo**: concluída e commitada em 2026-11-13
   (backend `3181d7f`, front `84ca27c`). Se a Brapi não devolver `adjustedClose`,
   a tela declara o cálculo sobre preço bruto.
2. **6.7.3 — persistência dos fechamentos**: delegada ao ADC. O contrato
   `/v1/prices` já está congelado (`ADC_PLAN.md` §26); a integração no
   consolidator espera o endpoint existir.
3. **Phase 7 (Deploy & Tooling)** — próximo bloco deste repositório. O backend
   já tem Dockerfile, compose com PostgreSQL, profile `prod`, actuator, Flyway e
   springdoc; faltam validação em Postgres real e o CI/E2E do front.
4. **Auth extras** continuam bloqueados até existirem endpoints de recuperação
   de senha e refresh no backend.

Detalhes do backend em `../consolidator/consolidator/BACKEND_ROADMAP.md`. Este
arquivo é o plano de fases do front; `frontend-plan.md` é o documento inicial
(histórico), mantido só como referência.