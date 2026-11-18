# ADR 011 — O importador usa a API pública do Consolidator, em ordem cronológica

- **Status:** aceita, implementada (validação com a planilha real pendente, spec 013)
- **Origem:** ADC_PLAN D7, D8, D9, D13, D14
- **Serviços:** ADC, Consolidator

## Decisão
- A planilha tem as abas `Compras` e `Vendas`, detectadas sem diferenciar maiúsculas de minúsculas.
- Compras e vendas são unidas, ordenadas por data crescente e enviadas uma a uma pelo `POST /transactions` existente. Um `POST /import/ledger` dedicado fica para depois.
- Ativo ausente é criado zerado (`{ticker, walletId, amount: 1}`). Se o Consolidator recusar, a primeira compra vira a abertura.

## Consequências
- O importador depende do contrato de `/assets` e `/transactions`. A divergência de formato de data (C3) é corrigida na spec 005.
