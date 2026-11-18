> **Histórico, arquivado em 2026-11-17.** Origem: `consolidator/consolidator/BACKEND_ROADMAP.md`.
> Substituído por: docs/adr/ (decisões D1–D13) e specs do backlog (docs/backlog-proposto.md)
> Conteúdo original abaixo, sem edição.

# Backend Roadmap — Ledger, Preço de Aquisição e Dívidas

Documento de acompanhamento das fases de correção do backend. Criado para não
perder o plano: cada fase registra objetivo, mudanças por arquivo, decisões com
o porquê, riscos e critério de aceite.

Contexto: o projeto começou com o `Asset` guardando agregados mutados
imperativamente (`amount`, `mediumPrice`, `totalInvested`) e o `Wallet` com um
`totalInvestedValue` congelado no momento da criação. A implementação das
Fases 2 a 4 do front expôs dois sintomas que só se resolvem na raiz:

1. O total investido da carteira permanece `0.0` mesmo após registrar compras.
2. O preço médio do ativo vem do Brapi (preço de mercado atual) em vez do preço
   realmente pago na data da compra.

---

## Decisões transversais

Estas decisões valem para todas as fases. Não reabrir sem registrar aqui.

| # | Decisão | Motivo |
|---|---------|--------|
| D1 | Ativo aceita preço e data de aquisição; a compra vira uma transação BUY de abertura | O ledger passa a ser a fonte da verdade. A transação não é dado inventado: o usuário realmente comprou, e o preço é o que ele digitou |
| D2 | Quantidade, preço e data da posição são editados **exclusivamente** pelo ledger | Separa as responsabilidades: o form de ativo edita `ticker`; a tela de transações edita a posição. Elimina ambiguidade de propriedade |
| D3 | `Asset.currentValue` mantém o nome atual e a semântica de preço unitário da Brapi | Renomear quebra contrato com o front e com os testes. Registrado como dívida técnica; o front já multiplica por `amount` |
| D4 | Fases D (validação/erros) e E (propriedade) vêm depois de A, B e C | Prioriza o fluxo funcional do usuário |
| D5 | `transactionDate` permanece `java.util.Date` nesta fase | Migração para `LocalDate` arrasta mapper, serialização e testes. Tratar como item separado |
| D6 | Recurso inexistente é 404; entrada inválida é 400; recurso de outro usuário é 403 | A distinção só existe se a exceção carregar a intenção. Por isso `findById` lança `EntityNotFoundException` em vez de `RuntimeException` |
| D7 | Checagem de posse vive no serviço, não no controller | `AssetService` é chamado também por `WalletService` e `ConsolidationService`. Checar no controller deixa o serviço como caminho alternativo para o mesmo vazamento |
| D8 | Recurso de outro usuário responde 403, e não 404 | Já era o comportamento de `WalletResource`. Id de ativo é sequencial, então 404 não esconde a existência; e 403 deixa o front distinguir "sem permissão" de "não encontrado" |
| D9 | Schema passa a ser versionado por migration (Flyway) | Dev usa H2 com `ddl-auto=update` e prod usa PostgreSQL com `ddl-auto=validate`. Sem migration, qualquer entidade nova funciona na máquina e derruba a aplicação em produção com "relation does not exist" — falha que só aparece no deploy |
| D10 | Proventos (dividendos) em entidade própria, nunca como `TransactionType` | Dividendo não é compra nem venda: é entrada de caixa sem alterar posição nem custo. Como `AssetPositionCalculator` só tem ramos `BUY`/`SELL`, um `DIVIDEND` cairia fora dos dois e a posição ficaria correta *por acidente*. Entidade separada elimina o risco de vez |
| D11 | DCF entra com padrões editáveis, e nunca como número solto | A Brapi não fornece fluxo de caixa livre, crescimento nem taxa de desconto — o usuário precisa informar tudo. Todo valor pré-preenchido é exibido marcado como premissa, a fórmula fica visível, e o resultado sai como faixa de sensibilidade. Um único número com aparência de verdade seria pior que não ter a feature |
| D12 | Indisponibilidade da Brapi é estado de negócio, não erro | Dividendos de FII retornam 403 no plano gratuito. Se o adapter tratar isso como exceção, a tela de FII quebra. O retorno é "indisponível, com motivo", e o front mostra aviso + lançamento manual |
| D13 | Reconstrução histórica é best-effort e responde parcial, avisada | O histórico da Brapi é limitado (3 meses para FII, 5 anos para ação). Truncar em silêncio faria o gráfico parecer completo. A resposta declara o que não foi possível reconstruir |

### Comportamento observado da Brapi

Medido em 2026-10-05 contra o token do plano gratuito. Estas respostas **mudam o
desenho** das Fases H e J, então não devem ser redescobertas na marra:

| Recurso | Ações | FIIs |
|---|---|---|
| Preço, P/E, EPS | sim | sim |
| `dividends=true&fundamental=true` | **sim**, 121 a 215 registros desde 2001 | **403** — "requer o plano Startup" |
| `range` + `interval` (série histórica) | até `5y` (61 pontos) | **só `1d`, `5d`, `1mo`, `3mo`** |

Detalhes que o código precisa tratar:

- **Registros sem `paymentDate`**: de 176 registros do PETR4, apenas 121 têm
  data. Os nulos precisam ser descartados, não convertidos.
- **`assetIssued` vem como ISIN** (`BRPETRACNPR6`), não como ticker. Não pode ser
  usado como chave de ativo.
- **Sem endpoint dedicado**: `GET /api/divdends/{ticker}` e `/api/dividends/{ticker}`
  retornam 404. Os dados só vêm pelo parâmetro do endpoint de quote.
- **Histórico sob demanda é caro**: Fases H e J servem do banco, nunca chamam a
  Brapi por render.

### Dívidas técnicas conhecidas

- **`Asset.currentValue`**: guarda o preço unitário corrente da Brapi, não o
  valor total da posição. O nome sugere o segundo. O valor total é
  `amount * currentValue`. O `ConsolidationService` e o front já fazem essa
  multiplicação. Renomear para `currentPrice` exige migração dos dois lados.
- **`AssetService.createWallet` faz N chamadas ao Brapi** dentro de uma única
  transação, uma por ativo. Se a criação de carteira ficar lenta, olhar aqui
  primeiro.
- **`Asset.fairValue` é um campo órfão**: preenchido uma única vez na criação do
  ativo com Graham (`sqrt(22.5 × PE × EPS)`), nunca recalculado, ausente do
  `PortfolioSummaryDTO` e não exibido em nenhuma tela. Pior: quando PE/EPS vêm
  `null`, o fallback é `setFairValue(dto.regularMarketPrice())`, ou seja
  "preço justo = preço de hoje", que afirma "não está sobrevalorizado" sem
  nenhuma base. A Fase I corrige o fallback para `null`.
- **`populateMarketData` imprime o upside no `stdout`**: dois `System.out.println`
  em código de produção. A Fase I remove.
- **DDL descasado entre dev e prod**: ver D9. É a Fase 0 que fecha isso.
### Falha corrigida — travao de autenticacao (2026-10-05)

Sintoma reportado: com um token velho no `localStorage` do navegador, o cadastro
respondia **403** e o usuario nao conseguia **nem criar a conta nem entrar** — as
duas telas de onde ele se recuperaria. Sem caminho de saida alem de limpar o
storage na mao.

Dois defeitos somados:

| # | Onde | Defeito |
|---|---|---|
| 1 | `JwtAuthFilter` | `loadUserByUsername` era chamado **antes** de `isTokenValid`. Token de usuario removido lancava `UsernameNotFoundException`, que derrubava a requisicao **antes** da regra `permitAll` ser avaliada —inclusive em `POST /users` e `/auth/login`. Resposta: `403` com corpo vazio |
| 2 | front `JwtInterceptor` + `ErrorInterceptor` | O token era anexado a **todas** as requisicoes, e o `403` nao limpava a sessao: so exibia mensagem. O token velho continuava sendo reenviado, entao o estado nao se recuperava |

Por que o usuario some: o H2 de dev e **em memoria** e `spring-boot-devtools`
esta no `pom.xml` com escopo `runtime`. Editar codigo recarrega o contexto no
mesmo JVM e **apaga o banco**. O token deixa de resolver para um usuario que
nao existe mais — exatamente o caso que o filtro nao tratava.

Correcao:

- `JwtAuthFilter`: token malformado, com assinatura invalida ou de usuario
  inexistente **segue como anonimo** em vez de derrubar a requisicao.
  `JWTServiceTest` nao cobre o filtro; `JwtAuthFilterTest` foi criado com 5 casos
  para isso, sendo o central "token de usuario inexistente nao derruba a
  requisicao".
- `auth.interceptor.ts`: nao anexa token em `/auth/` e `/users`.
- `error.interceptor.ts`: `403` com token em maos faz logout e redireciona para
  `/auth/login`; sem token, continua sendo "sem permissao".

Decisao que vem junto: **rota publica nao recebe token.** O `permitAll` do Spring
Security so vale se nada antes dele derrubar a requisicao — o filtro corre antes
das regras de autorizacao. Enviar token para rota publica nao e inofensivo, e
transforma credencial velha em travao.

Verificado contra o servidor rodando, com token de usuario inexistente:
`POST /users` 201, `POST /auth/login` 200, `GET /users` 403 (rota protegida sem
token, como esperado).

- **Dívida técnica resolvida na Fase E**: a camada de autorização ausente no
  `AssetResource` (`WalletResource` validava posse, `AssetResource` não) foi
  fechada. A checagem passou a viver no serviço, e não em base comum entre os
  dois controllers: a omissão era de `AssetResource` por ordem de escrita do
  código, não de projeto, então não havia uma base comum a extrair — havia duas
  implementações diferentes, uma delas errada.

---

## Fase A — Ledger determinístico

**Status:** concluída

### Objetivo

Tornar o livro-razão a fonte da verdade. Nenhum agregado sobrevive a uma edição
ou exclusão de transação.

### Sintoma que resolve

Editar ou excluir uma transação hoje deixa `amount`, `mediumPrice` e
`totalInvested` do ativo incorretos, de forma silenciosa e permanente. O
`updateTransaction` e o `deleteTransaction` não chamam
`updateAssetCostBasis`.

### Mudanças

#### `dtos/TransactionDTO.java` — aceita a data da transação

```java
public record TransactionDTO(
        Long assetId,
        Integer amount,
        Double unitPrice,
        TransactionType type,
        Date transactionDate) {
}
```

`createTransaction` deixa de usar `new Date()` fixo e passa a usar
`dto.transactionDate()`, com `new Date()` apenas como fallback quando o campo
vem nulo. Assim o front antigo continua funcionando durante a transição.

#### `repositories/TransactionRepository.java` — ordenação canônica

```java
List<Transaction> findByAssetIdOrderByTransactionDateAscIdAsc(Long assetId);
```

Sem ordenação determinística o replay não é reprodutível quando duas transações
caem no mesmo milissegundo. `id` é o desempate.

#### `services/AssetPositionCalculator.java` — novo, replay puro

```java
public record Position(int amount, double totalInvested, Double mediumPrice) {}

public Position calculate(List<Transaction> transactions) {
    int qty = 0;
    double cost = 0.0;
    Double avg = null;

    for (Transaction t : transactions) {
        if (t.getType() == TransactionType.BUY) {
            cost += t.getAmount() * t.getUnitPrice();
            qty += t.getAmount();
            avg = cost / qty;
        } else {
            cost -= avg * t.getAmount();
            qty -= t.getAmount();
        }
    }

    return new Position(qty, cost, avg);
}
```

Sem estado, sem acesso a repositório, sem `@Transactional`. Reproduz o método do
custo médio que já existia de forma incremental: a venda desconta
`avg * amount` e **não** altera `avg`.

A diferença é que agora é derivado, então editar a transação 1 de 5 recalcula as
cinco corretamente.

#### `services/TransactionService.java` — recalcula em toda escrita

`updateAssetCostBasis` sai. `createTransaction`, `updateTransaction` e
`deleteTransaction` passam a chamar o replay e aplicar o resultado.

**O replay roda antes do `save`.** Para simular o estado pós-write sem gravar, o
serviço monta o ledger em memória — adicionando, substituindo ou removendo a
transação — e só persiste se o resultado for válido. Uma venda acima da posição
agora não deixa registro gravado, sem depender de rollback do banco.

Isso é diferente do risco Originally previsto: a validação em memória é
suficiente porque o replay é puro.

Ao editar, a ordem canônica é reaplicada sobre a lista em memória, porque
mudar a data reposiciona a transação e altera todos os agregados
posteriores. `sort()` espelha a ordenação do repositório.

Se o `assetId` mudar na edição, o ativo de origem também é recalculado, com a
transação removida do ledger dele.

### Testes

**`AssetPositionCalculatorTest`** (novo, 10 casos) cobre o replay isolado:
ledger vazio, compra única, média ponderada, venda desconta a média sem alterá-la,
venda total zera o investido, over-selling, venda antes de qualquer compra, e
os dois cenários que a mutação incremental não resolvia — editar uma compra
antiga e remover uma compra antiga, ambos recomputando todos os agregados
seguintes.

Um caso fixa o contrato de ordenação: com uma venda entre duas compras, inverter
a ordem muda o resultado. É isso que torna a ordenação canônica obrigatória em
vez de confiar na ordem do banco.

**`TransactionServiceTest`** reescrito. O repositório mockado persiste de
verdade em uma lista, então o teste exercita o caminho completo: salvar, reler o
ledger, recalcular. Cobre a data do cliente, o fallback para `new Date()`, o
ledger com a transação substituída no update, a preservação da data original
quando o `PUT` omite o campo, o ledger sem a transação no delete, e a garantia de
que nada é gravado quando o replay rejeita.

### Critério de aceite — verificado

`mvn test`: 75 testes, 0 falhas.

### Estado no front

`TransactionRequestDTO` ganhou `transactionDate?` e o formulário de transação
passou a ter campo de data editável, com validação de data futura e conversão
para ISO UTC. A nota "a data é registrada automaticamente pelo servidor" saiu do
formulário.

### Riscos

- **Regressão silenciosa**: o agregado deixa de ser mutado, então qualquer
  caminho de escrita que esqueça de chamar o recalculador reintroduz o bug.
  Coberto pelos testes de `TransactionServiceTest`.
- **`mediumPrice` null**: ativo sem compras fica com `mediumPrice = null`. O front
  já trata `null` em `profitLossPercentage`.
- **Volume**: o replay é O(n) por escrita, com uma query a mais por operação. Irrelevante na escala atual.

---

## Fase B — Preço de aquisição

**Status:** concluída

### Objetivo

