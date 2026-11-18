# ADR 010 — ADC é fonte de dados; valuation fica no Consolidator

- **Status:** aceita
- **Origem:** ADC_PLAN D18, D19
- **Serviços:** ADC, Consolidator

## Decisão
- O ADC coleta, normaliza e expõe dados. Ele não calcula valuation, DCF nem projeções; isso é do Consolidator, pelo método que o usuário escolher (ADR 005).
- O coletor é organizado em adaptadores por fonte (client, parser, normalizador, persistência), para trocar uma fonte sem afetar a API.
- Agregações simples (FCF, Dívida/PL) ainda estão em aberto: ADC ou Consolidator, a decidir na spec 017.
