# ADR 008 — Credenciais e token JWT do ADC só em memória

- **Status:** aceita, implementada
- **Origem:** ADC_PLAN D6, D15
- **Serviços:** ADC

## Decisão
O ADC faz login por CLI com e-mail e senha. O token JWT vive só em memória durante a execução e nunca é gravado em disco, nem ele nem as credenciais.
