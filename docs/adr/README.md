# Decisões de arquitetura (ADR)

Cada ADR registra uma decisão que ainda restringe o código ou o planejamento. Decisões que não restringem mais nada ficam só como linha neste índice. Formato: `NNN-titulo.md`, curto, com status, origem, serviços afetados e decisão. Para mudar uma decisão, crie um ADR novo que substitui o antigo e atualize o status do antigo. Não reescreva o histórico.

## Índice

| ADR | Decisão | Status |
|---|---|---|
| [001](001-ledger-fonte-da-verdade.md) | O ledger de transações é a fonte da verdade da posição | Implementada |
| [002](002-status-http-e-posse.md) | 404/400/403/401 e checagem de posse no serviço | Implementada, exceto `/users` (spec 002) |
| [003](003-schema-por-flyway.md) | Schema versionado por Flyway, `validate` em todo perfil | Implementada |
| [004](004-proventos-entidade-propria.md) | Proventos em entidade própria | Implementada |
| [005](005-valor-justo-por-metodo.md) | Valor justo pelo método que o usuário escolher | Parcial (spec 004) |
| [006](006-indisponibilidade-de-terceiros.md) | Indisponibilidade de fonte externa é estado, não erro | Parcial (spec 008) |
| [007](007-adc-isolado-api-first.md) | ADC separado, banco próprio, integração só pela API | Implementada |
| [008](008-credenciais-so-em-memoria.md) | Credenciais e token do ADC só em memória | Implementada |
| [009](009-fontes-de-dados.md) | Fonte de cada tipo de dado de mercado | Parcial (specs 012, 017) |
| [010](010-adc-fonte-nao-calcula-valuation.md) | ADC é fonte de dados; valuation fica no Consolidator | Vigente |
| [011](011-importador-pela-api.md) | Importador pela API pública, em ordem cronológica | Implementada (spec 013 valida) |
| [012](012-precos-historicos-cotahist.md) | COTAHIST, `daily_close` e contrato `/v1/prices` | Não implementada (specs 012, 016) |
| [013](013-modelo-dados-fundamentus.md) | Dados do Fundamentus por ticker; proventos por data-com | Implementada |
| [014](014-planejamento-centralizado-no-hub.md) | Planejamento centralizado no hub | Em execução (spec 003) |

## Decisões dos planos arquivados

Todas as decisões numeradas dos dois planos arquivados aparecem abaixo, com o destino de cada uma.

### `BACKEND_ROADMAP.md` (Consolidator)
| Decisão | Destino |
|---|---|
| D1, D2 | ADR 001 |
| D3: `currentValue` mantém o nome e a semântica de preço unitário | Vigente até a spec 004, que revisa o campo. Sem ADR, porque é dívida e não princípio |
| D4: Fases D e E depois de A, B e C | Descartada: ordem já cumprida |
| D5: `transactionDate` continua `java.util.Date` | Descartada: o campo virou `LocalDate` (Fase 6.6) |
| D6, D7, D8 | ADR 002 |
| D9 | ADR 003 |
| D10 | ADR 004 |
| D11 | ADR 005 |
| D12, D13 | ADR 006 |

### `ADC_PLAN.md` (ADC)
| Decisão | Destino |
|---|---|
| D1: nome "ADC (Asset Data Collector)" | Vigente, sem ADR |
| D2, D4, D5, D31 | ADR 007 |
| D3, D12: Python, FastAPI, pandas, PostgreSQL | Vigente, sem ADR: a stack está no `CLAUDE.md` do ADC |
| D6, D15 | ADR 008 |
| D7, D8, D9, D13, D14 | ADR 011 |
| D10: corretagem fora do MVP | Vigente; a pendência está em `docs/archive/pendencias.md` |
| D11, D22, D30 | ADR 009 |
| D16, D17 | Absorvidas: repetiam a D11 (ADR 009) |
| D18, D19 | ADR 010 |
| D20: banco e API só depois da 7.7 | Descartada: a ordem foi invertida e o banco já existe |
| D21: operação local com Docker Compose | Vigente, sem ADR; execução na spec 014 |
| D23, D24, D25, D26 | ADR 012 |
| D27, D28, D29 | ADR 013 |

## Numeração de fases aposentada

Desde 2026-11-17, o trabalho é identificado pelo **número da spec** (`specs/NNN-*.md`). As numerações antigas (Fases 0–6 do Consolidator, Fases A–K e "0" do roadmap, 6.x do Visualizer, Fases 0–10 do ADC) aparecem só nos planos arquivados. A tabela abaixo diz para onde foi cada uma.

| Fase antiga | Plano | Situação | Continua em |
|---|---|---|---|
| 0–3 (limpeza, JWT, transações, consolidação) | `implementation_plan.html` | Concluídas | — |
| 4 (testes e polimento) | `implementation_plan.html` | Concluída; o Swagger ficou pendente | 001 |
| 5 (persistência e Docker) | `implementation_plan.html` | Parcial | 014 |
| 6.1 (pgAdmin) | `implementation_plan.html` | Descartada | — |
| A–I, K | `BACKEND_ROADMAP.md` | Concluídas | — |
| 0 (Flyway) | `BACKEND_ROADMAP.md` | Concluída; falta validar em PostgreSQL | 014 |
| J (evolução patrimonial) | `BACKEND_ROADMAP.md` | Parcial: `assetType` | 010 |
| Phases 2–5, 8 | visualizer `IMPLEMENTATION_PLAN.md` | Concluídas | — |
| 6.1 (polish) | visualizer `IMPLEMENTATION_PLAN.md` | Parcial | 009 |
| 6.2–6.6, 6.7.1, 6.7.2 | visualizer e `.opencode` | Concluídas; restos de fuso horário | 005 |
| 6.7.3 (fechamentos via ADC) | visualizer e `.opencode` | Não feita | 012 |
| Phase 7 (deploy e tooling) | visualizer `IMPLEMENTATION_PLAN.md` | Só Vitest | 009, 014, 015 |
| ADC 0–2 | `ADC_PLAN.md` | Concluídas | — |
| ADC 3 (Fundamentus) | `ADC_PLAN.md` | Concluída; faltam os resultados trimestrais | 016 |
| ADC 4, 5 (CVM, agregações) | `ADC_PLAN.md` | Não feitas | 017 |
| ADC 6 (API) | `ADC_PLAN.md` | Não feita | 011 |
| ADC 7 (importador) | `ADC_PLAN.md` | Código pronto; faltam 7.7 e 7.8 | 013 |
| ADC 8 (agendamento) | `ADC_PLAN.md` | Não feita | 016 |
| ADC 9, 10 (cliente no Consolidator, COTAHIST) | `ADC_PLAN.md` | Não feitas | 012 |

As pendências de cada fase estão em [`docs/archive/pendencias.md`](../archive/pendencias.md).
