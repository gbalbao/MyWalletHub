# 004 — Precificação: cotação atual e P&L

## Por quê
A auditoria (`docs/estado-do-projeto.md` §5) achou quatro problemas de precificação:
- **C1, a única quebra de contrato.** Em `GET /assets`, `AssetResponseDTO.currentValue` é o preço da Brapi gravado no cadastro do ativo e nunca atualizado. As telas de ativos, de valor justo e o formulário de ativo usam esse campo como cotação, então mostram P&L e potencial de valorização errados.
- **C2.** O dashboard e o `sumPortfolioTotals` somam os resumos das carteiras no front, incluindo no investido os ativos sem cotação. Isso cria um prejuízo que não existe.
- **C2 também no backend (achado na escrita desta spec).** O resumo de cada carteira (`ConsolidationService`, `PortfolioSummaryDTO`) calcula `totalProfitLoss = totalCurrentValue - totalInvested`. O custo de um ativo sem cotação conta como prejuízo. O resumo geral (`/wallet/summary`) já faz certo, com `pricedInvested`.
- **C5.** `AssetResponseDTO.fairValue` é um Graham automático, calculado só no cadastro, que envelhece e não tem relação com os valuations que o usuário calcula.

## Objetivo
- Toda tela que mostra cotação usa o preço atual do mercado. Quando a cotação não vem, mostra "sem cotação", nunca zero.
- O P&L de cada carteira e do total considera só as posições com preço, e diz quais ficaram de fora.
- O "valor justo" de um ativo é o último valuation que o usuário calculou, com o método e a data.

## Critérios de aceite
- [ ] **`GET /assets` e `GET /assets/{id}`** (e o mesmo DTO em `WalletResource`) trazem `currentPrice`: o preço unitário atual da Brapi, buscado na leitura. Quando a Brapi falha ou não tem preço, o campo vem `null`, a resposta continua 200 e não vem zero. O campo `currentValue` deixa de existir nesse DTO.
- [ ] Na mesma requisição, cada ticker é buscado na Brapi uma vez só, mesmo que apareça em mais de uma carteira. Um teste com a Brapi simulada conta as chamadas.
- [ ] **Migration V5** remove as colunas `assets.current_value` e `assets.fair_value`. Com o `ddl-auto=validate`, o contexto sobe e os testes passam no H2. O SQL é compatível com PostgreSQL.
- [ ] **`fairValue`** em `AssetResponseDTO` é o `result` do valuation mais recente do ativo, de qualquer método (`findByAssetIdOrderByComputedAtDescIdDesc`, o primeiro da lista). Dois campos novos acompanham: `fairValueMethod` (`GRAHAM`, `BAZIN` ou `DCF`, o enum `ValuationMethod`) e `fairValueComputedAt`. Sem valuation, os três vêm `null`.
- [ ] O cadastro e a troca de ticker não calculam mais Graham: `populateMarketData` deixa de gravar `fairValue`. Calcular um valuation novo muda o `fairValue` da próxima leitura do ativo.
- [ ] **O resumo de cada carteira** (`GET /wallet/{id}/summary`) ganha `pricedInvested`, o custo só das posições com preço.
  - `totalProfitLoss = totalCurrentValue - pricedInvested`.
  - `totalProfitLossPercentage` usa `pricedInvested` como divisor e vem `null` quando `pricedInvested` for 0, como no `/wallet/summary`.
  - `totalInvested` continua sendo o custo de todas as posições.
- [ ] Um teste prova que uma carteira com um ativo cotado e outro sem cotação mostra P&L só do cotado, e que os totais por carteira e o geral (`/wallet/summary`) batem.
- [ ] **Visualizer:**
  - `asset-list`, `fair-value` e `asset-form` usam `currentPrice`. Sem cotação, mostram "—" ou "sem cotação", e o P&L e o potencial do ativo ficam vazios, não zero.
  - A tela de valor justo mostra o `fairValue` com o método e a data ("Graham, 12/11/2026"). Sem valuation, mostra "sem valuation" e um atalho para calcular.
