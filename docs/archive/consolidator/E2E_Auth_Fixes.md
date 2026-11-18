> **Histórico, arquivado em 2026-11-17.** Origem: `consolidator/consolidator/E2E_Auth_Fixes.md`.
> Substituído por: spec 002 (itens #3 e #10); demais itens já implementados
> Conteúdo original abaixo, sem edição.

# E2E Auth & API Fixes — Pendências do Backend

> **Status:** backlog — nada aqui foi implementado
> **Backend:** `consolidator` — Spring Boot 3.5.6, Java 17
> **Frontend:** `../visualizer` — Angular 22, `http://localhost:4200` → `http://localhost:8080`
> **Origem:** análise do contrato real da API durante a Phase 3 (Assets CRUD) do front-end
> **Bloqueia:** o fluxo de login/cadastro **não funciona ponta a ponta** (itens 1 e 2)

Todos os itens abaixo foram verificados por leitura direta do código-fonte
(caminhos e linhas citados são do estado atual do repositório).

---

## 1. [BLOQUEADOR] CORS não configurado

Não existe **nenhuma** configuração de CORS no projeto. Busca por
`@CrossOrigin`, `CorsConfigurationSource`, `addCorsMappings` e `.cors()` em
`src/main/java` retorna **zero resultados**.

Como o front-end roda em `http://localhost:4200` e a API em
`http://localhost:8080`, o browser aplica *same-origin policy* e bloqueia
**todas** as chamadas antes de alcançarem o Spring.

### Sintoma
```
Access to XMLHttpRequest at 'http://localhost:8080/auth/login' from origin
'http://localhost:4200' has been blocked by CORS policy: No
'Access-Control-Allow-Origin' header is present on the requested resource.
```

### Correção sugerida
Criar `CorsConfig` com um `CorsConfigurationSource` bean e encadear
`.cors(...)` no `SecurityConfig`, antes de `.csrf(...)`:

```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("http://localhost:4200"));
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    config.setAllowedHeaders(List.of("Authorization", "Content-Type"));
    config.setAllowCredentials(true);

    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);
    return source;
}
```

Como o backend já usa `SessionCreationPolicy.STATELESS` com `csrf` desligado,
habilitar CORS é seguro para o JWT.

> **Alternativa considerada e descartada no front-end:** `proxy.conf.json` do
> Angular com `apiUrl` apontando para `/api`. Optamos por não usar proxy para não
> mascarar problemas reais de configuração de origem.

**Arquivos:** `common/configs/SecurityConfig.java`

---

## 2. [BLOQUEADOR] `LoginResponseDTO` retorna só `{ token }`, sem `user`

```java
public record LoginResponseDTO(String token) {}
```

O JWT carrega o **e-mail** no *subject* e o papel na claim `role`, mas o corpo
da resposta entrega **apenas** o token.

### Consequência no front-end
`AuthService.login()` executa `tokenStorage.setUser(response.user)`, que é
`undefined`. `localStorage.setItem('user', undefined)` grava a **string**
`"undefined"`; no carregamento seguinte, `TokenStorage.getUser()` faz
`JSON.parse("undefined")` e **lança exceção**, derrubando a aplicação (o header
exibe o nome do usuário).

### Correção sugerida — Opção A (recomendada)
Devolver o usuário junto:
```java
public record LoginResponseDTO(String token, UserResponseDTO user) {}
```
Mudança mínima de contrato; exige apenas um ajuste no DTO TypeScript.

### Correção sugerida — Opção B
Manter `{ token }` e derivar o usuário no front-end decodificando o JWT
(base64url do payload), usando `sub` (e-mail) e `role`.
Trade-offs: o header passa a exibir e-mail em vez de nome, o `id` do usuário
continua indisponível (e `GET /users/{id}` exige `ROLE_ADMIN`, então nunca
serviria), e o `name` fica indisponível para exibição.

**Arquivos:** `dtos/LoginResponseDTO.java`

---

## 3. [BUG] `POST /wallet` causa NPE quando `assets` não é enviado

`WalletService.createWallet()` itera `dto.assets()` sem checar nulo:

```java
dto.assets().forEach(assetDTO -> { ... });   // NPE se dto.assets() == null
```

O `WalletDTO` do front-end (`{ name, description }`) não envia `assets`, então
**criar carteira responde HTTP 500**.

### Correção sugerida (backend, preferable)
```java
if (dto.assets() != null) {
    dto.assets().forEach(assetDTO ->
        assetList.add(assetService.createAssetWithWallet(assetDTO, wallet)));
}
```

Alternativa: remover `assets` do `WalletDTO` e criar assets exclusivamente via
`POST /assets`, que é o fluxo natural.

**Arquivos:** `services/WalletService.java:39`

---

## 4. [BUG] `POST /wallet` não persiste `description`

`createWallet()` define apenas o nome e **nunca** chama
`wallet.setDescription(dto.description())`. A descrição enviada no cadastro é
**silenciosamente descartada**. Curiosamente, `updateWallet()` (linha 80) trata
a descrição corretamente — a inconsistência é só na criação.

### Correção sugerida
```java
wallet.setName(dto.name());
wallet.setDescription(dto.description());   // <- faltava
```

**Arquivos:** `services/WalletService.java:37`

---

## 5. [BUG] `POST` e `PUT /assets` ignoram o campo `name`

`AssetDataToAssetMapper` sobrescreve `name` e `ticker` com o retorno do Brapi
(`symbol` → `ticker`, `longName` → `name`). O `name` enviado no request é
descartado.

### Impacto no front-end
O formulário de assets precisa enviar `ticker` (é o input real) e deixar claro
que **o nome é derivado do Brapi e não é editável**. Como `name` é um componente
obrigatório do record `AssetDTO`, o front-end envia `''`.

Além disso: se o Brapi não encontrar o ticker, `createAsset` lança
`RuntimeException` → **HTTP 500** (ver item 7), e não um 4xx tratável.

**Arquivos:** `mappers/AssetDataToAssetMapper.java`, `services/AssetService.java:41-54`

---

## 6. [SEGURANÇA] `GET /assets` sem `walletId` expõe assets de todos os usuários

`AssetService.findAll(null)` cai no `else` e chama `repository.findAll()`,
retornando **todos** os assets de **todos** os usuários:

```java
if (walletId != null && !walletId.isBlank()) {
    assetList = repository.findByWalletId(longWalletId);
} else {
    assetList = repository.findAll();   // <-- vaza dados de todos
}
```

Não há `@PreAuthorize` nem checagem de `Authentication` no `AssetResource`; o
`SecurityConfig` só exige `anyRequest().authenticated()`. Qualquer usuário
logado enxerga a carteira dos outros — **vazamento horizontal de dados**.

### Correção sugerida
Tornar `walletId` obrigatório, ou resolver o usuário autenticado e filtrar as
carteiras dele quando o parâmetro for omitido.

**Arquivos:** `services/AssetService.java:57-71`, `controllers/AssetResource.java:41`

---

## 7. [BUG] Erros de domínio retornam HTTP 500 em vez de 4xx

`GenericExceptionHandler` trata **apenas** `MethodArgumentNotValidException` e
`ConstraintViolationException`. Todos os erros de negócio usam `RuntimeException`
crua, que cai no tratamento padrão do Spring Boot → **500 Internal Server Error**:

| Situação | Excessão | Status atual | Status ideal |
|---|---|---|---|
| Asset não encontrado | `RuntimeException("Asset not found with id: N")` | 500 | 404 |
| Ticker inválido no Brapi | `RuntimeException("Asset data not found for ticker: X")` | 500 | 400/422 |
| Venda acima do possuído | `RuntimeException("Cannot sell more than owned...")` | 500 | 409 |
| Carteira de outro usuário | `RuntimeException("Access denied: ...")` | 500 | 403 |
| `walletId` ausente ou inválido | `NumberFormatException` | 500 | 400 |

Única exceção: `GET /wallet/{id}` de carteira alheia **já** devolve 403 limpo
(`WalletResource.java:67-70`).

### Correção sugerida
Trocar as `RuntimeException` por `ResponseStatusException` (ou
`EntityNotFoundException`) nos services e adicionar os handlers correspondentes
ao `GenericExceptionHandler`, incluindo `MethodArgumentTypeMismatchException` → 400.

### Impacto no front-end
O front-end não consegue distinguir "não encontrado" de "erro interno", então
mensagens como "Internal Server Error" não são actionáveis para o usuário.

**Arquivos:** `common/utils/GenericExceptionHandler.java`, `services/*.java`

---

## 8. [BUG] Editar/excluir transação não recalcula o custo do ativo

`createTransaction` chama `updateAssetCostBasis(...)`, que recalcula
`mediumPrice`, `totalInvested` e `amount` do ativo. Porém
`updateTransaction` (linha 96) e `deleteTransaction` (linha 109) **não** chamam
esse método.

Consequência: editar uma compra de 10 para 100 unidades altera o registro da
transação mas deixa `amount`/`mediumPrice`/`totalInvested` do ativo com os
valores antigos — os dados ficam **inconsistentes** e o preço médio nunca
converge. Excluir uma transação tem o mesmo efeito.

### Correção sugerida
Em `updateTransaction`, reverter o efeito da transação original e reaplicar o da
nova; em `deleteTransaction`, reverter o efeito da transação removida. Ou
simplificar: tornar a transação **imutável** (permitir apenas create/delete, e
documentar que edition exige recriação).

**Arquivos:** `services/TransactionService.java:96-114`

---

## 9. [BUG] `allocationPercentage` da summary usa soma parcial

Em `getPortfolioSummary`, `totalCurrentValue` é incrementado **dentro** do loop
(linha 77) e o `allocationPercentage` (linha 92) é calculado contra esse valor
acumulado até o momento — não contra o total final.

Resultado: os percentuais exibidos **não somam 100%**, e o último asset da lista
tende a exibir 100% sozinho.

### Correção sugerida
Calcular `allocationPercentage` em uma segunda passagem, após `totalCurrentValue`
estar completo.

**Arquivos:** `services/ConsolidationService.java:92-94`

---

## 10. [SEGURANÇA] `@PreAuthorize` inerte — não há `@EnableMethodSecurity`

Busca por `@EnableMethodSecurity` / `@EnableGlobalMethodSecurity` em
`src/main/java` retorna **zero resultados**. A anotação
`@PreAuthorize("hasRole('ADMIN')")` no `UserResource.getAll` **não tem efeito**;
o controle de acesso real vem do `requestMatchers(HttpMethod.GET, "/users/**").hasRole("ADMIN")`
no `SecurityConfig`.

Funciona, mas por acaso — e a anotação dá falsa sensação de que a camada de
serviço está protegida.

### Correção sugerida
Adicionar `@EnableMethodSecurity` na classe de configuração, ou remover a
anotação para não confundir.

**Arquivos:** `common/configs/SecurityConfig.java`

---

## Checklist

| # | Item | Severidade | Status |
|---|---|---|---|
| 1 | CORS não configurado | bloqueador | pendente |
| 2 | `LoginResponseDTO` sem `user` | bloqueador | pendente |
| 3 | NPE em `POST /wallet` (`assets` null) | bug | pendente |
| 4 | `description` não persistida no `POST /wallet` | bug | pendente |
| 5 | `name` ignorado em `POST`/`PUT /assets` | bug | pendente |
| 6 | `GET /assets` sem `walletId` vaza todos os assets | segurança | pendente |
| 7 | Erros de domínio retornam 500 | bug | pendente |
| 8 | Editar/excluir transação não recalcula custo | bug | pendente |
| 9 | `allocationPercentage` com base parcial | bug | pendente |
| 10 | `@PreAuthorize` inerte | segurança | pendente |

Itens 1 e 2 **impedem qualquer teste end-to-end** e devem ser resolvidos antes
das demais fases.

---

## Como testar manualmente

```bash
# 1. subir o backend
mvn spring-boot:run

# 2. criar usuário (sem autenticação)
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"email":"joao@test.com","password":"12345678","name":"João"}'

# 3. login
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"joao@test.com","password":"12345678"}'

# 4. listar assets de uma carteira com o token
curl "http://localhost:8080/assets?walletId=1" \
  -H "Authorization: Bearer <token>"

# 5. summary da carteira
curl "http://localhost:8080/wallet/1/summary" \
  -H "Authorization: Bearer <token>"
```

Swagger: `http://localhost:8080/swagger-ui.html` (exige autenticação — ver
`SecurityConfig`).

---

## Contrato da API (referência rápida)

Registros em `com.mywallet.consolidator.dtos` — nomes de propriedade são
exatamente os do record, em `camelCase` (não há Jackson `@JsonProperty` nem
`property-naming-strategy` no projeto). Datas `java.util.Date` saem em
ISO-8601 com offset, ex. `2026-10-01T12:34:56.789+00:00`. Enums via
`@Enumerated(EnumType.STRING)` → `"BUY"` / `"SELL"`.

| Endpoint | Body | Response |
|---|---|---|
| `POST /auth/login` | `{ email, password }` | `{ token }` |
| `POST /users` | `{ email, password, name? }` | `UserResponseDTO` |
| `GET /wallet` | — | `WalletResponseDTO[]` |
| `POST /wallet` | `{ name, description?, assets[] }` | `WalletResponseDTO` |
| `GET /wallet/{id}` | — | `WalletResponseDTO` |
| `PUT /wallet/{id}` | `WalletDTO` | `WalletResponseDTO` |
| `DELETE /wallet/{id}` | — | 204 |
| `GET /wallet/{walletId}/summary` | — | `PortfolioSummaryDTO` |
| `GET /assets?walletId=` | — | `AssetResponseDTO[]` |
| `POST /assets` | `{ name, ticker, walletId, amount }` | `AssetResponseDTO` |
| `GET /assets/{id}` | — | `AssetResponseDTO` |
| `PUT /assets/{id}` | `AssetDTO` | `AssetResponseDTO` |
| `DELETE /assets/{id}` | — | 204 |
| `GET /transactions?assetId=` | — | `TransactionResponseDTO[]` |
| `POST /transactions` | `{ assetId, amount, unitPrice, type }` | `TransactionResponseDTO` |

Observações que surprises quem integra:

- `AssetDTO.walletId` é **`String`**, não `Long`.
- `AssetResponseDTO` **não** tem `walletId` — só o id do asset.
- `TransactionDTO` **não** aceita `date`: a data é gerada pelo servidor
  (`new Date()`) e só retorna na resposta como `transactionDate`.
- `TransactionDTO` **não** tem `fees` nem `total`.
- `assetType` existe no enum mas **não** aparece em nenhum DTO.
- `amount` é `Integer` e os preços são `Double` — não há `BigDecimal` em lugar
  nenhum, o que implica imprecisão de ponto flutuante em valores monetários.
- Resposta de validação (400) é um mapa plano `{ campo: mensagem }`, sem
  wrapper de `status`/`timestamp`.