O preço vem do usuário, na data que ele escolher, e não do mercado no momento da
screenshot.

### Sintoma que resolve

`populateNewAsset` inventa `mediumPrice` a partir do `regularMarketPrice` do
Brapi. "Criar 100 unidades de PETR4" produz `totalInvested = 100 * preço de
hoje`. É fabricação de custo.

Além disso, `mediumPrice` passa a significar "preço médio pago" em vez de
"preço médio de mercado hoje", que é o que o nome sempre prometeu.

### Mudanças

#### `dtos/AssetCreateDTO.java` e `dtos/AssetUpdateDTO.java` — contratos separados

Hoje um único `AssetDTO` serve para criar e para editar, com `amount` e `unitPrice`
que fazem sentido só na criação. Viram dois records porque são contratos
diferentes de verdade:

```java
public record AssetCreateDTO(
        @NotBlank String ticker,
        @NotBlank String walletId,
        @NotNull @Positive Integer amount,
        @Positive Double unitPrice,
        Date acquisitionDate) {}

public record AssetUpdateDTO(
        @NotBlank String ticker) {}
```

Sem `name` nos dois, por um motivo que só apareceu em produção: o nome é dado de
mercado, resolvido pelo `ticker` no Brapi, e o cliente não tem como conhecê-lo
antes de criar o ativo. A primeira versão desta fase exigiu `name` com
`@NotBlank` no `AssetCreateDTO` e a UI quebrou com 400, mandando `name: ""` como
o front sempre mandou. Exigir um campo que o cliente não pode preencher só
produz string vazia. No `AssetUpdateDTO` o efeito era pior: gravar o nome
recebido apagava o nome real, e o nome era justamente o único campo que o
formulário de edição oferecia.

No `create` o `name` legado é ignorado em silêncio, para não quebrar cliente
antigo. No `update` ele é rejeitado, junto com `amount`/`unitPrice`/`walletId`.

O `PUT /assets/{id}` recusa `unitPrice` com erro claro, em vez de ignorar o
campo em silêncio (decisão D2).

`WalletDTO` contém `List<AssetDTO>`; passa a conter `List<AssetCreateDTO>`.

#### `AssetService.createAssetWithWallet` — sintetiza a transação de abertura

Com `unitPrice` preenchido, delega a `TransactionService.createTransaction` o
registro de uma BUY de abertura e deixa o replay derivar `mediumPrice` e
`totalInvested`.

Um detalhe que vale registrar: `AssetService` não copia o resultado de volta
para o seu `asset`. `createTransaction` recarrega o ativo do repositório, e
dentro da mesma transação de banco o gerenciador de persistência devolve a
mesma instância que acabamos de salvar, então o replay escreve nela e o campo
volta atualizado no objeto devolvido ao chamador. Copiar o resultado seria
duplicar a aritmética do replay num segundo lugar, que é a forma mais rápida de
os dois divergirem.

`populateNewAsset` virou `populateMarketData` e não toca mais em
`mediumPrice`/`totalInvested`. `currentValue` continua vindo do Brapi (D3).

#### `AssetUpdateDTO` rejeita campo desconhecido em vez de ignorá-lo

O Jackson ignora propriedade não mapeada por padrão no Spring Boot, o que
transformaria um `amount` errado em um 200 que não altera nada: exatamente o tipo
de sucesso enganoso que a separação de contratos existe para evitar. Um
`@JsonAnySetter` no record lança e sai como 400.

Ficou local no `AssetUpdateDTO` em vez de virar
`spring.jackson.deserialization.fail-on-unknown-properties=true`, que mudaria o
comportamento de todos os endpoints para resolver o problema de um.

#### Exclusão em cascata

`deleteAsset` apaga as transações antes do ativo. O `@OneToMany` do `Asset` não
tem cascade, e transação órfã apontando para asset excluído quebraria o replay.

### Testes

**`AssetServiceTest`** reescrito (12 casos). Cobre a transação de abertura
sintetizada com a data do cliente, o `new Date()` como fallback, o ativo zerado
sem `unitPrice`, e o ponto central: `currentValue` continua vindo do Brapi
enquanto `mediumPrice` e `totalInvested` não podem ter recebido o preço de
mercado. Também fixa que `updateAsset` não toca a posição, e que
`deleteAsset` apaga transação antes do ativo (`InOrder`).

**`AssetOpeningTransactionTest`** (novo, 7 casos) sobe o contexto Spring inteiro
contra H2. É o que fecha o ciclo: os testes com mock provam que o serviço chama
o collaborative, não que a transação chega na tabela `transactions` nem que o
valor gravado bate. Cobre a abertura com agregado casando com o replay, o ativo
zerado, recalcular ao editar e ao excluir a compra de abertura, a segunda compra
sobre a abertura (média 45.0 entre 100@30 e 100@60), a cascata de exclusão, e a
regressão da Fase A voltando pelo PUT de metadata.

**`AssetResourceTest`** ganha três casos: `PUT` com `amount` e com `unitPrice`
retornam 400, e `amount` negativo no `POST` é rejeitado.

`mvn test`: 92 testes, 0 falhas.

### Estado no front

`AssetCreateRequestDTO` e `AssetUpdateRequestDTO` separados. O formulário virou
"Adicionar posição", com preço de aquisição e data da compra, e em modo de
edição mostra que a posição não é editável ali. A coluna "Preço médio" passou a
"Preço médio pago" e trata `null` com em dash e tooltip, que é o caso do ativo
criado sem custo.

### Riscos que sobraram

- **Visibilidade da transação de abertura**: `GET /transactions?assetId=` passa a
  devolver um registro que o usuário não digitou. É correto para auditoria, mas
  a UI ainda não marca como "Abertura de posição".
- **Duplicidade**: o usuário criar o ativo e depois registrar uma compra da mesma
  quantidade conta duas vezes. O backend não tem como detectar, porque são dois
  registros válidos. Mitigação é de vocabulário: o form de ativo diz "adicionar
  posição existente" e o de transação diz "registrar compra ou venda".
- **`walletId` sumiu do PUT**: trocar o ativo de carteira não tem mais endpoint.
  Não havia UI para isso, então nada quebrou, mas é uma functionality que
  existe no contrato antigo e precisa de decisão antes de voltar.
- **Asset sem usuário**: `createAssetWithWallet` aceita uma `Wallet` que ainda não
  tem id, e o cascade `PERSIST` do `@ManyToOne` grava a carteira junto. É o que
  o `WalletService` já fazia; agora a transação de abertura entra no meio.

### Critério de aceite — verificado

Criar ativo com `unitPrice` e `acquisitionDate` gera exatamente uma transação BUY
com esses valores, e o agregado do ativo bate com o replay. Criar sem `unitPrice`
gera ativo zerado e sem transação. Ambos cobertos em
`AssetOpeningTransactionTest` contra H2.

---

## Fase C — Carteira derivada

**Status:** concluída

### Objetivo

`totalInvestedValue` calculado na leitura, e não congelado na criação.

### Sintoma que resolve

`WalletService.createWallet` calcula o total uma única vez. Como o front envia
`assets: []` (workaround do NPE), nasce `0.0`, e nenhum código depois disso
volta a tocar no campo.

Bug adjacente: `createWallet` nunca chama `setDescription`. A descrição digitada
no formulário é descartada na criação e só passa a valer depois de um `PUT`.

### Mudanças

