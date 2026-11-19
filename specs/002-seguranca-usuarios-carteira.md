# 002 — Segurança de usuários e exclusão de carteira

## Por quê
A auditoria (`docs/estado-do-projeto.md` §4, P0) e a verificação da spec 001 com o servidor rodando (2026-11-17) encontraram estes problemas:
- Qualquer usuário autenticado consegue alterar ou excluir a conta de outro usuário.
- O `@PreAuthorize` não tem efeito.
- Toda negação enviada por `sendError` chega ao cliente como 401. Isso inclui o 403 de papel, o 404 de rota inexistente, o 405 e o 415. Pelo ADR 002, o front desloga o usuário em todos esses casos.
- Excluir uma carteira com ativos falha por chave estrangeira, com um 400 genérico.
- O login com senha errada e o cadastro com e-mail repetido devolvem 400; o do cadastro traz a mensagem crua do banco.
- O `/h2-console` é público em todos os perfis.

## Objetivo
- Só o ADMIN altera ou exclui usuários.
- Cada negação chega com o status certo, então o front só desloga quando o token realmente não vale.
- Ao excluir uma carteira com ativos, o usuário vê um aviso e decide se apaga tudo ("Deletar mesmo assim") ou desiste.
- Login errado e e-mail repetido mostram mensagens claras.

## Critérios de aceite
- [ ] **Usuários.** `PUT /users/{id}` e `DELETE /users/{id}` exigem ADMIN.
  - Usuário autenticado sem ADMIN recebe **403** `{error}` no servidor real e no MockMvc, e o recurso não muda.
  - Com ADMIN, as rotas respondem como hoje: 200, 204 ou 404.
  - `DELETE /users/{id}` feito por um ADMIN apaga o usuário e, numa única transação, todas as carteiras dele com o conteúdo, como na exclusão de carteira com `force=true`. Responde 204. Se qualquer passo falhar, nada é apagado.
  - Um ADMIN que tenta excluir a própria conta recebe **409** `{error, code: "CANNOT_DELETE_SELF"}`, e nada é apagado.
- [ ] **`@EnableMethodSecurity` ativo.** Os `@PreAuthorize` existentes passam a valer, e um teste prova que um `@PreAuthorize` nega a chamada mesmo sem a regra de URL.
- [ ] **Dispatch de erro.** O `SecurityConfig` permite `DispatcherType.ERROR`. No servidor real (teste com `@SpringBootTest(webEnvironment = RANDOM_PORT)`), as respostas ficam assim:

  | Chamada | Status | Corpo |
  |---|---|---|
  | `GET /users` com token válido sem ADMIN | 403 | — |
  | Rota inexistente com token válido | 404 | — |
  | Método não suportado (ex.: `PATCH /wallet`) com token válido | 405 | — |
  | `POST` com `Content-Type` não suportado | 415 | — |
  | Rota de negócio sem token | 401 | — |
  | No perfil `prod`, `/v3/api-docs` e `/swagger-ui/index.html` | 404 | — |
  | No perfil `prod`, `/h2-console` | não pública (404 ou 401) | nunca o console |
  | Erro de negócio (ex.: venda antes da compra) | 400 | `{error, code}` igual ao de hoje |

  O dispatch de `/error` não pode abrir nenhuma rota de negócio sem token.
- [ ] **`/h2-console`.** Fica liberado no `SecurityConfig` só quando o console estiver habilitado, ou seja, no perfil padrão de dev. Fora dele, a regra `permitAll` some.
- [ ] **Login.** Credencial inválida em `POST /auth/login`, seja e-mail inexistente ou senha errada, responde **401** `{error: "E-mail ou senha inválidos"}`. A mensagem é a mesma nos dois casos, para não revelar quais e-mails existem. Login válido continua 200 com `{token, user}`.
- [ ] **E-mail duplicado.** `POST /users` com e-mail já cadastrado responde **409** `{error: "E-mail já cadastrado", code: "EMAIL_ALREADY_EXISTS"}`, sem texto do banco no corpo. A verificação existe no serviço, e a violação de unicidade do banco tem um handler de reserva com o mesmo resultado.
- [ ] **`POST /wallet` com `assets` nulo ou ausente** cria a carteira vazia (201), sem NPE. `name` vazio ou ausente responde 400 no formato de validação `{campo: mensagem}`.
- [ ] **Exclusão de carteira:**
  - `DELETE /wallet/{id}` de carteira sem ativos responde 204, como hoje, e apaga também os snapshots da carteira.
  - `DELETE /wallet/{id}` de carteira com ativos, sem `force`, responde **409** `{error, code: "WALLET_HAS_ASSETS"}` e não apaga nada. A mensagem diz quantos ativos a carteira tem.
  - `DELETE /wallet/{id}?force=true` apaga numa única transação a carteira, os ativos, as transações, os proventos, as valuations e os snapshots, e responde 204. Se qualquer passo falhar, nada é apagado.
  - Carteira de outro usuário continua 403, e carteira inexistente continua 404, com ou sem `force`.
  - Os testes cobrem os três casos e a reversão da transação.
