# Problemas encontrados e soluções

Registro do que deu errado durante a montagem do portal e como foi resolvido.

| Problema | Causa | Solução |
|---|---|---|
| VNC fechava ao conectar | `-allow` do x11vnc não aceita CIDR (`192.168.0.0/24`) | Usar prefixo: `-allow 192.168.0.,127.0.0.1` e `-logappend` para depurar |
| Pegasus: "no games found" | Pasta do usuário ilegível e `game_dirs.txt` no usuário errado | Metadata em `/homelab/pegasus/meta` e `game_dirs.txt` no usuário do portal |
| Jogos não abriam (erro código 1) | `flatpak-spawn --host` duplicado: o Pegasus Flatpak já o acrescenta | Remover o prefixo da linha `launch:` |
| Centenas de "Game file doesn't exist" | `file:` é relativo ao metafile | Usar caminhos absolutos |
| App de streaming abria o comando do NES | `launch:` da coleção sobrescrevia | Colocar `launch:` por item e isolar a pasta `meta` |
| Erro de DRM no Firefox | Sem Widevine funcional | Chrome em modo kiosk com perfil dedicado |
| Controle 2 não funcionava no RetroArch | Binds só do jogador 1 | Copiar os binds do jogador 1 para o jogador 2 (`7-copiar-controle-p2.sh`) |
| Janela pequena no RetroArch | Fullscreen desligado | `video_fullscreen` e `windowed_fullscreen` ligados (`6-ajustar-retroarch.sh`) |
| Pegasus aberto por `sudo -u` sem áudio | Faltava sessão D-Bus | Só afeta testes; o autostart real funciona |
| Ícones das guias sumiam | Tema não conhece o `shortname` | Tema derivado com logos SVG por coleção (`11-tema-familia.sh`) |

## Lições

1. Leia o log antes de mudar configuração (`lastrun.log` do Pegasus resolveu vários casos).
2. Em Flatpak, confira o que o próprio empacotamento já acrescenta.
3. Mantenha scripts curtos e numerados: reproduzir o ambiente do zero fica trivial.
