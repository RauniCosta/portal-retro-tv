# Melhorias planejadas

## Imagens
- As capas originais têm cerca de 640 px e ~500 KB cada. O tema as mostra em 256×256.
- Gerar uma pasta de capas otimizadas (300×400, JPEG) sem alterar as originais: de ~200 MB para ~15 MB.
- Uniformizar a proporção (as capas variam entre retrato, paisagem e quadrado).
- Redimensionar os banners SVG de Filmes, Streaming e Fotos para o mesmo formato.
- Reduzir os screenshots de PS1 e N64 (640×480, até 330 KB).

## Cores e visual
- Cor ou degradê por coleção (NES/SNES, Mega Drive, PS1, Streaming, Fotos).
- Destaque colorido no item selecionado, para ler de longe na TV.
- Fundo próprio por coleção.

## Guias
- Remover a guia vazia de Game Boy e unir GBC e GBA em "Game Boy".
- Reordenar: Filmes, Streaming, Jogos, Fotos.
- Criar a biblioteca de fotos no Jellyfin e tratar duplicadas (`fotos/achar-duplicadas.py`, somente leitura).
- Coleções por gênero e número de jogadores.

## Testes pendentes
- BIOS do PS1 e desempenho de PS1 e N64 no E8500.
