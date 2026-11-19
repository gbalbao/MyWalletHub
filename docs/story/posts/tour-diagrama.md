# Diagrama do post 2 (tour) — descrição para o Excalidraw

> Material de apoio. Não é o rascunho do post. Sem dados reais, sem endpoints, sem detalhes de segurança.

## Layout (da esquerda para a direita, 3 colunas)

**Coluna 1 — Usuário e interface**
- Caixa "Visualizer" (Angular). Legenda: "Telas: carteiras, transações, análise".
- Acima dela, um ícone ou rótulo "Investidor".
- Seta Investidor → Visualizer.

**Coluna 2 — Núcleo**
- Caixa grande "Consolidator" (Java, Spring Boot). Legenda: "Posições, resultados, proventos, valuation, histórico".
- Abaixo dela, cilindro "Banco do Consolidator".
- Seta Consolidator ↔ banco.
- Seta Visualizer → Consolidator, rótulo "consome a API".

**Coluna 3 — Dados**
- Caixa "ADC" (Python). Legenda: "Coleta de fundamentos e importação de planilha".
- Abaixo dela, cilindro "Banco do ADC" (separado do outro).
- Seta ADC ↔ banco.
- Seta ADC → Consolidator, rótulo "envia o histórico importado".

**Fontes externas (faixa na parte de cima ou de baixo)**
- Caixa tracejada "Brapi" (cotações e proventos), com seta para o Consolidator.
- Caixa tracejada "Fundamentus" (fundamentos), com seta para o ADC.
- Caixa tracejada "Planilha" (histórico de operações), com seta para o ADC.

## Elementos de apoio
- Uma legenda de cores: azul = serviço, cinza = banco, tracejado = fonte externa, laranja = ainda em construção.
- Marque em laranja "ADC → Consolidator" para dados de preços e cliente do ADC: ainda não existe. Se preferir não mostrar o que está em construção, omita a seta e a legenda laranja.
- Título: "MyWallet — how it fits together".
- Frase de rodapé: "One owner for the API and the calculations: the Consolidator."

## Base factual (conferir antes de publicar)
- Serviços e stacks: CLAUDE.md do hub.
- Brapi e proventos no Consolidator; Fundamentus e importador no ADC: `docs/estado-do-projeto.md`.
- Banco do ADC separado: CLAUDE.md do hub (ADC com PostgreSQL próprio).
- O envio do histórico importado do ADC para o Consolidator existe como código do importador; a validação com planilha real está pendente.
