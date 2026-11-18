# ADR 013 — Dados do Fundamentus chaveados por ticker

- **Status:** aceita, implementada (série trimestral depende de `resultados_trimestrais`, spec 016)
- **Origem:** ADC_PLAN D27, D28, D29
- **Serviços:** ADC

## Decisão
- Snapshots, indicadores e demonstrativos usam `ticker_id`, não `company_id`. O Fundamentus publica por papel e não expõe CNPJ. `companies` fica para o coletor da CVM, e PETR3 e PETR4 repetem os mesmos dados de balanço.
- Proventos usam a **data-com** (`com_date`), que é a publicada pelo Fundamentus. A chave inclui `payment_date` com `NULLS NOT DISTINCT`.
- A série trimestral se acumula a cada coleta. Trimestres anteriores ao primeiro uso exigiriam CVM ITR/DFP.
