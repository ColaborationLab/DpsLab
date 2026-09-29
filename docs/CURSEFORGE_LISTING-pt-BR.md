# DpsFoundry Link — ficha de beta aberta para CurseForge

## Dados do projeto

- Nome: **DpsFoundry Link**
- Categoria proposta: **Utilities**
- Jogo: World of Warcraft Retail
- Tipo: addon
- Estado: beta aberta

## Descrição curta

DpsFoundry Link observa seu personagem localmente, exporta o perfil para o
DpsFoundry Core e mostra scores de equipamento com pesos compatíveis.

## Descrição

DpsFoundry Link acompanha o DpsFoundry Core no fluxo **analisar → decidir →
sincronizar → jogar → refinar**. Exporte seu personagem e builds do jogo para
o Core, importe os pesos calculados e consulte scores nos tooltips compatíveis.

Não é uma conexão em tempo real nem automatiza ações no jogo. Os dados são
trocados localmente entre o addon e o aplicativo. A beta suporta o fluxo já
existente do Core para classes e especializações compatíveis.

## Início rápido

1. Instale o Link em `World of Warcraft/_retail_/Interface/AddOns/DpsLab`.
2. No jogo use `/dpslab export app` e confirme `/reload`.
3. Abra o DpsFoundry Core, importe a exportação e simule as builds escolhidas.
4. Exporte os pesos selecionados do Core e importe-os no Link para ver scores.

## Feedback da beta

Informe erros ou sugestões pelo
[GitHub Issues](https://github.com/ColaborationLab/DpsLab/issues/new?title=Beta+feedback%3A+).
Não publique nomes, reinos ou exportações completas salvo se indispensáveis
para explicar o problema.

## Changelog inicial

- Primeira beta aberta do DpsFoundry Link.
- Exportação local de personagem e builds para o Core.
- Importação de pesos e scores em tooltips compatíveis.
- Seletor de perfis, interface Foundry e acesso pelo minimapa.

## Capturas necessárias antes do envio

1. Janela principal do Link com perfil ativo.
2. Janela de pesos com uma build selecionada.
3. Tooltip com score de item compatível.
4. Menu do minimapa e fluxo de exportação local.

As capturas beta atuais estão em [`curseforge-captures`](curseforge-captures/)
e serão substituídas por uma sessão atual de jogo antes de uma versão estável.
