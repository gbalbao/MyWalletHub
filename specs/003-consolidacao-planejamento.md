# 003 — Consolidação do planejamento no hub

## Por quê
A auditoria (`docs/estado-do-projeto.md` §3) encontrou problemas na documentação de planejamento:
- 12 arquivos espalhados nos três repositórios e na raiz de `Projetos\`;
- 4 numerações de fase sobrepostas;
- conflitos diretos entre planos (`daily_close`, status do Consolidator, configuração de ambiente do front);
- o plano mestre do ADC fora de qualquer git;
- a regra `*.md` no `.gitignore` do Consolidator, que deixa quase todos os planos dele sem versão.

Em 2026-11-15, o usuário decidiu centralizar todo o planejamento no hub.

## Objetivo
Uma única fonte de planejamento:
- `specs/` para o quê e o porquê de cada feature;
- `contracts/` para a API;
- `docs/adr/` para as decisões;
- `docs/archive/` para os planos históricos;
- ClickUp para o andamento e o backlog.

Nos repositórios dos serviços fica só o operacional: `CLAUDE.md` e `README.md`. Nenhum conteúdo de plano se perde; ele é arquivado.

## Critérios de aceite
- [ ] Os 10 arquivos de plano listados em "Inventário" existem em `docs/archive/<serviço>/` no hub, com o conteúdo original sem edição e um cabeçalho de 3 linhas: "Histórico, arquivado em AAAA-MM-DD; origem: <caminho>; substituído por: <spec/ADR/card>". O `HELP.md` é só excluído.
- [ ] Nenhum desses 11 arquivos (os 10 planos e o `HELP.md`) permanece no local de origem. A remoção só acontece depois que a cópia arquivada for conferida.
- [ ] `docs/adr/` contém um ADR curto para cada decisão ainda válida extraída do `BACKEND_ROADMAP.md` (D1–D13) e do `ADC_PLAN.md` (D1–D31). As obsoletas e redundantes (ex.: ADC D16, D17, D20; roadmap D5) aparecem num índice `docs/adr/README.md` como "descartada", com o motivo.
- [ ] Toda pendência aberta citada nos planos arquivados está em uma de três listas, sem item órfão: (a) coberta por spec do backlog (`docs/backlog-proposto.md`); (b) em `docs/archive/pendencias.md`, para virar card; (c) descartada, com motivo.
- [ ] `docs/adr/README.md` registra que a numeração de fases antiga (Fases 0–6, A–K, 6.x, ADC 0–10) foi aposentada e que vale o número da spec, com uma tabela de equivalência das fases antigas para as specs.
- [ ] Nenhum `CLAUDE.md`, `README.md` ou `AGENTS.md` dos serviços aponta para arquivo inexistente. Uma busca por `ADC_PLAN`, `BACKEND_ROADMAP`, `IMPLEMENTATION_PLAN`, `SESSION_PLAN`, `E2E_Auth_Fixes` e `ENHANCEMENTS` nos três repositórios só encontra referências que apontam para o hub.
- [ ] O `AGENTS.md` do Consolidator não tem mais seção de estado de fases. Ficam só as informações operacionais ainda verdadeiras, conferidas contra o código.
- [ ] A regra `*.md` saiu do `.gitignore` do Consolidator, e os `.md` operacionais que restarem estão versionados.
- [ ] O `CLAUDE.md` do ADC está versionado.
- [ ] O `CLAUDE.md` do hub explica onde vive cada tipo de documento (o que já está lá é revisado; não duplicar).
- [ ] Nenhum código de aplicação foi alterado nos três serviços: o diff de cada repositório contém só `.md`, `.html` e `.gitignore`.

## Inventário (arquivos a arquivar)
| Origem | Destino |
|---|---|
| `consolidator/implementation_plan.html` | `docs/archive/consolidator/` |
| `consolidator/.opencode/plans/implementation_plan.md` | `docs/archive/consolidator/` |
| `consolidator/consolidator/BACKEND_ROADMAP.md` | `docs/archive/consolidator/` (depois de extrair os ADRs) |
| `consolidator/consolidator/E2E_Auth_Fixes.md` | `docs/archive/consolidator/` |
| `consolidator/consolidator/ENHANCEMENTS.md` | `docs/archive/consolidator/` (pendências vão para a spec 008 ou para cards) |
| `visualizer/IMPLEMENTATION_PLAN.md` | `docs/archive/visualizer/` |
| `visualizer/frontend-plan.md` | `docs/archive/visualizer/` |
| `visualizer/frontend-plan.html` | `docs/archive/visualizer/` |
| `Projetos/ADC_PLAN.md` | `docs/archive/adc/` (depois de extrair os ADRs) |
| `Projetos/SESSION_PLAN.md` | `docs/archive/geral/` |
| `consolidator/consolidator/HELP.md` | Excluir (README padrão do Spring Initializr, sem conteúdo de plano) |

Ficam fora do arquivamento:
- os `CLAUDE.md` e `README.md` dos serviços (operacionais), que só são ajustados;
- o `AGENTS.md` do Consolidator, que é reescrito;
- `Projetos/Wallet Consolidator/` (projeto antigo, não faz parte do MyWallet).

## Mudanças de contrato
Nenhuma.

## Tarefas por serviço
### Hub (arquiteto)
- [ ] Criar `docs/archive/` com a estrutura por serviço e copiar os 10 arquivos com o cabeçalho de histórico.
- [ ] Extrair os ADRs do `BACKEND_ROADMAP.md`, conferindo cada decisão contra o código, e registrar as descartadas no índice.
- [ ] Extrair os ADRs do `ADC_PLAN.md` do mesmo jeito, incluindo o contrato `/v1/prices` (§26) como insumo para as specs 011 e 012, ainda não como contrato.
- [ ] Levantar as pendências abertas dos planos arquivados e classificá-las em spec existente, `docs/archive/pendencias.md` ou descartada.
- [ ] Escrever `docs/adr/README.md`: índice, convenção, tabela de equivalência das fases antigas para as specs.
- [ ] Revisar o `CLAUDE.md` do hub para dizer onde vive cada tipo de documento.
### Consolidator
- [ ] Remover os 5 planos e o `HELP.md` da origem, depois da conferência do arquivamento.
- [ ] Reescrever o `AGENTS.md`: tirar a seção de fases e corrigir o que contradiz o código (ex.: `ddl-auto`, lista de controllers, quantidade de testes, data da transação).
- [ ] Tirar `*.md` do `.gitignore`, revisar o `CLAUDE.md` (a regra "atualizar o status no AGENTS.md" deixa de existir) e apontar para o hub.
### Visualizer
- [ ] Remover os 3 planos da origem, depois da conferência do arquivamento.
- [ ] Revisar o `CLAUDE.md` e o `README.md` do app (hoje um boilerplate do Angular CLI) para apontar para o hub.
### ADC
- [ ] Atualizar o `CLAUDE.md` e o `README.md`, que hoje fazem link para `../ADC_PLAN.md`, para apontar para o hub, e versionar o `CLAUDE.md`.
### Raiz `Projetos\` (arquiteto)
- [ ] Remover `ADC_PLAN.md` e `SESSION_PLAN.md` só depois que o usuário confirmar que commitou a cópia no hub. Essa pasta não tem git, então a remoção é irreversível.

> Execução: as tarefas de Consolidator, Visualizer e ADC são delegadas aos subagentes do serviço com `model: opus` e `effort: medium`.

## Fora de escopo
- Corrigir qualquer código ou comportamento apontado nos planos: isso fica com as specs do backlog.
- Criar no ClickUp os cards das pendências sem spec: eles entram no `/spec-to-cards` ou numa etapa própria.
- Reescrever o conteúdo dos planos arquivados (eles ficam como estão, só com o cabeçalho).
- Apagar o projeto antigo `Projetos/Wallet Consolidator/`.

## Riscos e dúvidas
- **Decidido (2026-11-16):** `ADC_PLAN.md` e `SESSION_PLAN.md` não estão em nenhum git. O usuário commita a cópia no hub antes, e só então os originais são removidos.
- **Decidido (2026-11-16):** os subagentes de cada serviço (`consolidator-dev`, `visualizer-dev`, `adc-dev`) fazem as mudanças nos próprios repositórios. Para este card, eles são invocados com o modelo **Opus** e esforço **medium**. O arquiteto cuida só do hub e da raiz.
- **Planos do Consolidator fora do git:** por causa do `*.md` no `.gitignore`, os planos não têm histórico. A cópia no hub vira a única versão.
- **Granularidade dos ADRs:** são 13 decisões no roadmap e 31 no ADC. Algumas viram ADRs separados, outras podem ser agrupadas. Critério proposto: ADR separado só quando a decisão ainda restringe código futuro; as demais entram como linha no índice.
- **Ordem com a spec 001:** a 001 não depende desta, mas a 003 vai citar as specs do backlog. Se a numeração do backlog mudar, a tabela de equivalência precisa ser ajustada.
- **Regras nos `CLAUDE.md` dos serviços:** se os subagentes tiverem instruções que mandam atualizar planos locais, elas precisam sair, senão os planos voltam a ser criados nos repositórios.

## ClickUp
Pasta MyWallet. Os cards ficam na lista do serviço; as dependências estão cadastradas no ClickUp.
- [[Hub] 003 — Arquivar planos, ADRs e pendências no hub](https://app.clickup.com/t/1dfhfaqc8a5)
- [[Consolidator] 003 — Remover planos locais e revisar AGENTS/CLAUDE/.gitignore](https://app.clickup.com/t/1dfhfaqc8a6): depende do card do Hub
- [[Visualizer] 003 — Remover planos locais e apontar docs para o hub](https://app.clickup.com/t/1dfhfaqc8a7): depende do card do Hub
- [[ADC] 003 — Apontar docs para o hub e versionar CLAUDE.md](https://app.clickup.com/t/1dfhfaqc8a8): depende do card do Hub
