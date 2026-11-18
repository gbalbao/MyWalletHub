# ADR 012 — Fechamentos diários do COTAHIST e contrato `/v1/prices`

- **Status:** aceita, **não implementada** (specs 012 e 016). A tabela `daily_close` existe no ADC e está vazia
- **Origem:** ADC_PLAN D22–D26 e §26 (contrato `/v1/prices`)
- **Serviços:** ADC (produtor), Consolidator (consumidor)

## Decisão
- `daily_close` guarda o fechamento bruto (`close`, para o valor de mercado do dia) e o ajustado (`adjusted_close`, para a volatilidade). Splits e bonificações são ajustados pelo `FATCOT`; proventos **não** entram no ajuste, e o contrato precisa dizer isso.
- O universo é o arquivo COTAHIST inteiro, não só os tickers das carteiras, para não acoplar o ADC ao ledger.
- Carga inicial de 5 anos e depois um job diário após o fechamento, com upsert idempotente por `(ticker, trade_date)`.
- Contrato `/v1/prices`: lote de até 20 tickers; ticker desconhecido vai para `missing` sem derrubar o lote; decimais como string; dias sem pregão não são preenchidos.

## Observação
O contrato foi descrito no plano como "congelado", mas não existe em `contracts/`. Ele entra lá na spec 012, antes da implementação.
