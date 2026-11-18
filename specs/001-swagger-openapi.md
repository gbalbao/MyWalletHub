# 001 — Swagger + OpenAPI (API como está)

## Por quê
`contracts/` está vazio, e a fonte de verdade de fato são os DTOs Java do Consolidator (auditoria, `docs/estado-do-projeto.md` §5). Sem contrato, o `integration-reviewer` só compara código com código, e as specs seguintes (002, 004, 005, 006, 008, 010) mudariam a API sem registro. Algumas rotas já mudaram sem constar em plano nenhum (C8). O springdoc 2.5.0 está no `pom.xml`, mas sem configuração, com as rotas bloqueadas (401) e provavelmente incompatível com o Spring Boot 3.5.6.

## Objetivo
Ter um Swagger navegável no Consolidator e um primeiro `contracts/openapi.yaml` real, que descreva a API **exatamente como ela é hoje**, incluindo os problemas conhecidos. Este contrato é a base para todas as specs seguintes. Nenhum comportamento da API muda nesta spec.

## Critérios de aceite
- [ ] Com o Consolidator rodando localmente (perfil padrão), `GET /v3/api-docs` responde 200 sem token, e `/swagger-ui/index.html` abre e lista todos os controllers.
- [ ] O Swagger UI tem o esquema Bearer JWT configurado: depois de colar o token do `POST /auth/login` em "Authorize", uma chamada autenticada (ex.: `GET /wallet`) responde 200.
- [ ] `contracts/openapi.yaml` existe no hub e contém todas as rotas do inventário (§4.1 da auditoria do Consolidator): `/auth`, `/users`, `/wallet` (incluindo summary, history, snapshots, backfill, volatility e merge), `/assets` (incluindo valuations), `/transactions` (incluindo results) e `/dividends` (incluindo summary e sync).
- [ ] Cada operação do YAML tem os parâmetros, o schema de request e response e os códigos de status que o código realmente devolve (200/201/204, 400, 401, 403, 404).
- [ ] O YAML documenta, sem alterar código:
  - unidades: percentuais de 0 a 100 (`profitLossPercentage`, `allocationPercentage`, `totalProfitLossPercentage`); `annualizedVolatility` como fração de 0 a 1; valores monetários em BRL implícito, `double` sem arredondamento;
  - formatos de data reais: `LocalDate` (`yyyy-MM-dd`) em transações, histórico e snapshots; `java.util.Date` em `computedAt`, `paymentDate` e `exDate`; `Instant` em `generatedAt`;
  - o significado de null em cada campo que pode vir null (ex.: preço ausente = "sem dado", nunca zero);
  - os três formatos de erro: `{campo: mensagem}` (validação), `{error}` e `{error, code}` (regra de negócio, com os códigos de `BusinessRuleException`);
  - quais rotas são públicas (`/auth/**`, `POST /users`) e quais exigem ADMIN (`GET /users/**`).
- [ ] O YAML tem uma seção "Problemas conhecidos" (em `info.description` e nas descrições dos campos afetados), em que cada item aponta para a spec que vai corrigi-lo (tabela em "Mudanças de contrato").
- [ ] Os testes atuais do Consolidator (`./mvnw test`) continuam passando, com o mesmo número de testes ou mais.
- [ ] No perfil `prod`, `/v3/api-docs` e `/swagger-ui` estão desligados (`springdoc.api-docs.enabled=false` e `springdoc.swagger-ui.enabled=false`) e indisponíveis. Um teste com o perfil `prod`, ou uma verificação de propriedade, comprova isso. Em MockMvc respondem 404; no servidor real, hoje, respondem 401, pelo problema de `sendError` corrigido na spec 002 (ajuste de 2026-11-17).
- [ ] O script `scripts/check_openapi.py` no hub:
  - sobe o Consolidator no perfil dev (H2 em memória, `BRAPI_TOKEN` fictício) ou usa uma instância que já esteja na 8080;
  - baixa `/v3/api-docs.yaml`;
  - normaliza quebras de linha e espaços finais e compara o texto com o `contracts/openapi.yaml`. A saída do springdoc foi idêntica em 3 subidas independentes, então não é preciso reordenar as chaves (ajuste de 2026-11-17);
  - sai com código 0 quando são iguais e com código diferente de 0 e um diff legível quando divergem;
  - derruba o Consolidator se tiver sido ele a subir.