- [ ] O dashboard e a página de portfólio tiram os totais gerais de `GET /wallet/summary` (`PortfolioAggregate`): `totalInvested`, `totalCurrentValue`, `totalProfitLoss`, `totalProfitLossPercentage` e `missingPrices`. Os cards de carteira usam o `pricedInvested` e o P&L do resumo de cada carteira, sem somar nem recalcular no front.
- [ ] `sumPortfolioTotals` é removido. `toPortfolioCard` deixa de trocar `null` por 0. Valores `null` aparecem como "—", e um percentual `null` não vira "0%".
- [ ] Quando `missingPrices` não está vazio, o dashboard e o portfólio mostram um aviso com os tickers sem cotação, explicando que eles ficaram fora do P&L.
- [ ] **Contrato:** `contracts/openapi.yaml` é regenerado depois da revisão do diff, e C1, C2 e C5 saem dos problemas conhecidos. `/check-contract` termina sem divergência, e o `integration-reviewer` confirma que o ADC não lê `currentValue` nem `fairValue` do ativo.
- [ ] `./mvnw test` e `npm test` passam, com testes novos para os pontos acima.

## Mudanças de contrato
Só o Consolidator muda. O Visualizer é o único consumidor afetado.

| Onde | Hoje | Depois | Quebra? |
|---|---|---|---|
| `AssetResponseDTO.currentValue` | `Double`, preço unitário gravado no cadastro | **Removido** | Sim, para o Visualizer (`asset.models.ts`, `asset-list`, `fair-value`, `asset-form`) |
| `AssetResponseDTO.currentPrice` | — | `Double` nullable, cotação unitária atual da Brapi em BRL; `null` = sem cotação | Campo novo |
| `AssetResponseDTO.fairValue` | Graham automático do cadastro | `result` do último valuation do usuário; `null` = sem valuation | Muda o significado, sem mudar o tipo |
| `AssetResponseDTO.fairValueMethod` | — | `ValuationMethod` nullable | Campo novo |
| `AssetResponseDTO.fairValueComputedAt` | — | Mesmo tipo e formato do `ValuationResponseDTO.computedAt` de hoje (date-time, `java.util.Date`); a 005 converte os dois juntos | Campo novo |
| `PortfolioSummaryDTO.pricedInvested` | — | `Double`, custo só das posições com preço | Campo novo |
| `PortfolioSummaryDTO.totalProfitLoss` | `totalCurrentValue - totalInvested` | `totalCurrentValue - pricedInvested` | Muda o valor (corrige o prejuízo que não existia) |
| `PortfolioSummaryDTO.totalProfitLossPercentage` | `double`, 0.0 sem investido | `Double` nullable, sobre `pricedInvested`; `null` quando ele for 0 | Muda o valor e passa a aceitar null |
| Banco | `assets.current_value`, `assets.fair_value` | Removidas (V5) | Interno |

`AssetSummaryDTO.currentValue` (o valor da posição no summary) não muda.

## Tarefas por serviço
### Consolidator
- [ ] **Cotação ao vivo em `AssetResponseDTO`:**
  - trocar `currentValue` por `currentPrice`, buscado na leitura pelo `brapiAdapter`, com um cache por requisição como o do `ConsolidationService`;
  - centralizar a montagem do DTO, hoje repetida em `AssetResource:51,115` e `WalletResource:157`;
  - não gravar mais `currentValue` no mapper.
- [ ] **`fairValue` vindo do último valuation:** preencher `fairValue`, `fairValueMethod` e `fairValueComputedAt` a partir do `AssetValuationRepository`, evitando uma consulta por ativo nas listas. Tirar o Graham de `populateMarketData`.
- [ ] **Migration V5:** remover `assets.current_value` e `assets.fair_value` e os campos da entidade `Asset`. Conferir com o H2 (`validate`) e revisar o SQL para PostgreSQL.
- [ ] **`PortfolioSummaryDTO` por carteira:** acrescentar `pricedInvested` e recalcular o P&L e o percentual como no agregado. Testes do caso misto, com um ativo cotado e outro sem cotação.
- [ ] **Documentação:** atualizar os `@Schema` dos campos alterados e tirar as notas C1, C2 e C5.
### Visualizer
- [ ] **Models e telas de ativo:** `asset.models.ts` com `currentPrice`, `fairValueMethod` e `fairValueComputedAt`. `asset-list`, `fair-value` e `asset-form` passam a usar `currentPrice` e tratam `null` como "sem cotação".
- [ ] **Valor justo:** mostrar o último valuation com o método e a data, e o estado "sem valuation" com um atalho para calcular.
- [ ] **Totais:**
  - o dashboard e o portfólio usam `getTotals()` (`/wallet/summary`) para o total geral e o `pricedInvested` de cada carteira;
  - remover `sumPortfolioTotals` e a troca de `null` por 0 em `toPortfolioCard`;
  - mostrar o aviso de `missingPrices`.
