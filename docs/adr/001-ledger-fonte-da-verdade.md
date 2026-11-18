# ADR 001 — O ledger de transações é a fonte da verdade da posição

- **Status:** aceita, implementada
- **Origem:** BACKEND_ROADMAP D1, D2 (arquivado em `docs/archive/consolidator/`)
- **Serviços:** Consolidator, Visualizer, ADC

## Contexto
A posição de um ativo (quantidade, preço médio, total investido) era editada no próprio ativo e também derivada das transações. Isso criava duas verdades.

## Decisão
- A posição é sempre recalculada pelo replay do ledger (`AssetPositionCalculator`), em ordem cronológica.
- Cadastrar um ativo com preço e data cria uma transação BUY de abertura.
- O formulário de ativo edita só o `ticker`. Quantidade, preço e data mudam apenas por transações.

## Consequências
- Editar ou excluir uma transação recalcula a posição inteira.
- Importadores (ADC) precisam enviar transações em ordem cronológica (ADR 011).
