# Swagger + OpenAPI: a API do MyWallet ganhou um manual

- **Spec:** `specs/001-swagger-openapi.md`
- **Serviços:** Consolidator, hub
- **Data:** 2026-11-19 (feature concluída em 2026-11-18)

## Problema
As três partes do MyWallet (o servidor que consolida a carteira, a tela e o coletor de dados) trocam informações o tempo todo. Ninguém tinha escrito como essa conversa funciona. A única referência era o próprio código, e algumas regras tinham mudado sem registro. Num app que mostra lucro, prejuízo e preço justo, um campo mal entendido vira um número errado na tela.

## Solução
O servidor agora tem uma página navegável que lista cada operação, o que ela recebe e o que devolve. Em ambiente de desenvolvimento dá para testar as chamadas por ela. Essa descrição também foi salva como um contrato oficial no repositório central. Um script compara o servidor com esse contrato e avisa quando os dois deixam de bater.

## Benefício
- Antes de qualquer mudança na API, fica claro o que muda para a tela e para o coletor.
- O contrato também registra as regras de leitura dos números: percentuais vão de 0 a 100, a volatilidade é uma fração de 0 a 1, os valores estão em reais e preço ausente significa "sem dado", nunca zero.
- O contrato tem uma lista de problemas conhecidos, e cada problema aponta para a spec que vai corrigi-lo. Um exemplo é o preço do ativo gravado no cadastro e nunca atualizado.
- Nada mudou no comportamento do app: esta etapa só documentou o que já existia.

## Aprendizado
- **Documentar antes de corrigir.** Escrever o contrato do jeito que a API é hoje, com os defeitos, deu uma linha de base. Cada correção futura agora aparece como uma diferença explícita no contrato.
- **Gerar o contrato a partir do código.** As descrições ficam em anotações no código e o arquivo do contrato nunca é editado à mão, então os dois não se afastam.
- **Testar no servidor de verdade.** A verificação no servidor rodando mostrou respostas diferentes das que os testes automatizados indicavam. Vale conferir as duas coisas.

## Vale post
Sim. "Documentar a API como ela é, defeitos incluídos" é uma ideia simples e pouco comum, e combina com a série sobre organizar um projeto pessoal com agentes.

## Material
- Print da página do Swagger com a lista de grupos (carteiras, ativos, transações, proventos), sem dados de carteira.
- Trecho do contrato com a descrição de um campo que tem a unidade e o significado de null.
- Print do script de verificação no terminal, com "contrato igual ao código".

## Pendências
- Alguns endereços que deveriam dizer "não encontrado" respondem com outro código no servidor real. A correção está na spec 002.
- O contrato ainda não marca quais campos podem vir vazios. Isso entra na spec 006.
- As divergências da tela e do coletor em relação ao contrato estão listadas como problemas conhecidos e serão tratadas nas specs 004 e 005.
