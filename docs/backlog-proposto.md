# Backlog proposto de specs — 2026-11-15

Baseado em [estado-do-projeto.md](estado-do-projeto.md). As referências entre parênteses apontam para as seções e IDs daquele relatório: P0 a P3 vêm da §4, C1 a C11 da §5. Nenhuma spec ou card foi criado ainda; os números são sugestões e serão confirmados no `/new-spec`.

**Status (2026-11-16):** aprovadas todas, exceto a 007 (rejeitada; ver a seção dela). Os números não foram renumerados.

Prioridade:
- **Alta**: risco de segurança, número errado na tela ou base para as outras specs.
- **Média**: risco real sem dano imediato, ou entrega planejada que destrava outra.
- **Baixa**: só passa a ser necessária quando os serviços forem integrados ou publicados.

## Resumo

| # | Título | Serviços | Depende de | Prioridade |
|---|---|---|---|---|
| 001 | Swagger + OpenAPI (API como está) | Consolidator, hub | — | Alta |
| 002 | Segurança de usuários e exclusão de carteira | Consolidator, Visualizer | 001 | Alta |
| 003 | Consolidação do planejamento no hub | hub, Consolidator, Visualizer, ADC | — | Alta |
| 004 | Precificação: cotação atual e P&L | Consolidator, Visualizer | 001 | Alta |
| 005 | Datas como dia de calendário | Consolidator, Visualizer, ADC | 001 | Média |
| 006 | Unidades, moeda e data da cotação no contrato | Consolidator, Visualizer | 001, 004 | Média |
| ~~007~~ | ~~Valor justo unificado~~ (rejeitada) | — | — | — |
| 008 | Resiliência da integração com a Brapi | Consolidator, Visualizer | 001 | Média |
| 009 | Saúde do build e navegação do Visualizer | Visualizer | — | Média |
| 010 | Tipo de ativo preenchido | Consolidator | 001 | Média |
| 011 | API de leitura do ADC (FastAPI) | ADC, hub | 001, 003 | Média |
| 012 | Fechamentos diários: COTAHIST e `/v1/prices` | ADC, Consolidator | 011 | Média |
| 013 | Importação validada com a planilha real | ADC | 005 | Média |
| 014 | Conteinerização e integração local | Consolidator, Visualizer, ADC | 001 | Baixa |
| 015 | CI, E2E e cobertura | Visualizer, Consolidator, ADC | 009, 014 | Baixa |
| 016 | Agendamento e hardening do ADC | ADC | 011 | Baixa |
| 017 | Fundamentos CVM e agregações | ADC | 011 | Baixa |

Ordem sugerida, em ondas. Dentro de uma onda, as specs podem rodar em paralelo.
1. **Onda 1:** 001 e 003.
2. **Onda 2:** 002 e 004.
3. **Onda 3:** 005, 006, 008, 009 e 010.
4. **Onda 4:** 011, 012 e 013.
5. **Onda 5:** 014, 015, 016 e 017.

## Detalhe

### 001 — Swagger + OpenAPI (API como está)
- **Objetivo:** publicar o Swagger do Consolidator e gerar o primeiro `contracts/openapi.yaml` real, descrevendo a API exatamente como ela é hoje.
- **Serviços:** Consolidator (springdoc, `SecurityConfig`); hub (`contracts/`).
- **Escopo:**
  - Atualizar o springdoc de 2.5.0 para 2.8.x (a 2.5.0 é provavelmente incompatível com o Boot 3.5.6) e liberar `/v3/api-docs/**` e `/swagger-ui/**`.
  - Adicionar o esquema de segurança Bearer JWT.
  - Gerar o YAML e revisá-lo à mão em `contracts/openapi.yaml`.
  - No YAML, documentar sem mudar comportamento:
    - unidades: percentual de 0 a 100; volatilidade como fração; moeda BRL implícita;
    - formatos de data (`LocalDate` em uns campos, `java.util.Date` em outros);
    - o que significa cada campo null;
    - os dois significados de `currentValue`;
    - o formato dos erros (`{campo: msg}`, `{error}`, `{error, code}`).
  - Ter uma forma de detectar quando o código diverge do YAML (teste ou script que compara com `/v3/api-docs`).
