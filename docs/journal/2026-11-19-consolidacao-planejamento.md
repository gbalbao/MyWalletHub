# Planejamento num lugar só

- **Spec:** `specs/003-consolidacao-planejamento.md`
- **Serviços:** hub, Consolidator, Visualizer, ADC
- **Data:** 2026-11-19

## Problema
O MyWallet tinha 12 arquivos de plano espalhados pelos três projetos e por uma pasta solta. Cada um contava a história de um jeito, com quatro numerações de "fase" diferentes. Alguns se contradiziam e outros estavam desatualizados havia meses. O plano do coletor de dados nem tinha histórico de versões. Saber o que já estava pronto e o que vinha depois exigia uma investigação.

## Solução
Todo o planejamento agora fica no repositório central (o hub):
- **Specs:** uma por funcionalidade, com o quê e o porquê.
- **ADRs:** as decisões de design, registradas em `docs/adr/`.
- **Arquivo histórico:** os planos antigos, guardados sem nenhuma alteração.
- **ClickUp:** o andamento.

Os três projetos guardam só as instruções de uso. As "fases" antigas foram aposentadas e o trabalho passou a ser identificado pelo número da spec. Uma tabela mostra a equivalência entre as fases antigas e as specs.

## Benefício
- Há uma resposta única para "o que já existe e o que vem depois".
- Nenhum conteúdo antigo se perdeu: tudo está arquivado, e as tarefas ainda abertas foram classificadas como spec, futuro card ou descartadas com motivo.
- Os arquivos de plano que estavam fora de qualquer controle de versão agora têm histórico.

## Aprendizado
- **Copiar, conferir, só então apagar.** Os arquivos sem controle de versão só foram removidos depois que a cópia arquivada foi conferida byte a byte.
- **A causa da bagunça era uma regra.** Uma regra de configuração no repositório do servidor fazia todos os documentos dele ficarem sem versão. Tirar essa regra resolveu a causa, não só o sintoma.

## Vale post
Sim. A dor de "planos espalhados com várias numerações" é comum em projeto pessoal que cresce, e o antes e depois é fácil de mostrar.

## Material
- Diagrama antes e depois: arquivos espalhados por quatro lugares contra uma estrutura única no hub (`specs/`, `docs/adr/`, `docs/archive/`, ClickUp).
- Print da tabela de equivalência entre as fases antigas e as specs.
- Print do quadro do ClickUp com as listas por serviço.

## Pendências
- Nenhuma da spec. Os itens que restaram dos planos antigos estão em `docs/archive/pendencias.md`, para virar cards.
