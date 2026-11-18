# Estoque de posts

> Atualizado em 2026-11-17. Status possíveis: ideia, rascunhado, publicado.
> Posts em inglês, com pt-BR logo abaixo. Ângulo padrão: problema → benefício → o que o app faz. Um destaque técnico por post.
> Regra: falhas e bugs só viram post depois de corrigidos e se melhorarem a credibilidade. Sem valores, dados de carteira ou detalhes de segurança.
> Reorganizado em temas amplos (cada um agrupa vários marcos da `timeline.md`), em vez de um post por feature. Os temas podem render séries.

## Ordem sugerida
1. Origem — rascunhado (`2026-11-17-origem.md`)
2. Tour da arquitetura
3. Do registro de operações ao patrimônio
4. Valuation e risco
5. UX
6. Dados e bastidores do processo

## Posts

### 1. Por que construí minha própria carteira de investimentos
- Status: rascunhado (`docs/story/posts/2026-11-17-origem.md`)
- Ângulo: gaps das ferramentas gratuitas → controle e métricas que não existiam → MyWallet.

### 2. Tour: como o MyWallet é montado
- Status: ideia
- Marcos: 2025-10 a 2026-11 (visão geral da timeline)
- Ângulo: um app de investimentos precisa de cálculo confiável, boa interface e dados de fundamentos → três serviços com papéis separados (Consolidator em Java/Spring Boot, Visualizer em Angular, ADC em Python) → o que cada um faz hoje.
- Destaque técnico: um dono para a API e para os cálculos (Consolidator), com interface e coleta de dados como consumidores.
- Limite honesto: ADC ainda em construção; o contrato formal (OpenAPI) ainda vem. Se a spec 001 estiver fechada na publicação, citar como entregue.
- Aqui entra design e padrões, em nível de visão geral. Detalhes de cada decisão ficam para os posts seguintes.

### 3. Do registro de operações ao patrimônio completo
- Status: ideia
- Marcos: 2026-10-02 (ledger), 2026-11-01 (todas as carteiras), 2026-11-02 a 2026-11-05 (resultado realizado e recusas de venda), 2026-11-10 (filtro de período), 2026-11-11 (isenção mensal)
- Ângulo: planilha com números digitados desatualiza e esconde erros → posição reconstruída das compras e vendas, agregada por todas as carteiras → o app mostra posição, resultado realizado e o porquê de uma venda ser recusada.
- Destaque técnico: derivar a posição por replay do histórico de operações.
- Limite honesto: datas tratadas como dias de calendário (post de bug só se estiver corrigido por completo).

### 4. Valuation e risco ao lado da posição
- Status: ideia
- Marcos: 2026-10-06 (Graham, Bazin, DCF), 2026-10-07 a 2026-10-10 (telas de análise, DY, valor justo por método), 2026-10-07 (histórico e snapshots), 2026-11-12 (volatilidade e evolução)
- Ângulo: valuation e risco em planilhas separadas → tudo no mesmo lugar → o app calcula por método e mostra retorno, valuation, proventos e volatilidade. Gordon, TIR e rentabilidade real citados como suportados (decisão do autor). Deixar claro que o app organiza e analisa, não recomenda.
- Destaque técnico: métodos de valuation intercambiáveis por usuário.
- Limite honesto: revisar antes de rascunhar os limites citados na auditoria (ex.: valor justo do cadastro que envelhece).

### 5. UX: a razão de eu ter começado
- Status: ideia
- Marcos: 2026-09-27 a 2026-10-02 (CRUD), 2026-10-28 a 2026-10-31 (polimento), 2026-11-04 (diálogo de venda anterior à compra), 2026-11-10 (botões unificados), 2026-11-12 (eixo em anos)
- Ângulo: UX fraca era um dos gaps das outras ferramentas → padronização de formulários, avisos de alterações não salvas e mensagens que explicam → o app guia em vez de só devolver erro.
- Destaque técnico: componentes compartilhados para cabeçalhos e formulários.

### 6. Dados de fundamentos e como organizo o trabalho
- Status: ideia
- Marcos: 2026-11-13 a 2026-11-15 (ADC, auditoria, hub com agentes)
- Ângulo: fundamentos coletados à mão e planos espalhados → coletor com cache e Postgres próprio, specs e contratos centralizados num hub → decisões antes do código.
- Destaque técnico: contrato primeiro (OpenAPI do Consolidator), depois implementação.
- Limite honesto: API do ADC, preços diários e agendamento ainda não existem. Publicar como "em construção", preferencialmente depois da spec 001 concluída.

## Bugs e correções (só depois de corrigidos)
- Bug do dia anterior nas datas: aguardar correção completa; decidir com o autor se ajuda a credibilidade.
- Correção de segurança do Consolidator: só publicar se o autor decidir, pelo ângulo da correção.