- [ ] O `integration-reviewer` (`/check-contract`) roda contra o novo contrato e não aponta divergência entre YAML e código. As divergências entre o Visualizer e o ADC e o contrato podem existir, mas precisam estar listadas na seção de problemas conhecidos.

## Mudanças de contrato
**Comportamento da API: nenhuma.** As únicas rotas novas são de infraestrutura: `GET /v3/api-docs`, `GET /v3/api-docs.yaml` e `/swagger-ui/**`, todas públicas. Nada quebra para o Visualizer nem para o ADC.

**Novo artefato:** `contracts/openapi.yaml` (OpenAPI 3.1.0, a versão padrão do springdoc 2.8), exportado do springdoc sem edição manual. O springdoc não infere sozinho as descrições de unidade, null e erro; elas entram como anotações `@Schema`/`@Operation` no código, para o YAML gerado já sair completo.

**Problemas conhecidos a registrar (sem corrigir):**

| ID | Problema como está hoje | Onde no contrato | Corrigido por |
|---|---|---|---|
| C1 | `AssetResponseDTO.currentValue` é o preço unitário gravado no cadastro e nunca atualizado; em `AssetSummaryDTO`, `currentValue` é o valor total da posição | `AssetResponseDTO`, `AssetSummaryDTO` | 004 |
| C2 | Não é de contrato: o front calcula P&L localmente. Registrar que o P&L oficial vem de `PortfolioTotalsDTO.totalProfitLoss` e `pricedInvested` | `PortfolioTotalsDTO` | 004 |
| C5 | `AssetResponseDTO.fairValue` é Graham automático (`sqrt(22.5*PE*EPS)`), calculado só no cadastro e ao trocar o ticker | `AssetResponseDTO.fairValue` | 004 (passa a mostrar o último valuation do usuário) |
| C3 | O Consolidator espera `transactionDate` e `acquisitionDate` como `yyyy-MM-dd`; o ADC envia `...T00:00:00.000Z` e só funciona pela tolerância do Jackson | `TransactionDTO`, `AssetCreateDTO` | 005 |
| C6 | `computedAt`, `paymentDate` e `exDate` são `java.util.Date`, enquanto o resto da API usa `LocalDate` | `ValuationResponseDTO`, `DividendReceiptDTO`, `DividendReceiptResponseDTO` | 005 |
| C4 | Volatilidade em fração (0 a 1) e os demais percentuais em 0 a 100 | `VolatilityResponseDTO` | 006 |
| C7 | Moeda e momento da cotação não são expostos | `AssetSummaryDTO` | 006 |
| C10 | `walletId` é `String` em `AssetCreateDTO` e `Long` no resto | `AssetCreateDTO` | 006 |
| — | `PUT/DELETE /users/{id}` não verificam o dono; `@PreAuthorize` não tem efeito | `/users/{id}` | 002 |
| — | `DELETE /wallet/{id}` com ativos provavelmente falha por FK (400 genérico) | `/wallet/{id}` | 002 |
| — | `POST /wallet` com `assets` nulo responde 400 (NPE) | `WalletDTO` | 002 |
| — | Falha da Brapi em `getAssetData` vira 400 no summary e no total | `/wallet/{id}/summary`, `/wallet/summary`, `POST /assets` | 008 |
| — | `Asset.assetType` nunca é preenchido | `AssetResponseDTO` e regras de histórico | 010 |
| C8 | Rotas que mudaram sem registro: proventos sem `assetId`/`walletId` retornam todas as carteiras; `sync` aceita id ou ticker; `/transactions` sem filtro retorna tudo do usuário; `POST /wallet/{id}/assets/merge` | rotas citadas | Resolvido por esta spec (passa a estar documentado) |

