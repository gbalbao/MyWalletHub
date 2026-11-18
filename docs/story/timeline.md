# Linha do tempo do MyWallet

> Gerada por /build-timeline em 2026-11-17. Datas vêm do `git log` (consolidator, visualizer, adc, hub); o "o quê" vem de `docs/estado-do-projeto.md` (auditoria de 2026-11-15). Marcos agrupam commits, não os listam. Quando só o commit mais próximo dá a data, está marcado.
> Observação: o git do Visualizer fica em `../visualizer/visualizer` (a pasta pai não é repositório).

| Data | Marco | Serviço(s) | Por que importou para o investidor |
|---|---|---|---|
| 2025-10-08 a 2025-10-24 | Primeira versão do backend: cadastro de ativos e carteiras, integração com a Brapi (cotações) e mapeadores | Consolidator | Ponto de partida: ter ativos e carteiras próprios, com cotação de mercado, em vez de planilha solta. |
| 2026-05-27 a 2026-06-04 (retomada após um período sem mexer no projeto) | Limpeza, correção de bugs e DTOs de resposta | Consolidator | Base mais estável para crescer. |
| 2026-07-27 | Login com JWT, transações e consolidação da carteira | Consolidator | O app passa a ter usuário e a consolidar posição a partir das compras e vendas registradas. |
| 2026-07-28 | Primeira bateria de testes automatizados (repositórios, serviços e controllers) | Consolidator | Confiança para mexer no cálculo sem quebrar o que já funcionava. |
| 2026-08-07 a 2026-09-17 | Nasce o front-end: projeto Angular e arquitetura base | Visualizer | Primeira interface para usar o que o backend calcula. |
| 2026-09-27 a 2026-10-02 | Telas de carteiras, ativos e transações (CRUD) | Visualizer | Dá para cadastrar e acompanhar a carteira pela tela. |
| 2026-10-02 | Posição do ativo derivada do histórico de transações (ledger) | Consolidator | A posição deixa de ser um número digitado e passa a ser reconstruída das operações, o que facilita auditar. |
| 2026-10-06 | Proventos: lançamento manual e sincronização com a Brapi | Consolidator | Acompanhar o que a carteira recebeu, não só o preço. |
| 2026-10-06 | Valuation por ativo: Graham, Bazin e fluxo de caixa descontado (DCF) | Consolidator | Primeiro passo do que motivou o projeto: valuation próprio. |
| 2026-10-07 a 2026-10-10 | Telas de análise: dividend yield por ativo, valor justo por método, gráficos de barras e série investida | Visualizer | O valuation e a alocação ficam visíveis na tela. |
| 2026-10-07 | Histórico da carteira com snapshots diários | Consolidator | Base para ver a evolução patrimonial ao longo do tempo. |
| 2026-10-28 a 2026-10-31 | Polimento de UX: aviso de alterações não salvas, formulários padronizados, cabeçalhos unificados, aviso de duplicatas | Visualizer | Atacar o gap de UX que me fez construir o app. |
| 2026-11-01 | Visão de todas as carteiras juntas (endpoints agregados e telas) | Consolidator, Visualizer | Consolidação do patrimônio inteiro, não só carteira a carteira. |
| 2026-11-02 a 2026-11-05 | Resultado realizado com compensação de prejuízos, tela de venda dedicada e explicação do porquê uma venda é recusada | Consolidator, Visualizer | Entender o resultado das vendas e por que uma operação não passou. |
| 2026-11-05 | Datas de negociação tratadas como dias de calendário (e correção do deslocamento de um dia no seletor de data) | Consolidator, Visualizer | Evita a operação aparecer no dia errado. |
| 2026-11-10 | Filtro de período nas transações | Consolidator, Visualizer | Achar operações de um intervalo específico. |
| 2026-11-11 | Painel de isenção mensal de vendas nos resultados | Visualizer | Ajuda a acompanhar o limite mensal de isenção. |
| 2026-11-12 | Volatilidade anualizada por ativo; gráfico de evolução com eixo em anos | Consolidator, Visualizer | Mais uma métrica de risco ao lado de retorno e valuation. |
| 2026-11-13 a 2026-11-14 | Nasce o ADC: coletor de fundamentos (Fundamentus) e armazenamento em Postgres próprio; importador de planilha implementado | ADC | Dados fundamentalistas para alimentar o valuation. Limite: o importador ainda não foi validado com a planilha real e a API do ADC não existe. |
| 2026-11-15 | Auditoria geral e criação do hub com agentes; planejamento centralizado | Hub | Organizar o projeto: specs, contratos e a próxima feature (OpenAPI do Consolidator). |

## Observações para não exagerar
- Features do roadmap marcadas como "Implementado" na auditoria sem data própria no git (por exemplo parte de rentabilidade e consolidação) não viraram marco separado.
- O commit de 2026-10-06 cita Graham, Bazin e DCF. Por decisão do autor (2026-11-17), pode-se dizer que o MyWallet suporta Gordon, TIR e rentabilidade real, com melhorias a implementar depois. Não há commit que os nomeie, então não atribuir data a eles.
- Pendências conhecidas (OpenAPI, ADC sem API, conteinerização nunca usada) são limitações reais e podem entrar nos posts com honestidade, sem detalhes de segurança.
