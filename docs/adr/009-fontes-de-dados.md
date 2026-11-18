# ADR 009 — Fonte de cada tipo de dado de mercado

- **Status:** aceita. Implementada para o Fundamentus; CVM, COTAHIST e a migração do histórico pendentes (specs 012, 017)
- **Origem:** ADC_PLAN D11, D16, D17, D22, D30 (D16 e D17 eram repetições da D11)
- **Serviços:** ADC, Consolidator

## Decisão
| Dado | Fonte |
|---|---|
| Balanço, DRE, indicadores, proventos | Fundamentus (ADC) |
| Fluxo de caixa, capex, capital de giro | CVM DFC (ADC) |
| Cotações históricas de fechamento | COTAHIST da B3 (ADC) |
| Cotação ao vivo | Brapi (Consolidator), a única sem alternativa gratuita |

## Consequências
- Hoje, o Consolidator ainda busca histórico e proventos na Brapi. A troca para o ADC é a spec 012, e a Brapi fica como fallback até a cobertura do ADC estabilizar.
