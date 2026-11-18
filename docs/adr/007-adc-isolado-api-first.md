# ADR 007 — ADC é um serviço separado que só fala com o Consolidator pela API

- **Status:** aceita, implementada
- **Origem:** ADC_PLAN D2, D4, D5, D31 (arquivado em `docs/archive/adc/`)
- **Serviços:** ADC, Consolidator

## Decisão
- O ADC é um projeto separado, com banco PostgreSQL próprio (Alembic), e nunca acessa o banco do Consolidator.
- Toda integração passa pela API: ADC → Consolidator pelos endpoints públicos (importador) e, no futuro, Consolidator → ADC por `/v1` (spec 012).
- No deploy, aceita-se um único servidor Postgres com dois databases e dois usuários sem acesso cruzado.

## Por quê
Flyway e Alembic não dividem um schema. Dados públicos que podem ser coletados de novo (ADC) e o ledger do usuário (Consolidator) têm requisitos diferentes de segurança e backup.
