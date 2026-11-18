# ADR 014 — Planejamento centralizado no hub

- **Status:** aceita (2026-11-15), em execução na spec 003
- **Origem:** auditoria `docs/estado-do-projeto.md` §3 e decisão do usuário
- **Serviços:** todos

## Contexto
O planejamento estava em 10 arquivos espalhados por três repositórios e pela raiz de `Projetos\`, alguns fora do git, com 4 numerações de fase e conflitos entre si.

## Decisão
| O quê | Onde |
|---|---|
| O quê e porquê de cada feature | `specs/NNN-*.md` |
| API entre serviços | `contracts/` |
| Decisões de design | `docs/adr/` |
| Planos antigos | `docs/archive/` (somente leitura) |
| Andamento e backlog | ClickUp, pasta MyWallet, uma lista por serviço mais a lista Hub |

Os repositórios dos serviços guardam só `CLAUDE.md`, `AGENTS.md` e `README.md` operacionais. A numeração de fases antiga foi aposentada; agora vale o número da spec.
