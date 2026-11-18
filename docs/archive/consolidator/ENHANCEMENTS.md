> **Histórico, arquivado em 2026-11-17.** Origem: `consolidator/consolidator/ENHANCEMENTS.md`.
> Substituído por: spec 008 (resiliência da Brapi)
> Conteúdo original abaixo, sem edição.

# Backend Enhancements — Melhorias Fora do Roadmap

> **Status:** backlog — nada aqui foi implementado ainda
> **Backend:** `consolidator` — Spring Boot 3.5.6, Java 17
> **Frontend:** `../visualizer` — Angular 22, `http://localhost:4200` → `http://localhost:8080`
> **Origem:** auditoria do consumo da Brapi durante a Fase G do `BACKEND_ROADMAP.md`
> **Roadmap aprovado:** `BACKEND_ROADMAP.md` — F → G → 0 → H → I → J, **inalterado por este arquivo**

Este arquivo registra correções e melhorias que apareceram durante a execução do
roadmap mas **não pertencem à ordem aprovada**. Ele não é uma etapa do roadmap:
nada aqui é executado por sequência, e um item só entra quando houver motivo
próprio. Os itens 1 e 2 saíram da Fase G; o resto é o que adiou.

O precedente de formato é o `E2E_Auth_Fixes.md`, que é irmão deste arquivo.

Marcadores usados:

| Marcador | Significado |
|---|---|
| `[BUG]` | Comportamento errado hoje. Não é melhoria, e adiar tem custo |
| `[MELHORIA]` | Otimização. Adiar não dói, só deixa o desperdício continuar |
| `[CORRIGIDO]` | Feito, com o registro do que foi feito |

---

## Contexto medido — limites da Brapi

Números conferidos na documentação oficial. **O painel em `brapi.dev/dashboard`
é a fonte da verdade**; a tabela abaixo é o plano publicado, não o seu plano.

| Plano | Requisições/mês | Simultâneas | Tickers/chamada | Delay |
|---|---|---|---|---|
| **Gratuito** | **15.000** | **1** | 1 | ~30 min |
| Startup (R$ 119,99) | 150.000 | 4 | 10 | ~15 min |
| Pro (R$ 139,99) | 500.000 | 16 | 20 | ~5 min |

Duas regras que mudam como se usa a cota:

- **Não há limite por segundo ou por minuto** nesses planos. O que existe é cota
  mensal e limite de requisições **simultâneas**. O `HTTP 429` pode vir de
  qualquer um dos dois.
- A cota mensal reinicia na **data de renovação** mostrada no painel de
  cobrança, não no dia 1 do mês.

O `TTL` do item 2 assume o plano Gratuito por ser o mais conservador em
atualização. **Se você estiver no Startup ou Pro, 30 min de cache é dado
obsoleto demais** — o `TTL` precisa seguir o plano.

### Os testes não consomem cota

Vale registrar porque é a suposição natural, e ela está errada:

- Os cinco arquivos de teste que tocam em Brapi injetam o adapter como mock
  (`@Mock`, `@MockBean` ou `@MockitoBean`): `AssetServiceTest`,
  `ConsolidationServiceTest`, `AssetResourceTest`, `WalletTotalInvestedTest` e
  `AssetOpeningTransactionTest`.
- `src/test/resources/application.properties` define `brapi.token=test-token`.

Ou seja: **`mvn clean install` gasta zero requisições.** Nenhum teste sai para a
API externa. Semear o banco não mudaria nada, porque o banco guarda preço de
aquisição, não preço atual — o portfolio busca preço vivo a cada requisição.

### Onde a cota é gasta de verdade

Dois call sites, ambos passando pelo `BrapiAdapter`:

| Call site | Quando | Custo |
|---|---|---|
| `ConsolidationService.java:65` | `GET /wallet/{walletId}/summary` | 1 por ticker distinto, **a cada** carregamento |
| `AssetService.fetchAssetData` (linhas 74 e 205) | criação/edição de ativo | 1 por operação |

---

## 1. [BUG] Falha da Brapi aparece como `400 Bad Request`

**Sequência: antes da Fase I.** Este não é item de melhoria e não deveria
esperar junto com o cache — ver "Por que nao e melhoria" abaixo.

### Sintoma

Não há tratamento de erro em nenhum dos três elos:

```java
// BrapiAdapter.java:28 — sem try/catch; getForObject estoura em 4xx/5xx/429
AdapterResponseDTO response = restTemplate.getForObject(url, AdapterResponseDTO.class);
```

```java
// ConsolidationService.java:65 — sem try/catch; a exceção escapa do @Transactional
Optional<AssetDataDTO> brapiData = brapiAdapter.getAssetData(ticker);
```

```java
// GenericExceptionHandler.java:67 — RuntimeException vira 400
@ExceptionHandler(RuntimeException.class)
public ResponseEntity<Map<String, String>> handleRuntime(RuntimeException ex) { ... }
```

`RestClientException` herda de `RuntimeException`, então o handler genérico a
captura.

### Impacto

Uma falha da Brapi derruba a tela de portfolio inteira com **`400 Bad Request`** —
que não é o que está acontecendo e não ajuda ninguém a diagnosticar. Vale mais o
detalhe do plano gratuito: **1 requisição simultânea** é justamente a condição
que produz `HTTP 429`.

O `AGENTS.md` já promete "Graceful Brapi failure handling" na Fase 3, e a promessa
está só parcialmente cumprida: a degradação graciosa funciona quando a Brapi
responde **vazio**, nunca quando ela **falha**.

O `400` não é um erro isolado. A Fase D corrigiu `500` → `4xx` para erros de
domínio, o que estava certo; o efeito colateral foi que o mesmo handler genérico
passou a capturar também exceções de biblioteca de terceiros e a reportá-las
como erro do cliente. A correção é mapear falha externa para `502`/`503`, não
desfazer a Fase D.

