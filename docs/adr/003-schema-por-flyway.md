# ADR 003 — Schema do Consolidator versionado por Flyway

- **Status:** aceita, implementada (validação em PostgreSQL real pendente, spec 014)
- **Origem:** BACKEND_ROADMAP D9
- **Serviços:** Consolidator

## Decisão
Toda mudança de schema é uma migration Flyway (`db/migration/V*.sql`). O Hibernate roda com `ddl-auto=validate` em todos os perfis, inclusive no dev com H2.

## Por quê
Com `ddl-auto=update` no dev, uma entidade nova funcionava localmente e só quebrava no deploy, com "relation does not exist".

## Consequências
- Nenhuma entidade nova sem a migration correspondente.
- Tipos que o H2 não valida, como enums nativos do PostgreSQL, continuam sendo um risco até a validação em PostgreSQL real.
