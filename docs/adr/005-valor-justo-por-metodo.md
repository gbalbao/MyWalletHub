# ADR 005 — O valor justo é calculado pelo método que o usuário escolhe

- **Status:** aceita (2026-11-16). Parcialmente implementada; o ajuste do `fairValue` do ativo fica na spec 004
- **Origem:** BACKEND_ROADMAP D11; decisão do usuário ao rejeitar a spec 007 do backlog
- **Serviços:** Consolidator, Visualizer

## Decisão
- Não existe um "valor justo" único. O usuário escolhe o método (Graham, Bazin ou DCF), e o `ValuationService` calcula.
- O DCF usa premissas editáveis, que aparecem marcadas como premissa, com a fórmula visível e o resultado mostrado como faixa de sensibilidade, nunca como número solto.
- O `fairValue` do ativo deixa de ser o Graham automático do cadastro e passa a mostrar o último valuation calculado pelo usuário, junto com o método (spec 004).

## Por quê
A Brapi não fornece fluxo de caixa, crescimento nem taxa de desconto. Um número único com aparência de verdade é pior do que não ter o número.
