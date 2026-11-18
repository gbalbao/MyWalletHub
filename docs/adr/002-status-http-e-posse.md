# ADR 002 — Semântica dos status HTTP e checagem de posse no serviço

- **Status:** aceita, implementada (exceção: `/users`, ver spec 002)
- **Origem:** BACKEND_ROADMAP D6, D7, D8
- **Serviços:** Consolidator (dono), Visualizer (consumidor)

## Decisão
- Recurso inexistente → **404**. Entrada inválida → **400**. Recurso de outro usuário → **403**, não 404.
- Token ausente ou inválido → **401**. Autenticado sem permissão → **403**. O front só desloga no 401.
- A checagem de posse fica no **serviço**, não no controller, porque os serviços se chamam entre si.

## Por quê
O id é sequencial, então responder 404 não esconde a existência do recurso. Com 403, o front consegue dizer "sem permissão" em vez de "não encontrado". Checar só no controller deixaria um caminho alternativo para o mesmo vazamento.

## Consequências
- Toda nova rota com recurso de usuário precisa checar a posse no serviço.
- `PUT/DELETE /users/{id}` ainda não seguem esta regra. Isso é corrigido na spec 002.