- `createWallet` ganha `wallet.setDescription(dto.description())`
- `totalInvestedValue` sai de campo mutado e passa a ser `SUM` dos agregados dos
  assets, calculado em `WalletResource` ao montar o `WalletResponseDTO`

### Riscos

- Testes de resource usam `TestSecurityConfig`; o ajuste fica contido neles.

### Critério de aceite

Carteira criada zerada e depois comprada reflete o valor no `GET /wallet/{id}` e
no `GET /wallet`. Descrição persiste desde a criação.

De quebra: `GET /wallet/{id}/summary` volta a fazer sentido. O
`ConsolidationService` já busca preço ao vivo do Brapi por ativo e é a base
natural da Phase 5 do front, que já estava com o endpoint certo.

### Pendência de produção

Remover `totalInvestedValue` do mapeamento do Hibernate não derruba a coluna.
Em produção `ddl-auto=validate` apenas valida o schema esperado pelo mapeamento,
e o projeto não tem Flyway nem Liquibase, então a coluna
`wallets.total_invested_value` continua lá.

Se a coluna for `NOT NULL` sem default, o `INSERT` da carteira passa a omitir o
campo e o banco recusa. Precisa de uma migração manual antes do deploy:

```sql
ALTER TABLE wallets ALTER COLUMN total_invested_value DROP NOT NULL;
```

Com o valor antigo preservado e a coluna intocada, a carteira volta a ler o
total do ledger. O dado antigo fica parado, mas não mais errado que antes: o
campo já era congelado no momento da criação e por isso não refletia compra
nenhuma.

---

## Fase D — Validação e erros

**Status:** concluída

### Objetivo

Status HTTP correto e validação no contrato.

### Sintoma que resolve

`TransactionDTO` não tem `@NotNull`/`@Positive`, então aceita `amount` negativo.
Ticker inexistente no Brapi e `walletId` inválido retornam 500 pelo
`RuntimeException` sem handler, e o front adivinha o motivo com `mapError`
olhando o status.

### Mudanças

#### `dtos/TransactionDTO.java` — validação no contrato

```java
public record TransactionDTO(
        @NotNull(message = "assetId is required")
        Long assetId,
        @NotNull(message = "amount is required")
        @Positive(message = "amount must be positive")
        Integer amount,
        @NotNull(message = "unitPrice is required")
        @Positive(message = "unitPrice must be positive")
        Double unitPrice,
        @NotNull(message = "type is required")
        TransactionType type,
        Date transactionDate) {}
```

`transactionDate` segue sem anotação: continua aceitando nulo, porque o
cliente legado não envia e o serviço cai para `new Date()` (decisão D5).

Uma venda com `amount` negativo era aceita pelo contrato e só falhava no replay,
depois do `save`. Agora é rejeitada antes de qualquer escrita.

#### `GenericExceptionHandler` — exceção tipada em vez de 500

O handler só existia para `MethodArgumentNotValidException` e para a
`ConstraintViolationException` do e-mail duplicado. Tudo o mais subia como 500,
e o front não tinha como distinguir "ticker não existe no Brapi" de "walletId
inválido" — os dois chegavam como `RuntimeException`.

A correção é trocar `RuntimeException` genérica por tipos que carregam a
intenção, e deixar o handler traduzir:

| Exceção | Status |
|---|---|
| `MethodArgumentNotValidException` | 400, mapa de campo → mensagem |
| `ConstraintViolationException` | 400, e-mail duplicado |
| `IllegalArgumentException` | 400 (inclui o `@JsonAnySetter` do `AssetUpdateDTO`) |
| `EntityNotFoundException` | 404 |
| `AccessDeniedException` | 403 |
| `ResponseStatusException` | o próprio status |
| `RuntimeException` | 400, com a mensagem |

O payload é `{"error": "..."}` nos casos novos. Não inclui stack trace: a
mensagem do `RuntimeException` já é descritiva porque os serviços a escrevem
com o id que falhou.

O `RuntimeException` genérico no fim é a rede de segurança para os serviços que
ainda não migraram para `EntityNotFoundException`. Ele responde 400 e não 500
porque, em todos os casos que restam, a causa é entrada inválida do cliente.

#### Exceções tipadas nos serviços

`findById` de `WalletService`, `AssetService`, `TransactionService` e
`UserService` passaram a lançar `EntityNotFoundException`. As checagens de posse
passaram a lançar `AccessDeniedException` (ver Fase E).

### Decisões

- **D6**: recurso inexistente é 404, e-mail duplicado é 400. A distinção é entre
  "não existe" e "existe mas está errado", e ela só fica disponível se a
  exceção carregar a intenção. Por isso o trabalho foi trocar as
  `RuntimeException` por tipos, e não mapear a `RuntimeException` para 404.
- **D7**: 403 em acesso a recurso de outro usuário, e não 404. O plano original
  desta fase sugeria 404 para não vazar existência por enumeração de id. A
  Fase E inverteu: ver D8.

### Testes

`TransactionResourceTest` e `AssetResourceTest` ganharam casos de status HTTP
(404 para ativo inexistente, 403 para recurso de outro usuário). `mvn clean
install`: **120 testes, 0 falhas**.

### Pendência

`@PastOrPresent` na data não entrou. O formulário do front já valida data
futura, e o `TransactionDTO` é usado tanto para compra quanto para venda: um
`ticker` de ativo que só existe daqui a três dias tem data de aquisição futura
legítima. Tratar isso exige decidir a regra de negócio antes de codificar.

---

## Fase E — Propriedade

**Status:** concluída

### Objetivo

Nenhum usuário enxerga ou altera dados de outro.

### Sintoma que resolve

- `GET /assets` sem `walletId` devolve os ativos de **todos** os usuários
- `POST /assets` não verifica se a carteira pertence ao usuário autenticado
- `PUT /assets/{id}` e `DELETE /assets/{id}` não verificam posse
- `GET /transactions?assetId=`, `POST /transactions` e `DELETE /transactions/{id}` não verificam posse

### Mudanças

A validação de posse foi para a **camada de serviço**, não para o controller.
Motivo: `AssetResource` não é a única porta de entrada. `WalletService` chama
`AssetService` durante a criação da carteira, e o `ConsolidationService` lê
ativos direto do repositório. Checar no controller deixaria o serviço como
caminho alternativo para o mesmo vazamento.

#### `AssetService` — posse em toda entrada

Cada método público que recebe um id passa a receber também o `userEmail`, e
a posse é conferida antes de qualquer leitura ou escrita:

```java
private Wallet findOwnedWallet(Long walletId, String userEmail)
{
    Wallet wallet = walletRepository.findById(walletId)
            .orElseThrow(() -> new EntityNotFoundException("Wallet not found for id: " + walletId));

    if (wallet.getUser() == null || !wallet.getUser().getEmail().equals(userEmail))
    {
        throw new AccessDeniedException("Access denied: wallet does not belong to authenticated user");
    }

    return wallet;
}
```

`findById` faz o mesmo pelo caminho `asset.wallet.user`, o que cobre
`GET /assets/{id}`, `PUT` e `DELETE` com uma única checagem.

#### `GET /assets` sem `walletId` deixa de ser global

```java
public List<Asset> findAll(String walletId, String userEmail)
{
    if (walletId != null && !walletId.isBlank())
    {
        findOwnedWallet(Long.valueOf(walletId), userEmail);
        return repository.findByWalletId(Long.valueOf(walletId));
    }

    User user = userRepository.findByEmail(userEmail)
            .orElseThrow(() -> new EntityNotFoundException("User not found with email: " + userEmail));

    List<Asset> scoped = new ArrayList<>();
    user.getWallets().forEach(wallet -> scoped.addAll(wallet.getAssets()));
    return scoped;
}
```

