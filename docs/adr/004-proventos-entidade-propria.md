# ADR 004 — Proventos em entidade própria, nunca como tipo de transação

- **Status:** aceita, implementada
- **Origem:** BACKEND_ROADMAP D10
- **Serviços:** Consolidator

## Decisão
Proventos ficam em `DividendReceipt`, com origem `BRAPI` ou `MANUAL`. Eles não são um `TransactionType`.

## Por quê
Provento é uma entrada de caixa que não altera posição nem custo. Um tipo `DIVIDEND` no ledger cairia fora dos ramos BUY/SELL do cálculo de posição, e a posição ficaria certa só por acidente.