- [ ] **Visualizer, exclusão de carteira.** Ao excluir uma carteira, a tela mostra a confirmação de hoje.
  - Se a resposta for 409 com `WALLET_HAS_ASSETS`, abre um segundo popup de aviso com a mensagem do backend e os botões "Cancelar" e "Deletar mesmo assim".
  - "Deletar mesmo assim" reenvia com `force=true` e, com 204, atualiza a lista.
  - "Cancelar" não envia nada.
  - Vale para a lista e para o detalhe da carteira.
- [ ] **Visualizer, login.** Um 401 em `POST /auth/login` mostra "E-mail ou senha inválidos" na tela de login. Ele não chama `logout()`, não navega e não mostra "Session expired". Nas demais rotas, o 401 continua deslogando.
- [ ] **Visualizer, cadastro.** Um 409 `EMAIL_ALREADY_EXISTS` mostra a mensagem do backend no formulário de cadastro, se houver tela de cadastro.
- [ ] **Contrato.** `contracts/openapi.yaml` é regenerado com `scripts/check_openapi.py --update` depois da revisão do diff, e os itens da 002 saem da lista de problemas conhecidos. `/check-contract` termina sem divergência.
- [ ] `./mvnw test` passa, com mais testes que hoje. Os testes do Visualizer (`npm test`) também passam, com testes novos para os dois popups e para o 401 do login.

## Mudanças de contrato
Todas são do Consolidator. Hoje o `BusinessRuleException` sempre responde 400. Os códigos novos (`EMAIL_ALREADY_EXISTS`, `WALLET_HAS_ASSETS`, `CANNOT_DELETE_SELF`) respondem 409, então a exceção ou o handler precisam carregar o status. Os códigos que já existem continuam 400.

| Rota | Hoje | Depois | Quebra para |
|---|---|---|---|
| `PUT /users/{id}` | Qualquer autenticado | Só ADMIN; sem ADMIN 403 `{error}` | Ninguém (o front não consome) |
| `DELETE /users/{id}` | Qualquer autenticado; com carteiras e ativos, provavelmente falha por FK | Só ADMIN; sem ADMIN 403 `{error}`; apaga em cascata; o próprio ADMIN recebe 409 `{error, code: CANNOT_DELETE_SELF}` | Ninguém |
| `GET /users`, `GET /users/{id}` sem ADMIN | 401 no servidor real | 403 | O front: o link ADMIN deixa de deslogar |
| Qualquer rota com 404/405/415 vindo de `sendError` | 401 no servidor real | O status real | O front: não desloga mais |
| `POST /auth/login`, credencial inválida | 400 `{error}` com a mensagem do Spring | **401** `{error}` com mensagem fixa | **Visualizer** (o interceptor desloga no 401; precisa abrir exceção para o login). O ADC só usa login válido |
| `POST /users`, e-mail duplicado | 400 `{error}` com o texto do banco | **409** `{error, code: EMAIL_ALREADY_EXISTS}` | Visualizer, se tiver cadastro |
| `POST /wallet`, `assets` nulo | 400 (NPE) | 201 com a carteira vazia | Nenhuma (só deixa de falhar) |
| `DELETE /wallet/{id}` | Novo parâmetro de query `force` (boolean, opcional, padrão `false`) | — | — |
| `DELETE /wallet/{id}`, com ativos e sem `force` | 400 genérico (FK) | **409** `{error, code: WALLET_HAS_ASSETS}` | Visualizer (novo popup) |
| `DELETE /wallet/{id}?force=true` | — | 204, exclusão em cascata | — |
| `/h2-console/**` | Público em todos os perfis | Público só no dev | Ninguém |

O ADC não é afetado: ele faz login com credencial válida, cria ativos e transações e não exclui carteiras nem usuários.