A versão anterior caía em `repository.findAll()`. O `walletId` continua
opcional porque o front usa a listagem sem filtro no dashboard, mas o escopo
passa a ser o usuário, não a tabela.

#### `TransactionService` — o ledger também é do dono

`createTransaction`, `updateTransaction`, `deleteTransaction` e `findByAssetId`
recebem `userEmail` e conferem a posse do ativo (ou do ativo da transação, no
caso do update e do delete).

`createTransaction` ficou com duas assinaturas de propósito: a com `userEmail`
é a entrada de usuário, e a sem ele é o caminho interno de escrita do ledger,
usado pela abertura de posição do `AssetService`. Esse caminho não é
alcançável por controller — o `AssetResource` e o `TransactionResource` só
expoem a variante com e-mail, e ela já validou a posse da carteira antes de
chegar lá.

#### Remoção dos atalhos sem dono

As variantes sem `userEmail` de `AssetService.findAll`, `findById`,
`createAsset`, `updateAsset` e `deleteAsset` foram removidas. Mantê-las como
overload com `null` seria exatamente o furo que a fase fecha: um `null` passando
por engano reintroduz a listagem global e a escrita sem dono, em silêncio.

### Decisões

- **D8**: recurso de outro usuário responde **403**, não 404. O plano desta fase
  sugeria 404 para não vazar existência na enumeração de ids. A Fase E
  implementou 403 porque o endpoint já responde 403 para o mesmo caso em
  `WalletResource.getWalletById`, e ter os dois recursos se comportando
  diferente com o mesmo problema é pior que o vazamento: o id de um ativo é
  sequencial e curto, então enumerá-lo é trivial de qualquer jeito, e o 403
  entrega ao usuário a informação de que ele está logado mas sem permissão —
  que é o que permite o front mostrar "você não tem acesso a este recurso" em
  vez de "não encontrado". Se o threat model mudar, a troca é uma linha no
  handler.
- **D9**: a checagem fica no serviço. Registrar aqui porque a omissão original
  não foi decisão: `WalletResource` validava e `AssetResource` não, por ordem
  de escrita do código.

### Testes

`AssetServiceTest` ganhou 4 casos de acesso cross-user: create com carteira
alheia, `findAll` com `walletId` alheio, `findAll` sem filtro devolvendo só o
escopo do usuário, update e delete de ativo alheio. `AssetResourceTest` ganhou
4 casos de status HTTP e `TransactionResourceTest` ganhou 3.

O caso que substitui o antigo `findAll_shouldReturnAllAssetsWhenWalletIdNull` é
o ponto central da fase: ele verifica `verify(assetRepository, never()).findAll()`,
o que falha se a listagem global voltar por qualquer caminho.

`mvn clean install`: **120 testes, 0 falhas** (109 da baseline + 11 novos).

### Pendências que sobraram

- **`WalletSummaryResource` e `ConsolidationService`**: a checagem existe, mas
  comparando e-mail em vez de id. Funciona, e é o mesmo caminho dos outros.
- **`UserResource.getAll`**: exige `ROLE_ADMIN` na `SecurityConfig`, então
  qualquer usuário autenticado sem papel de admin recebe 403. Não foi
  verificado nesta fase se o filtro por dono existe para o caso de admin.
- **Tabela deLedgers**: `Transaction` herda a posse do ativo, então não tem
  coluna de usuário. Um `GET /transactions` sem filtro por ativo não existe
  (ver Fase F), o que mantém a exposição fechada por construção.

---

## Fase F — Leitura do ledger

**Status:** concluída (2026-10-05)

### Objetivo

Matar o N+1 na listagem de transações por carteira.

### Sintoma que resolve

Não existia endpoint de transações por carteira. O front fazia `forkJoin` com um
`GET /transactions?assetId=` por ativo, que é N+1: o número de chamadas crescia
com o tamanho da carteira.

### Mudanças

- `TransactionRepository.findByAssetWalletIdOrderByTransactionDateAscIdAsc`.
  A ordenação espelha a ordem canônica por ativo (`transactionDate`, depois `id`
  como desempate) para que a concatenação dos ledgers continue reprodutível.
- `TransactionService.findByWalletId(walletId, userEmail)`, com a checagem de
  posse na camada de serviço, como nas demais operações (D7).
- `GET /transactions` passou a aceitar `assetId` **ou** `walletId`. Os dois
  juntos é 400, e nenhum também é 400.
- Front: `WalletTransactionList` trocou o `forkJoin` por uma requisição só.

### Decisões

**Posse verificada antes da consulta, não dentro do `WHERE`.** Filtrar pelo dono
dentro da query devolveria lista vazia para carteira alheia, e lista vazia é
indistinguível de "carteira sem transações" — o vazamento viria junto com a
perda do 403.

**`assetId` ficou opcional em vez de criar uma rota nova.** `GET /transactions` já
era o ponto de entrada da listagem; uma segunda rota duplicaria a mesma lógica de
ownership. Em troca, os dois casos de parâmetro inválido são 400 explícito: sem
isso, `walletId` ausente cairia no caminho de ativo e responderia 404, que parece
problema de dado em vez de chamada incompleta.

**O `catchError` que engolia erro foi removido.** O `forkJoin` usava
`catchError(() => of([]))` por ativo, então uma falha de rede virava tabela
vazia sem aviso. Com uma requisição só, a falha vai para `errorMessage`, e
"carteira sem transações" continua significando carteira sem transações.

### Testes

+11 (2 de repositório, 4 de serviço, 5 de recurso).

O teste de repositório é o que garante que a derived query funciona: nome de
derived query errado não dá erro de compilação, devolve lista vazia e passa
falso. O SQL gerado confirma o join único:

```sql
select ... from transactions t1_0
  left join assets a1_0 on a1_0.id = t1_0.asset_id
  left join wallets w1_0 on w1_0.id = a1_0.wallet_id
 where w1_0.id = ? order by t1_0.transaction_date, t1_0.id
```

---

## Fase G — Login

**Status:** concluída

### Objetivo

Encerrar o workaround do front.

### Sintoma que resolve

`LoginResponseDTO` retornava apenas `token`. O `AuthService` esperava `user` e
gravava `JSON.stringify(undefined)` = `"undefined"` no `localStorage`, e o
`getUser()` seguinte lançava exceção no `JSON.parse`, derrubando a aplicação.

Mitigado com `userFromToken()` decodificando as claims do JWT — mas o JWT não
carrega o id do usuário, então o `id` gravado era **sempre 0**, e o header
exibia e-mail em vez de nome.

### Mudanças

```java
public record LoginResponseDTO(String token, UserResponseDTO user) {}
```

`UserResponseDTO` ganhou `role`: o front lê a role para o `AdminGuard` e para a
sidebar, e ela não existia em lugar nenhum do contrato. É aditivo, e as rotas que
devolvem esse DTO (`GET /users` e `GET /users/{id}`) já exigem ADMIN.

O `AuthController` passou a buscar a entidade `User`, porque `UserDetails` carrega
apenas e-mail, senha e authorities — não tem id nem nome. Buscar a entidade é
obrigatório: qualquer atalho que use as claims reproduz o `id: 0` sem erro
visível.