### Correção sugerida

1. `try/catch` em `ConsolidationService`, no caminho do fetch: Brapi fora do ar
   vira aviso por ativo (`warning`/`warningMessage` já existem no método), com
   `currentPrice = null`. O portfolio continua renderizando.
2. Falha de terceiro mapeada para `502`/`503`, separando "o chamador fez algo
   errado" de "a dependência está indisponível".
3. `AssetService.fetchAssetData` (linhas 74 e 205) **continua lançando** quando
   não há valor em cache. Sem isso, uma indisponibilidade da Brapi se
   apresentaria como "ticker não encontrado" na criação de ativo, mascarando a
   causa real.

### Testes

- Brapi estourando → summary responde `200` com aviso por ativo, e não `400`.
- Sem o `try/catch`, o teste volta a falhar com `400` — é o que garante que a
  regressão não volta.
- `AssetService` continua rejeitando ticker inválido na criação.

### Por que este item não é melhoria

Porque o custo de adiar não é só desperdício de cota: a Fase I calcula DCF e
consulta **fundamentals por ativo, por cálculo**, então é a fase em que o consumo
e a superfície de falha crescem ao mesmo tempo. Herdar o `400` aqui é o pior
momento possível. O item 2, esse sim, é otimização e pode esperar o tempo que for.

---

## 2. [MELHORIA] Cache da Brapi com TTL

**Sequência: a critério.** Depois da Fase I o desperdício fica maior, não
menor, porque a Fase I adiciona chamadas por ativo. Mas nada trava sem isso.

### Sintoma

O cache é **só por requisição**:

```java
// ConsolidationService.java:43 — HashMap local, descartado no fim do método
Map<String, AssetDataDTO> priceCache = new HashMap<>();
```

Dois cliques no portfolio = **2 × N** requisições por dados idênticos. E no
plano gratuito o dado só muda a cada ~30 min, então recarregar antes disso é
desperdício puro. Pior: resultado **vazio** nem entra no cache (linha 68 só
guarda quando `isPresent()`), então um ticker que dá `404`/`403` é re-buscado a
cada clique. Esse é o caso patológico, não a exceção.

### Impacto

Cota queimada sem retorno. Hoje não dói porque os testes não consomem e o uso é
pessoal, mas a Fase H (proventos) e a Fase I (fundamentals) multiplicam as
chamadas.

### Correção sugerida

Tudo dentro do `BrapiAdapter`, que é o único gargalo — os dois call sites passam
por ele, então um cache aqui cobre os dois.

**Configuração nova:**

| Propriedade | Default | Papel |
|---|---|---|
| `brapi.base-url` | `https://brapi.dev/api/quote/` | Hoje é `private final` hardcoded em `BrapiAdapter.java:16` |
| `brapi.cache-ttl` | `PT30M` | Casa com o delay do Gratuito. `PT0S` desliga |
| `brapi.cache-stale-grace` | `PT24H` | Quanto tempo um valor vencido ainda pode ser servido se a Brapi estiver fora |

`base-url` não é sofisticação: com ela, `src/test/resources` aponta para
`localhost` e um teste futuro que esqueça de mockar o adapter **falha na hora**
em vez de consumir cota silenciosamente. É a rede de proteção do item "os testes
não consomem cota" acima.

**Implementação:**

- `ConcurrentHashMap<String, CacheEntry>`, com `CacheEntry(Optional<AssetDataDTO> value, Instant expiresAt)`.
- `Clock` injetado, para testar TTL sem `sleep`.
- **Cachear resultado negativo** junto com o positivo.
- **Stale-on-error:** entrada vencida dentro da janela de graça e fetch
  falhando → devolve o valor velho em vez de propagar a falha.
- Cache **global, não por usuário**: é dado de mercado, não tem PII, e compartilhar
  aumenta o efeito.
- Sem dependência nova. Caffeine não é necessário para um map de ticker → preço;
  um map à mão são ~40 linhas e é mais fácil de testar que configurar a
  abstração de cache do Spring.

### Testes

- 2ª chamada do mesmo ticker não vai à Brapi.
- TTL expirado volta a buscar.
- Resultado negativo fica cacheado (não re-busca a cada chamada).
- Stale-on-error devolve o valor velho em vez de falhar.
- `brapi.cache-ttl=PT0S` desliga o cache — dá um caminho limpo para testar o
  resto da aplicação sem cache.

---

## 3. [MELHORIA] Respeitar o limite de 1 requisição simultânea

Duas falhas de cache simultâneas para tickers **diferentes** ainda gastam 2
requisições, e o Gratuito permite 1. Com uso pessoal a contenção é baixa, então
não trava nada. Quando for hora: um semáforo global com 1 permiso no plano
Gratuito.

## 4. [MELHORIA] Batching de tickers

Só paga a partir do Startup, que aceita 10 tickers por chamada. No Gratuito é 1
por chamada — que é exatamente o que já fazemos.

## 5. [MELHORIA] Remover o `priceCache` local do `ConsolidationService`

Com o cache no adapter (item 2), o `HashMap` da linha 43 fica redundante. Remover
deixa uma fonte só de verdade. É inofensivo manter, então fica como decisão.

## 6. [MELHORIA] Métricas de consumo

Cache hit/miss e requisições por ciclo de cobrança. Sem visibility, o item 2
não tem como ser avaliado depois de implementado — e sem isso ninguém descobre
que a cota está acabando a tempo de trocar de plano.

---

**Arquivos citados:** `controllers/BrapiAdapter.java`,
`services/ConsolidationService.java`, `services/AssetService.java`,
`common/utils/GenericExceptionHandler.java`, `src/main/resources/application.properties`