## Tarefas por serviço
### Consolidator
- [ ] **Segurança (filtro):** permitir `DispatcherType.ERROR`, ativar `@EnableMethodSecurity`, exigir ADMIN em `PUT/DELETE /users/**`, liberar `/h2-console/**` só com o console habilitado. Cobrir com um teste `RANDOM_PORT` que faça chamadas HTTP reais e verifique a tabela dos critérios, incluindo o Swagger em `prod`.
- [ ] **Erros de autenticação e cadastro:** responder 401 com mensagem fixa para `AuthenticationException` no login; checar o e-mail duplicado em `UserService.createUser`, com handler de reserva para `DataIntegrityViolationException`; deixar o `BusinessRuleException` carregar o status HTTP (409 para os códigos novos, 400 para os existentes); remover o handler de `ConstraintViolationException`, que hoje devolve uma chave com o nome da classe, ou ajustá-lo ao formato `{campo: mensagem}`.
- [ ] **Carteira:** corrigir o NPE de `assets` nulo e validar `name`. Em `WalletService.deleteWallet(id, userId, force)`, responder 409 `WALLET_HAS_ASSETS` quando houver ativos e não houver `force`. Com `force`, apagar em cascata dentro de `@Transactional`: para cada ativo, reaproveitar a ordem de `AssetService.deleteAsset` (valuations, proventos, transações, ativo); depois os snapshots da carteira; por fim, a carteira. Também apagar os snapshots na exclusão de carteira vazia. Em `UserService.deleteUser`, reaproveitar essa cascata para cada carteira do usuário e recusar com 409 `CANNOT_DELETE_SELF` quando o ADMIN tentar excluir a própria conta.
- [ ] **Documentação:** atualizar as anotações `@Operation`/`@ApiResponse` das rotas alteradas e tirar os textos de "PROBLEMA CONHECIDO (spec 002)".
### Visualizer
- [ ] **Interceptor e login:** não deslogar nem navegar num 401 de `/auth/login`, e mostrar "E-mail ou senha inválidos" na tela de login. Cobrir com teste.
- [ ] **Exclusão de carteira:** tratar o 409 `WALLET_HAS_ASSETS` em `wallet-list` e `wallet-detail` com um segundo popup ("Cancelar" / "Deletar mesmo assim") pelo `ConfirmService`. Acrescentar `force` em `WalletService.delete(id, force = false)`. Cobrir com teste.
- [ ] **Cadastro:** mostrar a mensagem do 409 `EMAIL_ALREADY_EXISTS`, se a tela existir; se não existir, nada a fazer.
### ADC
- Nenhuma tarefa. O `integration-reviewer` confirma que o importador não depende do 400 do login nem da exclusão de carteira.
### Hub (arquiteto)
- [ ] Revisar o diff do contrato, regenerar `contracts/openapi.yaml` com `--update`, atualizar a lista de problemas conhecidos e rodar `/check-contract`.

## Fora de escopo
- Autoedição do perfil por usuário comum: com "só ADMIN", ninguém edita a própria conta pela API. Se for preciso, entra numa spec futura, por exemplo com `PUT /users/me`.
- A tela de administração de usuários e o link ADMIN "Usuários" quebrado (fica no backlog, P1 §4.9).
- Liberar `/actuator/health`, Docker e CORS por propriedade (spec 014).
- Expiração ou refresh de token, rate limit no login, política de senha.
- Exclusão lógica (soft delete) ou lixeira de carteira.

## Riscos e dúvidas
- **Decidido (2026-11-19):** `PUT/DELETE /users/{id}` ficam só com o ADMIN.
- **Decidido (2026-11-19):** a exclusão de carteira com ativos responde 409 por padrão e apaga em cascata com `force=true`, depois do popup "Deletar mesmo assim".
- **Decidido (2026-11-19):** o login inválido passa a responder 401, e o e-mail duplicado, 409 `EMAIL_ALREADY_EXISTS`.
- **Decidido (2026-11-19):** a exclusão de um usuário reaproveita a cascata da carteira. Cada carteira dele é apagada como se viesse com `force=true`. Sem isso, a exclusão falharia por FK: o `User` mapeia as carteiras com `cascade = ALL`, mas `Wallet → Asset` não tem cascade.
- **Decidido (2026-11-19):** o ADMIN não pode excluir a própria conta. A tentativa recebe 409 `CANNOT_DELETE_SELF`, para o sistema não ficar sem nenhum ADMIN.
- **A cascata é irreversível.** O popup precisa deixar claro o que se perde: ativos, transações, proventos, valuations e histórico. A mensagem vem do backend para não divergir.
- **O dispatch `ERROR` liberado:** o risco é expor alguma informação na página de erro padrão. O teste em servidor real confere que o corpo não traz stack trace e que nenhuma rota de negócio fica acessível sem token.
- **Mudança de status no login:** clientes que tratavam o 400 do login quebram. O único conhecido é o Visualizer, que entra na mesma entrega. O Consolidator e o Visualizer precisam ir juntos; sem a mudança do front, o login errado mostraria "Session expired".
- **`@EnableMethodSecurity` pode ativar `@PreAuthorize` esquecidos** em outros controllers. O subagente lista todos antes de ativar e confere que nenhum bloqueia uma rota usada hoje.

## ClickUp
Pasta MyWallet. Os cards ficam na lista do serviço; as dependências estão cadastradas no ClickUp.
- [[Consolidator] 002 — Segurança de usuários, status de erro e exclusão de carteira](https://app.clickup.com/t/1dfhfaqcynf)
- [[Visualizer] 002 — Login 401 e exclusão de carteira com confirmação](https://app.clickup.com/t/1dfhfaqcynh): depende do card do Consolidator
- [[Hub] 002 — Atualizar contrato e check-contract](https://app.clickup.com/t/1dfhfaqcynj): depende dos cards do Consolidator e do Visualizer