No front, `userFromToken()` e `decodeToken()` foram removidos; o login grava o
usuário da resposta. O `displayName()` do header já tinha fallback
(`name || email`), então passou a exibir o nome sem alteração.

### Correlato: 401 e 403 deixaram de ser o mesmo status

Ajustando esta fase apareceu um defeito no tratamento de erro do front: ele
deslogava em **qualquer** 403. O backend respondia 403 em três situações
distintas — token inválido, rota protegida sem token, e recurso de outro usuário.
Um 403 de ownership derrubava a sessão de quem estava autenticado e legítimo.

O `SecurityConfig` agora separa os dois meanings, e o front segue a separação:

| Status | Significado | Front |
|---|---|---|
| **401** | token ausente ou inválido → reautentique | desloga e redireciona |
| **403** | autenticado, porém sem permissão | mostra "access denied", **mantém a sessão** |

`JwtAuthFilter` já convertia token inválido em requisição anônima; o que faltava
 era o status correto na saída. Com `authenticationEntryPoint` respondendo 401, o
front só precisa deslogar em 401 — e um 403 legitimo deixa de derrubar a sessão.

### Correlato: `/users` não é pública por inteiro

`JwtInterceptor` listava `/users` entre as rotas públicas para não travar o
cadastro com token velho. Mas só o **POST** é público; o **GET** é a listagem de
usuários e exige ADMIN. Dispensar o token ali fazia o próprio admin receber 403
na própria listagem. A lista virou por método.

### Verificação

- `AuthResourceTest` (4): o login devolve `id > 0` real, `name` e `role`; a senha
  não vaza; senha errada é rejeitada. Roda contra o banco, sem mock do
  `UserService` — foi justamente o mock que escondeu o id zerado.
- `AuthFailureSemanticsTest` (6): com a cadeia de filtros real, fixa 401 sem
  token, 401 com token inválido, 403 de role insuficiente, 403 de ownership com
  carteira real de outro usuário, e o cadastro/login com token velho.
- `auth.service.spec.ts` (4): id real no storage, role ADMIN preservada, queda
  para e-mail sem nome, e `user: null` não grava lixo no `localStorage`.
- `auth.interceptor.spec.ts` (8): token ausente no POST `/users` e no login,
  presente no GET `/users` e nas rotas protegidas; 401 desloga, 403 não.

**Total: 149 testes no backend, 19 no frontend.**

---

## Fase 0 — Schema versionado (Flyway)

**Status:** concluída

### Objetivo

Eliminar o descasamento que faz toda entidade nova passar no dev e quebrar em
produção.

### Sintoma que resolve

| Ambiente | Banco | `ddl-auto` | Efeito |
|---|---|---|---|
| Dev/test | H2 em memória | `update` | cria a tabela sozinho, silenciosamente |
| **Prod** | PostgreSQL | `validate` | **não cria nada — a aplicação não sobe** |

Não há nenhum `.sql` no projeto, nem Flyway, nem Liquibase. As tabelas de
produção existem só porque alguém rodou DDL na mão. A consequenceia é que a
Fase H, primeira a criar tabela, não é testável no banco real antes do deploy.

### Mudanças

- `pom.xml`: `flyway-core` **e** `flyway-database-postgresql`. No Flyway 10+ o
  suporte a PostgreSQL saiu do core e virou módulo separado; adicionar só o core
  faz a migration passar no H2 e falhar no Postgres.
- `V1__baseline.sql` **única, sem split `common`/`vendor`**: as quatro entidades
  usam `GenerationType.IDENTITY`, e `BIGINT GENERATED BY DEFAULT AS IDENTITY`
  é válido em H2 e em PostgreSQL 10+ (o compose usa 16). O mesmo raciocínio valeu
  para `DOUBLE PRECISION` no lugar de `float(53)`. Enums são **tipos nativos via
  `CREATE TYPE`** — PostgreSQL não aceita um literal ENUM como tipo de coluna.
- `ddl-auto=validate` também no dev e no teste; `update`/`create-drop` saíram.
  A migration passou a ser o que cria o schema em todo ambiente.
- `create-drop` saiu de `src/test/resources/application.properties`, o Flyway
  entrou, e a suíte inteira — inclusive os `@DataJpaTest` — exercita a V1 real.
- `baseline-on-migrate=true` com `baseline-version=1` **só nos perfis que apontam
  para banco populado** (dev e `prod`). Fica fora do ambiente de teste: lá o
  schema nasce inteiro do Flyway, e baseline calado esconderia erro real.

### Verificação

- `./mvnw clean install`: **152 testes, 0 falhas**.
- Quebrar a migration de propósito (renomear `ticker`) derruba tanto o boot
  (`@SpringBootTest`) quanto os `@DataJpaTest`, com
  `Schema-validation: missing column [ticker] in table [assets]`. Prova de que
  a suíte usa a V1, e não um schema que nasce por outro caminho.
- `FlywayBaselineTest` (3 casos) cobre o critério de aceite: um banco que já tem
  as tabelas é **carimbado** na versão 1, a V1 não roda contra ele, as tabelas
  sobrevivem e o `validate` aceita — pois o contexto só monta se o schema bater
  com as entidades.

### Critério de aceite

`./mvnw clean install` verde e, em uma cópia de um banco populado, `mvn` sobe
com `baseline-on-migrate` sem erro e aplica apenas as migrations novas.
**Satisfeito** — a cópia populada é simulada em H2 dentro do `FlywayBaselineTest`,
que monta a DDL direto na conexão e depois sobe o contexto com o baseline ligado.

### Riscos

- Verificação em PostgreSQL real fica para quem tiver Docker: `CREATE TYPE ...
  AS ENUM` e `BIGINT GENERATED BY DEFAULT AS IDENTITY` são os únicos trechos que
  o H2 não prova de forma idêntica ao Postgres. `docker compose up` com o volume
  `postgres_data` vazio deve subir e criar o schema; um banco já populado deve
  ser carimbado em vez de recriado.

---

## Fase H — Proventos

**Status:** concluída

### Objetivo

Receber e exibir proventos (dividendos e JCP) por ativo e por carteira.

### Decisões estruturais

Ver D10 (entidade separada) e D12 (indisponibilidade não é erro). A Brapi entrega
dividendos **só para ações** no plano gratuito; FIIs vêm 403. Registrado em
"Comportamento observado da Brapi". `source` é `VARCHAR(255)` + `EnumType.STRING`,
não native enum: varchar é idêntico em H2 e PostgreSQL, e o native enum é
justamente a parte que o H2 não valida (ver Riscos).

### Mudanças

- `V2__dividend_receipts.sql`: tabela `dividend_receipts` com FK para `assets`.
- `DividendSource` (`BRAPI` | `MANUAL`) e `DividendReceipt` (`asset`, `rate`,
  `paymentDate`, `exDate`, `label`, `source`).
- `DividendReceiptRepository`: consultas por ativo/carteira (ordem decrescente e
  crescente por `paymentDate`), por origem e `deleteByAssetId`.
- `BrapiAdapter.getDividends(ticker)`: chama `?dividends=true&token=`, **traduz
  o 403 em `Optional.empty()`** ("indisponível") e deixa a lista vazia significar
  "ticker sem proventos".
- `DividendService`: `findByAssetId`, `findByWalletId` (filtro de ano em memória —
  predicado temporal JPQL varia entre H2 e PostgreSQL), `summarize` agregado por
  ano, `createManual`, `syncFromBrapi` com dedup por ativo + data + valor (a Brapi
  entrega o histórico inteiro a cada chamada) e `deleteManual` (só `MANUAL`;
  receita `BRAPI` errada se corrige com re-sync).