- [ ] **Testes** dos estados com cotação, sem cotação, sem valuation e com carteira mista.
### ADC
- Nenhuma tarefa. O importador não lê `currentValue` nem `fairValue`; o `integration-reviewer` confirma.
### Hub (arquiteto)
- [ ] Revisar o diff do contrato, regenerar `contracts/openapi.yaml` com `--update`, atualizar os problemas conhecidos e rodar `/check-contract`.

## Fora de escopo
- O formato das datas (`computedAt`, `paymentDate`, `exDate` como `java.util.Date`): spec 005.
- A moeda e o momento da cotação no contrato (C7), e as unidades de percentual e volatilidade (C4): spec 006.
- Resiliência da Brapi: cache com TTL entre requisições, timeout, tratar a falha como aviso, e não como 400, no `POST /assets`. Fica na spec 008. Aqui só vale que a falha na leitura dá `currentPrice = null`.
- Escolher um "método preferido" de valuation por ativo. Vale sempre o mais recente.
- Histórico patrimonial e snapshots: continuam com a regra de hoje.

## Riscos e dúvidas
- **Decidido (2026-11-19):** `currentValue` vira `currentPrice` ao vivo, e a coluna antiga sai.
- **Decidido (2026-11-19):** o `fairValue` gravado é apagado, e o campo passa a ser o último valuation, com o método.
- **P/L e LPA não são campos do cadastro.** Na pergunta eu disse que eram, mas `AssetCreateDTO` só tem `ticker`, `walletId`, `amount`, `unitPrice` e `acquisitionDate`. O Graham automático usava o P/L e o LPA que a Brapi devolvia no cadastro. Não há o que manter no cadastro; esses dados continuam disponíveis para a tela de valuation pela própria Brapi.
- **Latência de `GET /assets`:** a lista passa a chamar a Brapi a cada leitura, um ticker por vez, como o summary já faz. Com muitos ativos a tela fica mais lenta. O cache entre requisições entra na 008; se a lentidão incomodar antes, a 008 sobe de prioridade.
- **Migration destrutiva:** a V5 apaga `current_value` e `fair_value`. Os dois são reconstruíveis: a cotação vem ao vivo e o Graham era automático. O banco de produção (PostgreSQL) nunca foi validado; o teste é no H2.
- **Ordem de entrega:** o Consolidator e o Visualizer precisam ir juntos. Sem o front novo, as telas de ativo ficam sem cotação, porque `currentValue` some.
- **`fairValueComputedAt` herda o problema C6.** O campo usa o mesmo tipo de `computedAt` para não criar um terceiro formato de data. A spec 005 converte todos de uma vez.

## ClickUp
Pasta MyWallet. Os cards ficam na lista do serviço; as dependências estão cadastradas no ClickUp.
- [[Consolidator] 004 — Cotação ao vivo, fairValue do último valuation e P&L por carteira](https://app.clickup.com/t/1dfhfaqcynk): depende do [Consolidator] 002
- [[Visualizer] 004 — Cotação atual, valor justo e totais do backend](https://app.clickup.com/t/1dfhfaqcynm): depende do [Consolidator] 004 e do [Visualizer] 002
- [[Hub] 004 — Atualizar contrato e check-contract](https://app.clickup.com/t/1dfhfaqcynn): depende do [Consolidator] 004, do [Visualizer] 004 e do [Hub] 002
