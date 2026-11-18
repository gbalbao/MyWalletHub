# Contratos

O contrato entre os serviços do MyWallet. O Consolidator é o dono da API; o Visualizer e o ADC a consomem.

| Arquivo | O que é |
|---|---|
| `openapi.yaml` | API do Consolidator (OpenAPI 3.1), exportada do springdoc. Criado pela spec 001 |

## Regras
- **Contrato primeiro.** Uma spec que muda a API atualiza este contrato antes da implementação, e a implementação só termina quando o código bate com ele.
- **O YAML não é editado à mão.** Descrições, unidades e notas vivem em anotações (`@Schema`, `@Operation`, `OpenApiConfig`) no Consolidator. O arquivo aqui é sempre o exportado, assim a verificação de divergência compara texto com texto.
- **Problemas conhecidos ficam visíveis.** O contrato descreve a API como ela é, incluindo os defeitos. Cada um aparece na tabela "Problemas conhecidos" do `info.description` e no campo afetado, com a spec que vai corrigi-lo. Ao corrigir, a spec remove a nota.

## Convenções (resumo; o detalhe está no `info.description`)
- **Dinheiro:** BRL implícito, `double`, sem arredondamento.
- **Percentuais:** de 0 a 100. Exceção: `annualizedVolatility`, fração de 0 a 1.
- **Datas:** `yyyy-MM-dd` (`LocalDate`) na maior parte da API; `date-time` em `computedAt`, `paymentDate`, `exDate` (`java.util.Date`) e `generatedAt` (`Instant`).
- **null:** significa "sem dado", nunca zero.
- **Erros:** `{campo: mensagem}` (validação), `{error}` e `{error, code}` (regra de negócio).

## Verificar e regenerar
Requer Java 17 (`JAVA_HOME`) e Python 3, só com a biblioteca padrão.

```bash
# Compara o código com o contrato. Sai 0 se igual, 1 com diff se divergir, 2 em erro de infraestrutura.
python scripts/check_openapi.py

# Depois de revisar o diff, grava o gerado como novo contrato.
python scripts/check_openapi.py --update
```

O script usa o Consolidator que estiver na 8080. Se não houver nenhum, ele sobe o Consolidator no perfil dev (H2 em memória, `BRAPI_TOKEN` fictício) e o derruba ao final. Em `prod`, o springdoc fica desligado. O `/check-contract` roda este script antes do `integration-reviewer`.