- `DividendResource`: `POST /dividends` (manual, 201) · `GET /dividends` com
  `assetId` **xor** `walletId` + `year` opcional (400 sem nenhum ou com ambos) ·
  `GET /dividends/summary?walletId` · `POST /dividends/sync/{assetId}` ·
  `DELETE /dividends/{id}` (204).
- `AssetService.deleteAsset` agora limpa os `dividend_receipts` antes das
  transações (FK) — passou a injetar `DividendReceiptRepository`.
- `AssetPositionCalculator` **não é tocado** — é o ponto da decisão D10.
- Extensão pedida além do roadmap: `DELETE /dividends/{id}` para apagar lançamento
  manual errado.

### Riscos

- Rate limit da Brapi no sync em lote — mitigado: sync é por ativo e explícito.
- Registro com `paymentDate` nulo (de 176 do PETR4, só 121 servem) — descartado
  no sync com contador `skipped`.
- `assetIssued` vem como ISIN e não pode virar chave de ativo — sem impacto, a
  chave de dedup é ativo + data + valor.
- Validação em PostgreSQL real (Docker indisponível) foi mantida como pendente.

---

## Fase I — Valor justo por usuário

**Status:** concluída

### Objetivo

Persistir e exibir o cálculo de preço justo por ativo e por método, com as
premissas que o usuário escolheu.

### Sintoma que resolve

`Asset.fairValue` existe, mas é órfão (ver dívida técnica). Além disso, Graham
está fixo no código e não é ajustável.

### Mudanças

- Fallback corrigido em `populateMarketData`: sem PE/EPS, `fairValue` vira
  `null` (dados insuficientes), nunca `regularMarketPrice`. Os dois
  `System.out.println` de upside foram removidos.
- `V3__asset_valuations.sql`: tabela `asset_valuations` com `asset_id`,
  `method`, `inputs_json`, `formula`, `result`, `low`, `high` e `computed_at`.
- `AssetValuation` grava **histórico** — cada cálculo é um registro novo, nunca
  sobrescreve, para a evolução do preço justo ser auditável.
- `ValuationMethod` (`GRAHAM` | `BAZIN` | `DCF`) e `ValuationService`:
  - **Graham** usa PE×EPS (padrões do mercado da Brapi, com override do
    usuário): `sqrt(22.5 × PE × EPS)`.
  - **Bazin** soma os `DividendReceipt` dos últimos 12 meses e divide pelo
    `targetYield` (padrão 6%, editável).
  - **DCF** integral manual: `freeCashFlow` obrigatório; `growthRate` 4%,
    `discountRate` 10%, `terminalGrowthRate` 2% e 5 anos como padrões
    editáveis.
  - Dados insuficientes é **400 com motivo**, nunca zero: Graham sem PE/EPS,
    Bazin sem proventos nos últimos 12 meses (Riscos), DCF sem fluxo de caixa
    ou com desconto menor que o crescimento terminal.
  - Resultado com **faixa de sensibilidade** (`low`/`high`) — contrato D11,
    nunca um número único com aparência de verdade.
- `ValuationResource`: `POST /assets/{id}/valuations` (201, grava e devolve
  premissas usadas + fórmula) e `GET /assets/{id}/valuations?method=` (histórico,
  mais recente primeiro).
- Propriedade pela cadeia `asset → wallet → user` (reusa
  `AssetService.findById`), mesmo padrão da Fase E.
- `AssetService.deleteAsset` agora limpa as valuations antes de apagar o ativo.

### Contrato com o front (D11)

Todo valor pré-preenchido é exibido marcado como premissa editável (a resposta
devolve `inputs` com o que foi efetivamente usado), a fórmula aparece na tela
(`formula` persistida no histórico) e o resultado sai como **faixa de
sensibilidade** — não como número único. Um único número com aparência de
verdade seria pior que a ausência da feature.

### Riscos

- Mudar o fallback altera o valor exibido hoje. É correção de bug, mas é
  mudança visível — `fairValue` null passa a significar "dados insuficientes".
- Bazin fica sem entrada quando não há proventos registrados; responde 400
  com o motivo em vez de devolver zero.
- Validação em PostgreSQL real (Docker indisponível) foi mantida como pendente,
  como nas migrations anteriores.

---

## Fase J — Evolução patrimonial

**Status:** concluída

### Objetivo

Gerar a série histórica do patrimônio consolidado da carteira.

### Mudanças

- **Reconstrução**: `findByAssetIdAndTransactionDateLessThanEqualOrderByTransactionDateAscIdAsc`
  no `TransactionRepository` (mesma ordenação canônica do ledger, cortada em
  `<=` data); `AssetPositionCalculator.calculateByDate` devolve a posição
  vigente no fim de cada dia de transação sem duplicar a aritmética do custo
  médio; o fechamento histórico da Brapi multiplica a quantidade dia a dia.
- `BrapiAdapter.getHistoricalPrices(ticker, range)`: endpoint v1 legado
  (`/quote/{ticker}/historical`), o mesmo `baseUrl` do resto da classe — os
  docs v2 têm outro formato e não seriam coerentes com o adapter existente.
  400/403 do plano viram `Optional.empty()` (indisponível), como em `getDividends`.
- `PortfolioHistoryService`: `GET /wallet/{id}/history?from&to` reconstrói a
  série na hora, com cache de fechamentos por ticker por request. Janela da
  fonte por tipo (D13): FII vira `range=3mo`, o resto `range=5y`.
- **Snapshots diários**: `V4__portfolio_snapshots.sql` + `PortfolioSnapshot`
  (único por carteira+data, upsert), `@EnableScheduling` na aplicação e
  `@Scheduled(cron="0 30 18 * * MON-FRI", zone="America/Sao_Paulo")` no
  `PortfolioSnapshotService`. `POST /wallet/{id}/history/backfill` materializa
  dias retroativos e `GET /wallet/{id}/history/snapshots` lê as fotografias.
  Uma carteira que falhe no job não impede as demais (log de aviso por carteira).
- **D13 materializado**: a resposta declara o que não foi reconstruído em vez
  de truncar — `warnings` (dias antes da primeira transação, ledger sem
  transações, histórico indisponível) e `points[].missingTickers` +
  `complete=false` por dia com preço faltante. `totalValue` é parcial quando
  `complete=false`, nunca apresenta preço de ontem como se fosse de hoje.
- Propriedade pela cadeia `wallet → user` (mesmo padrão da Fase E), inclusive
  no backfill e no job (o job itera todas as carteiras, sem usuário).

### Riscos

- O ledger só tem histórico a partir da primeira transação. Antes disso a série
  não existe — é um limite do dado, não do código (declarado em `warnings`).
- FIIs têm no máximo 3 meses de preço histórico no plano atual; o que ficar de
  fora vira `missingTickers`, nunca erro.
- Job diário exige timezone e consciência de fechamento de mercado — a janela
  das 18:30 em `America/Sao_Paulo` é estimativa; se a fonte ainda não tiver o
  fechamento, o dia fica como reconstrução parcial (D13), nunca vazio.
- Validação em PostgreSQL real (Docker indisponível) permanece pendente, como
  nas fases anteriores; a V4 usa os mesmos tipos das V1–V3.
- O snapshot do próprio dia em que o preço ainda não fechou pode ser gravado
  como parcial; re-executar o job ou o backfill corrige (upsert).

