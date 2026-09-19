# DpsLab — Guia de distribuição para Windows

## Pacote e instalação

O pacote reduzido inclui DpsLab.exe, seus arquivos internos, simc.exe, a pasta
DpsLabAddon e SIMULATIONCRAFT_NOTICE.txt. Não é necessário instalar
SimulationCraft separadamente nem informar um caminho externo para simc.exe.

1. Extraia o ZIP completo para uma pasta local com permissão de escrita.
2. Copie DpsLabAddon para World of Warcraft/_retail_/Interface/AddOns/DpsLab.
3. Feche o WoW se houver um addon antigo e substitua seu conteúdo.
4. Execute DpsLab.exe e escolha Auto, ES, EN ou PT-BR.
5. No WoW execute /dpslab export app e confirme /reload.
6. No aplicativo clique em Detectar exportação, escolha de uma a quatro builds e
   execute a simulação.
7. Salve o perfil para manter personagem, equipamento, builds e resultados.

Uma build também pode ser simulada; nesse caso não há delta relativo. Strings
externas continuam sendo simulações hipotéticas.

## Pesos e scores

Depois de uma simulação com pesos, importe-os no addon, abra /dpslab config e
escolha substituir os pesos atuais, mantê-los ou salvar uma cópia antes de
ativar os novos. Use /reload se solicitado e ative Mostrar scores de item.
Perfis compatíveis mostram scores em tooltips de equipamento, inventário e
comparação. (b) identifica a referência genérica para iniciantes. Dados ausentes
são mostrados como indisponíveis; nenhum zero é inventado.

## Idiomas, dados e privacidade

Auto usa esES/esMX para espanhol e ptBR para português brasileiro; os demais
locales usam inglês. A preferência fica em
%LOCALAPPDATA%/DpsLab/language.json. Caminhos e perfis usam arquivos separados.
Não é necessária rede para detectar exportações ou executar SimC. Exportações
podem conter nome, reino, equipamento, talentos e builds; revise-as antes de
compartilhar.

## Atualização e solução de problemas

Feche o WoW e o aplicativo antes de substituir o addon ou atualizar o pacote.
Para começar sem preferências de caminho ou idioma, remova apenas
%LOCALAPPDATA%/DpsLab/workspace_paths.json e language.json; isso não exclui os
perfis de personagem salvos. Se o
aplicativo não abrir, extraia novamente o ZIP completo e mantenha _internal.
Se a exportação não for detectada, instale a mesma versão do addon, execute
/reload e clique em Detectar exportação. Se faltar score, confirme o perfil de
pesos compatível e ative Mostrar scores de item. Builds incompletas e personagens
abaixo do nível máximo não são simulados.

O SimulationCraft é distribuído sob GPL v3. Consulte
SIMULATIONCRAFT_NOTICE.txt para o SHA-256 do binário e o repositório-fonte.