- **Fora do escopo:** qualquer correção de comportamento. Os problemas encontrados vão para a seção "problemas conhecidos" do contrato, com link para a spec que vai corrigi-los.
- **Depende de:** nada.
- **Prioridade:** alta. `contracts/` está vazio e a fonte de verdade de fato são os DTOs Java (§5). Sem contrato, o `integration-reviewer` só compara código com código, e todas as outras specs mudariam a API sem registro. A spec também cobre C8: rotas que mudaram sem constar em plano nenhum (escopo dos proventos, `/transactions` sem filtro, `merge`).

### 002 — Segurança de usuários e exclusão de carteira
- **Objetivo:** impedir que um usuário altere ou exclua outro, e dar um comportamento definido à exclusão de carteira com ativos.
- **Serviços:** Consolidator; Visualizer (tratar 403 e 409 na exclusão).
- **Escopo:**
  - Checar o dono, ou exigir ADMIN, em `PUT/DELETE /users/{id}` (`UserResource.java:55-67`).
  - Ativar `@EnableMethodSecurity`, já que o `@PreAuthorize` de hoje não tem efeito (E2E #10).
  - Definir a exclusão de carteira com ativos: excluir tudo em cascata ou recusar com 409 (`WalletService.java:87-96`).
  - Corrigir o NPE de `POST /wallet` com `assets` nulo e validar `name` (E2E #3).
  - Achados da 001 (confirmados com a aplicação rodando em 2026-11-17):
    - `GET /users` com token válido sem ADMIN responde **401** no servidor real (confirmado em 2026-11-17), embora o `AuthFailureSemanticsTest` em MockMvc veja 403.
      - Causa provável: o 403 do Spring Security sai via `sendError`, o dispatch de ERROR para `/error` roda sem autenticação e cai no entry point 401.
      - Isso viola o ADR 002: o front desloga o usuário.
      - Pela leitura do código, afeta todo erro enviado por `sendError`: 404 de rota inexistente, 405, 415 e `@RequestParam` obrigatório ausente. O 404 de recurso (`EntityNotFoundException`) não é afetado. Confirmar em servidor real.
      - Correção esperada: permitir `DispatcherType.ERROR` no `SecurityConfig` e cobrir com teste em servidor real (`RANDOM_PORT`), não só MockMvc. Incluir o caso do Swagger desligado em `prod`, que deve dar 404.
    - `/h2-console/**` é público no `SecurityConfig` em todos os perfis. Fechar fora do dev.
    - Login com credencial inválida responde **400**, não 401.
    - E-mail duplicado em `POST /users` devolve 400 com a mensagem crua do banco em `{error}`.
  - Atualizar o contrato.
- **Depende de:** 001, para a mudança entrar no contrato.
- **Prioridade:** alta. É uma falha de segurança real (P0 §4.2) e a exclusão provavelmente falha por FK (§4.3).

### 003 — Consolidação do planejamento no hub
- **Objetivo:** reunir todo o planejamento no hub e deixar nos repositórios dos serviços só o que é operacional (`CLAUDE.md`, `README.md`).
- **Serviços:** hub (`specs/`, `docs/adr/`, `docs/archive/`); Consolidator, Visualizer e ADC, de onde os arquivos saem e onde as referências mudam.
- **Escopo:**
  - Arquivar no hub, em `docs/archive/`, os 12 planos do inventário (§3.1), com um cabeçalho "histórico" em cada.
  - Extrair as decisões ainda válidas (D1–D13 do roadmap, D1–D31 do ADC, menos as redundantes e obsoletas) para ADRs curtos.
  - Levar as pendências abertas (`ENHANCEMENTS.md`, E2E #3 e #10, pendências do ADC) para o backlog.
  - Unificar a numeração de fases: passa a valer a numeração das specs.
  - Reescrever a parte de estado do `AGENTS.md` do Consolidator.
  - Revisar a regra `*.md` do `.gitignore` do Consolidator.
  - Versionar o `CLAUDE.md` do ADC.
  - Atualizar os links que apontam para `../ADC_PLAN.md`.
- **Depende de:** nada. Pode rodar junto com a 001.
- **Prioridade:** alta. Há 4 numerações de fase sobrepostas, conflitos diretos (`daily_close`, status do Consolidator, configuração de ambiente do front) e o plano mestre do ADC está fora do git (§3.2 e §3.3). Você já decidiu centralizar no hub.

### 004 — Precificação: cotação atual e P&L
- **Objetivo:** fazer toda tela que mostra cotação e P&L usar o preço atual calculado pelo backend.
- **Serviços:** Consolidator, Visualizer.
- **Escopo:**
  - C1: `AssetResponseDTO.currentValue` é congelado no cadastro. Decidir entre renomear o campo, removê-lo ou atualizá-lo na leitura.
  - Fazer `asset-list`, `fair-value` e `asset-form` usarem `currentPrice` do summary.
  - C2: o dashboard e `sumPortfolioTotals` devem usar `PortfolioAggregate` (`totalProfitLoss` e `pricedInvested`) em vez de calcular no front.
  - Remover a conversão de null em 0 em `PortfolioCard`.
  - `fairValue` do ativo: deixar de calcular Graham automático no cadastro e passar a exibir o último valuation calculado pelo usuário, com o método (Graham, Bazin ou DCF). Quando não houver valuation, o campo vem null.
- **Depende de:** 001. O nome e o significado de `currentValue` mudam no contrato.
- **Prioridade:** alta. C1 é a única quebra da auditoria: o usuário vê P&L errado. C2 inventa prejuízo para ativo sem cotação.

### 005 — Datas como dia de calendário
- **Objetivo:** usar `yyyy-MM-dd` em todas as datas de calendário da API, nos dois sentidos.
- **Serviços:** Consolidator, Visualizer, ADC.
- **Escopo:**
  - C3: o ADC passa a enviar `transactionDate` e `acquisitionDate` como `yyyy-MM-dd` (`core/utils.py:192`, `client.py:97`, `test_client.py:59`).
  - C6: `paymentDate` e `exDate` viram `LocalDate`. `computedAt` vira ISO com fuso explícito.
  - Corrigir `formatDate` no `fair-value`.
  - Trocar os `ZoneId.systemDefault()` restantes (`PortfolioSnapshotService:44`, `DividendService:338/363/373`, `ValuationService:126`) por `TradingDay`.
- **Depende de:** 001.
- **Prioridade:** média. Hoje funciona porque o Jackson é tolerante, mas não há teste E2E que prove isso. O bug de "um dia antes" já foi corrigido em transações e continua em proventos e valuation.

### 006 — Unidades, moeda e data da cotação no contrato
- **Objetivo:** deixar explícitos na API a moeda, o momento da cotação e a escala dos percentuais.
- **Serviços:** Consolidator, Visualizer.
- **Escopo:**
  - C4: padronizar ou marcar a escala da volatilidade em relação aos outros percentuais.
  - C7: expor `currency` e o momento da cotação (`regularMarketTime`) no summary.
  - Nulidade no contrato: o springdoc 2.8 com OpenAPI 3.1 não emite `nullable` nem `required` nas respostas, e o null só aparece em prosa. Decidir se o contrato passa a declarar isso por tipo (`type: [x, "null"]`, `required`), o que um gerador de cliente entende. Campos afetados citados na 001: `name` do ativo e `formula` do valuation.
  - Lacunas de descrição apontadas na revisão de integração da 001, adiadas pelo usuário em 2026-11-17:
    - `POST /assets` com `amount` e sem `unitPrice` cria um ativo zerado, e o `amount` é ignorado. O ADC e o Visualizer dependem disso.
    - A lista de rotas públicas no `info.description` omite `/h2-console/**`, `OPTIONS /**` e o padrão `POST /users/**`.
  - C10: alinhar a obrigatoriedade dos campos no TS com o Java; usar `Long` em `walletId` no `AssetCreateDTO`; tornar `totalInvestedValue` não opcional.
- **Depende de:** 001 e 004, que mexem nos mesmos DTOs.
- **Prioridade:** média. Não há erro visível hoje, mas o pipe de percentual aplicado à volatilidade erraria por um fator de 100, e o usuário não sabe de quando é a cotação.

### 007 — Valor justo unificado (REJEITADA em 2026-11-16)
> Decisão do usuário: o valor justo deve ser calculado pela metodologia que o usuário escolher (Graham, Bazin ou fluxo de caixa), como o `ValuationService` já faz. Não haverá um valor justo único. O `fairValue` automático do ativo (Graham com `PE*EPS`) é documentado como está na 001. Depois, na 004, passa a exibir o último valuation calculado pelo usuário, junto com o método usado (decisão de 2026-11-16).

- **Objetivo:** ter um único cálculo de Graham, correto e atualizado.
- **Serviços:** Consolidator, Visualizer.
- **Escopo:**
  - C5: o `fairValue` do cadastro usa `PE*EPS`, quando a fórmula correta é `EPS*BVPS`, e ele envelhece. Passar a derivar do `ValuationService` ou deixar de expor esse campo no ativo.
  - Decidir se `fairValue` entra no `PortfolioSummaryDTO`, dívida citada no roadmap.
- **Depende de:** 001.
- **Prioridade:** média. A fórmula errada afeta uma decisão de investimento, mas existe a tela de valuation como alternativa.

### 008 — Resiliência da integração com a Brapi
- **Objetivo:** fazer uma falha da Brapi virar aviso por ativo, e não erro 400 na carteira inteira.
- **Serviços:** Consolidator; Visualizer (exibir o aviso).
- **Escopo:**
  - ENHANCEMENTS #1: tratar falhas em `getAssetData` e mapear erro de terceiro para 502/503.
  - Configurar timeout no `RestTemplate` e tornar `brapi.base-url` configurável.
  - Criar cache com TTL e remover o `priceCache` local (#2 e #5).
  - Escrever o teste de `getAssetData`, que falta.
  - Avaliar depois: semáforo, batching e métricas (#3, #4 e #6).
- **Depende de:** 001, porque os códigos de erro novos entram no contrato.
- **Prioridade:** média. É bug conhecido e parcialmente corrigido. Uma oscilação da Brapi derruba o resumo.

### 009 — Saúde do build e navegação do Visualizer
- **Objetivo:** fazer o build de produção, o lint e a navegação ADMIN funcionarem.
- **Serviços:** Visualizer.
- **Escopo:**
  - `fileReplacements` no `angular.json`.
  - ESLint e o target `lint`, que o `CLAUDE.md` do Visualizer exige.
  - Corrigir o link "Usuários": criar a rota com `AdminGuard` e `GET /users`, ou remover o link.
  - Fechar a fase 6.1: mensagens do `ErrorInterceptor` em português e `role="status"` nos spinners.
  - Remover o `.bak2` e o `getSnapshots` sem uso.
- **Depende de:** nada.
- **Prioridade:** média. O build de produção aponta para localhost, mas ainda não há deploy. O lint quebrado impede o subagente de cumprir o próprio `CLAUDE.md`.

### 010 — Tipo de ativo preenchido
- **Objetivo:** preencher `Asset.assetType` (ação, FII etc.) a partir da Brapi, no cadastro e com backfill dos ativos que já existem.
- **Serviços:** Consolidator.
- **Escopo:** preencher no cadastro, fazer backfill por migration ou job, e expor o campo no DTO se for útil ao front.
- **Depende de:** 001.
- **Prioridade:** média. Hoje a regra "FII usa 3 meses" do histórico e da volatilidade (Fases J e K, D13) nunca é aplicada, porque o campo nunca é preenchido.

### 011 — API de leitura do ADC (FastAPI)
- **Objetivo:** expor por uma API somente leitura os dados que o coletor já grava.
- **Serviços:** ADC; hub (`contracts/adc.openapi.yaml`).
- **Escopo:** Fase 6 do ADC: `/health`, autenticação `X-ADC-Token`, `/v1/companies/{ticker}` com market, indicators, statements e dividends, e o OpenAPI da API no hub.
- **Depende de:** 001, para seguir o mesmo padrão de contrato, e 003, porque o plano do ADC precisa estar no hub.
- **Prioridade:** média. É o próximo passo declarado do ADC. Hoje os dados coletados não têm consumidor.

### 012 — Fechamentos diários: COTAHIST e `/v1/prices`
- **Objetivo:** trocar a Brapi pelo ADC como fonte dos fechamentos históricos.
- **Serviços:** ADC (coletor COTAHIST, ajuste por FATCOT, `/v1/prices`); Consolidator (cliente do ADC em `PortfolioHistoryService.loadCloses`).
- **Escopo:** Fases 10 e 9 do ADC e 6.7.3 do Consolidator, contrato em `contracts/`, e golden test de split.
- **Depende de:** 011.
- **Prioridade:** média. C11: os dois lados dão o contrato como "congelado", mas nenhum o implementou. A tabela `daily_close` existe e está vazia.

### 013 — Importação validada com a planilha real
- **Objetivo:** concluir o MVP do importador validando com a sua planilha real.
- **Serviços:** ADC.
- **Escopo:**
  - Etapa 7.7, com execução ponta a ponta contra o Consolidator local.
  - Etapa 7.8: documentar o fluxo no contrato, no lugar do `BACKEND_ROADMAP`.
  - Remover `auth.resolve_credentials`, que não é usado.
- **Depende de:** 005, para as datas já irem no formato certo.
- **Prioridade:** média. Bloqueia o fechamento do MVP do ADC e depende de você para a planilha.

### 014 — Conteinerização e integração local
- **Objetivo:** subir os três serviços juntos em containers.
- **Serviços:** todos.
- **Escopo:**
  - Completar o `docker-compose.yml` do Consolidator: `BRAPI_TOKEN`, volume, portas e `depends_on`.
  - Liberar `/actuator/health`.
  - Validar as migrations em PostgreSQL real.
  - Criar o `logback-spring.xml`.
  - Configurar o CORS por propriedade.
  - Dockerfile e nginx do Visualizer, resolvendo o conflito do prefixo `/api` (C9).
  - Serviços do ADC no compose.
- **Depende de:** 001.
- **Prioridade:** baixa. Rebaixada por decisão sua: o Consolidator roda localmente e nunca foi conteinerizado. Só vira necessária quando os três serviços forem integrados.

### 015 — CI, E2E e cobertura
- **Objetivo:** ter um pipeline que rode testes, lint e verificação de contrato em cada mudança.
- **Serviços:** Visualizer (Phase 7: CI, Playwright, limiar de cobertura); Consolidator; ADC (meta de cobertura de 80%).
- **Escopo:** incluir no pipeline a verificação de divergência do contrato criada na 001.
- **Depende de:** 009 (lint) e 014 (ambiente).
- **Prioridade:** baixa. Ainda não há CI em nenhum serviço, mas há testes locais em todos.

### 016 — Agendamento e hardening do ADC
- **Objetivo:** rodar a coleta sem execução manual.
- **Serviços:** ADC.
- **Escopo:** Fase 8: agendamento do Fundamentus e do COTAHIST, lock de job no Postgres e logs em JSON; incluir a página `resultados_trimestrais.php`.
- **Depende de:** 011, e também 012 para o COTAHIST.
- **Prioridade:** baixa. Hoje a coleta é só por CLI manual, o que basta para o uso atual.

### 017 — Fundamentos CVM e agregações
- **Objetivo:** completar a base fundamentalista do ADC com os dados da CVM.
- **Serviços:** ADC.
- **Escopo:**
  - Fase 4 (CVM DFC, `companies`, `source_aliases`).
  - Fase 5 (FCF, Dívida/PL, margens).
  - Decidir antes se a agregação fica no ADC ou no Consolidator (§24.7 do plano).
- **Depende de:** 011.
- **Prioridade:** baixa. É expansão de escopo. Nada atual depende disso.

## Achados que não viraram spec
- **Comentários de código citando planos arquivados (spec 003, 2026-11-18).** A 003 não podia alterar código, então sobraram estas referências:
  - Consolidator, para `BACKEND_ROADMAP.md`: `AssetCreateDTO.java:15`, `AssetUpdateDTO.java:12`, `WalletDTO.java:11` e `Wallet.java:37`.
  - Visualizer, para `E2E_Auth_Fixes.md`: `asset-form.ts:255` e `wallet.service.ts:53`.
  - ADC, "Fase 10": `db/models.py:225`.

  Correção: trocar pelos ADRs do hub, num card avulso por serviço ou junto da próxima spec que mexer nesses arquivos.
- **H2 do dev perde as tabelas quando fica parado (2026-11-18).** `application.properties` usa `jdbc:h2:mem:testdb` sem `DB_CLOSE_DELAY=-1`. Quando o pool do Hikari fecha todas as conexões (`maxLifetime` de 30 min), o H2 descarta o banco e as requisições seguintes dão "Table USERS not found". Correção de uma linha no Consolidator: card avulso. Enquanto isso, suba o dev com `SPRING_DATASOURCE_URL="jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1"`.
- **`PROMPT_NOVA_SESSAO.txt`:** já excluído.
- **Rotas não consumidas** (`GET/PUT/DELETE /users*`, `backfill`): ficam só documentadas na 001. A 009 decide se o front passa a usar `GET /users`.
- **Opcionais do front** (P&L por ativo, `MatSort`/paginator, transaction-detail): vão como cards soltos no ClickUp, sem spec.
- **pgAdmin (6.1 do Consolidator):** descartado, exceto se você quiser.