## Tarefas por serviço
### Consolidator
- [ ] Atualizar `springdoc-openapi-starter-webmvc-ui` de 2.5.0 para a 2.8.x compatível com o Spring Boot 3.5.6 e confirmar que o contexto sobe e que `/v3/api-docs` responde.
- [ ] Liberar `/v3/api-docs/**` e `/swagger-ui/**` no `SecurityConfig`, sem mudar nenhuma outra regra, e cobrir com teste (rota pública 200; rota de negócio sem token continua 401).
- [ ] Desligar o springdoc no `application-prod.properties` e cobrir com teste.
- [ ] Criar a configuração do OpenAPI (`OpenApiConfig`): título, versão, servidor local e esquema de segurança Bearer JWT aplicado globalmente, com exceção das rotas públicas.
- [ ] Anotar os controllers de autenticação, usuários e carteiras (`AuthController`, `UserResource`, `WalletResource`, `WalletSummaryResource`) com `@Tag`, `@Operation` e as respostas de erro reais.
- [ ] Anotar os controllers de ativos, transações, proventos, valuation e histórico (`AssetResource`, `TransactionResource`, `DividendResource`, `ValuationResource`, `PortfolioHistoryResource`).
- [ ] Anotar os DTOs com `@Schema`: unidades, formato de data, semântica de null e as notas de "problema conhecido" da tabela acima.
- [ ] Documentar os schemas de erro (validação, `{error}`, `{error, code}` com os códigos de `BusinessRuleException`).
### Hub (arquiteto)
- [ ] Escrever `scripts/check-openapi` (ver critério de aceite) e chamá-lo a partir do `/check-contract`.
- [ ] Exportar o `/v3/api-docs.yaml` para `contracts/openapi.yaml` sem edição manual (a revisão acontece nas anotações do código), com a seção "Problemas conhecidos".
- [ ] Escrever `contracts/README.md`: como regenerar o YAML, convenções (unidades, datas, null) e a regra "contrato primeiro".
- [ ] Rodar `/check-contract` contra o novo contrato e registrar o resultado.
### Visualizer
- Nenhuma tarefa. O Visualizer só consome o contrato; as divergências dele entram como problemas conhecidos.
### ADC
- Nenhuma tarefa. A divergência C3 fica registrada e é corrigida na 005.

## Fora de escopo
- Qualquer correção de comportamento, nome ou tipo de campo (vai para 002, 004, 005, 006, 008 e 010).
- O contrato da API do ADC (`/v1/prices`, `/v1/companies`): spec 011/012.
- Gerar clientes TypeScript ou Python a partir do OpenAPI.
- Rodar a verificação de divergência em CI (não há CI ainda; spec 015).
- Migrar os planos antigos para o hub (spec 003).

## Riscos e dúvidas
- **Decidido (2026-11-16):** o Swagger fica ligado só em dev e desligado em `prod`.
- **Decidido (2026-11-16):** a verificação de divergência é um script no hub que sobe o Consolidator e compara com `contracts/openapi.yaml`.
- **O script depende do Java local e do `mvnw`:** ele roda na máquina do usuário. Se a subida demorar, aceitar uma instância que já esteja rodando na 8080 evita esperar a cada verificação.
- **YAML gerado contra revisado à mão:** se a revisão manual acrescentar texto que não está nas anotações, a verificação de divergência acusa diferença. Regra proposta: tudo que é descritivo entra como anotação no código, e o YAML do hub é sempre o exportado, sem edição posterior.
- **Compatibilidade do springdoc:** a quebra com Spring 6.2 na 2.5.0 é conhecida, mas não foi testada em execução nesta máquina. A versão exata da 2.8.x é confirmada na primeira tarefa.
- **Anotações em massa:** o volume de `@Schema` nos DTOs é grande. O risco é a revisão do diff ficar pesada; por isso as anotações estão divididas em várias tarefas.
- **`java.util.Date` no YAML:** o springdoc representa esse tipo como `date-time`. Isso está correto para o comportamento atual, e a nota do C6 explica a diferença em relação aos campos `LocalDate`.

## ClickUp
Pasta MyWallet. Os cards ficam na lista do serviço; as dependências estão cadastradas no ClickUp.
- [[Consolidator] 001 — Swagger + OpenAPI (API como está)](https://app.clickup.com/t/1dfhfaqc8a3)
- [[Hub] 001 — contracts/openapi.yaml e script check-openapi](https://app.clickup.com/t/1dfhfaqc8a4): depende do card do Consolidator
