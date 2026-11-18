# ADR 006 — Indisponibilidade de fonte externa é estado de negócio, não erro

- **Status:** aceita. Implementada em proventos e histórico; falta em `getAssetData` (spec 008)
- **Origem:** BACKEND_ROADMAP D12, D13
- **Serviços:** Consolidator, Visualizer

## Decisão
- Quando a Brapi não entrega um dado (ex.: 403 em dividendos de FII no plano gratuito), o adapter devolve "indisponível com motivo", não uma exceção. O front mostra um aviso e oferece o lançamento manual.
- Reconstruções históricas são best-effort. A resposta diz o que ficou incompleto (`complete`, `missingTickers`), em vez de truncar em silêncio.

## Consequências
- Hoje, uma falha em `getAssetData` ainda vira 400 no resumo da carteira, o que viola esta decisão. A correção está na spec 008.