---

## Fase K — Volatilidade histórica por ativo

**Status:** concluída e commitada em 2026-11-13 (`3181d7f`)

### Objetivo

Expor, por ticker, o desvio-padrão anualizado dos retornos diários na mesma
janela do gráfico patrimonial — uma leitura descritiva de risco passado, sem
previsão.

### Mudanças

- `GET /wallet/{id}/volatility?from&to` e `GET /wallet/volatility?from&to`
  (consolidado) em `PortfolioHistoryResource`, ambos com ownership pela cadeia
  `wallet → user` e validação de `from > to` (400). No consolidado, o mesmo
  ticker em duas carteiras vira **uma linha só**.
- `VolatilityService`: desvio-padrão **amostral** (`n-1`) dos retornos diários
  **logarítmicos** (`ln(P_t/P_{t-1})`) × `sqrt(252)`. Abaixo de **20 retornos**
  a resposta devolve `null` (não zero) e a tela declara “dados insuficientes”.
  Retornos entre fechamentos com **gap > 5 dias corridos** são descartados:
  não são retorno de um dia.
- `HistoricalPriceDTO` ganhou `adjustedClose`. A volatilidade usa o ajustado
  apenas quando a **série inteira** o traz; caso contrário cai para `close` e
  declara o ticker em `warnings` — split e provento não são retorno do ativo,
  mas inventar ajuste seria pior. A reconstrução patrimonial (Fase J) continua
  usando `close` bruto.
- Escopo: só tickers que tiveram **posição em algum dia** da janela. Com
  `from` ausente, a janela começa na primeira transação do conjunto; com `to`
  ausente, vai até hoje.
- `warnings` (D13) declara preço não ajustado e ticker sem histórico na fonte;
  cada linha traz `observations`, `firstClose` e `lastClose` para a tela
  mostrar a cobertura efetiva.

### Testes

`VolatilityServiceTest` (11): annualização com 252, mínimo de observações,
buracos > 5 dias, preferência por `adjustedClose`, fallback com aviso, filtro
de posição na janela, fonte sem histórico, dedupe entre carteiras, ledger
vazio, `from > to` e ownership. `PortfolioHistoryResourceTest` ganhou 3 casos
de contrato/rota. Total do backend: **337**.

### Riscos

- FIIs continuam limitados a ~3 meses de histórico no plano atual (agora
  `assetType` continua sem ser populado, então o range pedido é `5y` e a fonte
  pode negar): a tabela mostra `null` + aviso, nunca um número inventado.
- Duas chamadas à Brapi por ticker (histórico + volatilidade) na mesma visita
  a `/analysis`; não há cache entre endpoints. Decisão de 2026-11-13: a
  persistência dos fechamentos (6.7.3) **não** será feita aqui — vai para o ADC
  (COTAHIST + `/v1/prices`, contrato em `ADC_PLAN.md` §26). Até a integração, o
  custo por visita permanece.
- O cálculo é por ticker e ignora o tamanho da posição: não é a contribuição
  do ativo para o risco da carteira (isso exigiria covariância).

### 6.7.3 — persistência dos fechamentos (delegada ao ADC)

Decidido em 2026-11-13: o consolidator **não** ganha tabela `daily_close`. A série
diária de fechamentos passa a vir do **ADC**, coletada do COTAHIST (B3), em
`GET /v1/prices/{ticker}` e `GET /v1/prices?tickers=` — contrato congelado em
`ADC_PLAN.md` §26, com `close` (patrimônio) e `adjusted_close` + `adjusted`
(volatilidade).

A integração é a Fase 9 do ADC: cliente HTTP com timeout, retry e cache curto;
Brapi permanece como fallback. **Nada a implementar aqui até o endpoint existir** —
o custo atual (duas chamadas por ticker em `/analysis`) fica registrado como
dívida, não como bug.

---

## Fases do front dependentes disto

- **Phase 5 — Portfolio Summary**: `GET /wallet/{walletId}/summary` já existe no
  backend (`WalletSummaryResource` + `ConsolidationService`). Não depende de
  nenhum endpoint novo.
- **Feito na Fase A**: o formulário de transação já tem campo de data editável.
- **Feito na Fase B**: o formulário de ativo pede preço e data de aquisição, e o
  texto de "Novo ativo" virou "Adicionar posição".
- **Resolvido pela Fase C**: o total investido da carteira deixou de ser um campo
  congelado em `0.0` e passou a ser derivado do ledger. Era o sintoma que o
  usuário reportou, e a carteira derivada (`WalletPortfolioCalculator`)
  fecha o cálculo.
- **Consumido na Phase 5 do front**: o painel e a tela de portfólio passaram a
  ler `GET /wallet/{walletId}/summary` em vez de somar ativos carteira a
  carteira, e o P&L do painel deixou de ser um `R$ 0,00` fixo no template.
- **Módulo de análise (depende de 0, H, I e J)**: `features/analysis/` no front,
  com gráficos de proventos e de evolução patrimonial. Requer `ngx-charts@25.0.2`,
  que declara suporte a Angular 22 (`^22.0.0`) e reaproveita o `@angular/cdk` e o
  `@angular/animations` já presentes. A escolha existe porque o front evita
  dependência de gráfico desde a Phase 5 (ali a alocação saiu em CSS puro); dois
  gráficos temporais com tooltip e eixo não são razonáveis em CSS.

---

## Resumo de status

| Fase | Status | Testes |
|---|---|---|
| A — Ledger determinístico | concluída | 75 na época |
| B — Preço de aquisição | concluída | 92 na época |
| C — Carteira derivada | concluída | 109 na época |
| D — Validação e erros | concluída | 120 |
| E — Propriedade | concluída | 123 |
| F — Leitura do ledger | **concluída** | 134 |
| G — Login | **concluída** | 149 |
| 0 — Schema versionado (Flyway) | **concluída** | 152 |
| H — Proventos | **concluída** | 184 |
| I — Valor justo | **concluída** | 212 |
| J — Evolução patrimonial | **concluída** | 243 |
| K — Volatilidade histórica | **implementada** | 337 |

**Ordem de execução:** F ✅ → G ✅ → 0 ✅ → H ✅ → I ✅ → J.

A Fase 0 vem depois de F e G, e não antes, porque **F e G não criam tabela
nenhuma** (F é um endpoint de leitura, G é um campo novo no DTO). O Flyway só é
pré-requisito a partir da Fase H, que é a primeira a criar tabela. Fazer a Fase 0
antes quebraria uma fase já aprovada sem necessidade.

Cada fase só começa com a anterior verde. Base de testes hoje: **337**.

`mvn clean install`: **337 testes, 0 falhas** (243 ao fim da Fase J, mais 94 de
slices posteriores — 6.4/6.6 e Fase K). A Fase K soma 14: 11 do
`VolatilityServiceTest` e 3 do `PortfolioHistoryResourceTest` (rotas de
volatilidade, consolidado e ownership).

Frontend: **19 testes, 0 falhas** (7 da baseline, mais 4 do contrato de login e
8 dos interceptors).

Correção posterior ao status acima: `GET /transactions/{id}` verificava
ownership no `TransactionResource`, depois de um `service.findById(id)` sem
e-mail — ou seja, existia um método público de leitura sem autorização. A
chegada virou `TransactionService.findOwnedById(id, userEmail)`, o recurso
delegou a ele e o 403 agora nasce da camada de serviço, como nas demais
operações.
