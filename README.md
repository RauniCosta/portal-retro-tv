# 🎮📺 Portal Retro TV

Transforma um PC antigo com Linux Mint na central de entretenimento da sala: **jogos retrô, filmes, streaming e fotos da família**, tudo navegável apenas com controles USB, direto na TV.

Projeto real, rodando em um **Core 2 Duo E8500, 5,7 GB de RAM e GeForce 210** (hardware de 2008).

![Portal Retro TV na tela](docs/imagens/portal.png)

## O que o portal faz

| Guia | O que abre | Como |
|---|---|---|
| Jogos retrô (NES, SNES, Mega Drive, PS1, N64, GB/GBC/GBA) | Jogo no RetroArch | Pegasus + cores libretro |
| Filmes | Biblioteca Jellyfin e HBO Max | Jellyfin / Chrome kiosk |
| Streaming | Netflix, YouTube, Disney+, Prime Video, Globoplay | Chrome kiosk (Widevine) |
| Fotos | Biblioteca de fotos no Jellyfin | Jellyfin |

- Login automático e abertura do **Pegasus Frontend** em tela cheia.
- Dois controles USB (réplica de SNES) funcionando nos jogos.
- **Select + Start** fecha o jogo ou o navegador e volta ao portal.
- Capas, descrições e vídeos gerados por script a partir dos `gamelist.xml`.
- Painel web simples de status (porta 8088) e acesso remoto por VNC para manutenção.

## Arquitetura

```
Login automático (LightDM)
        └── Pegasus Frontend (Flatpak, tela cheia)
              ├── Jogos ──► retroarch -L <core> <rom>
              └── Apps ───► portal-abrir "<Nome>" ──► Chrome kiosk
                                                      └── portal-saida.py (Select+Start fecha)
```

## Estrutura do repositório

```
portal/      scripts numerados, na ordem de execução
otimizar/    limpeza de serviços e desktop (opcional)
painel/      painel de status em Python + HTML
fotos/       localizador de fotos duplicadas (somente leitura)
docs/        problemas e soluções, melhorias planejadas
```

## Requisitos

- Linux Mint 22 (ou Ubuntu/Debian equivalente), RetroArch, Flatpak, Google Chrome, Jellyfin.
- Suas próprias ROMs e BIOS, em `/homelab/RomM/library/roms/<sistema>/` com `gamelist.xml`. **O repositório não inclui ROMs, BIOS nem capas.**
- O tema usado é o [pegasus-theme-grid](https://github.com/mmatyas/pegasus-theme-grid), clonado em `/opt/portal-retro-tv/temas/pegasus-theme-grid` (respeite a licença dele).

## Instalação

Os scripts assumem o repositório em `/opt/portal-retro-tv` e o usuário do portal chamado `portal` (autologin). Ajuste os nomes no topo de cada script se usar outros.

```bash
sudo git clone https://github.com/RauniCosta/portal-retro-tv /opt/portal-retro-tv
cd /opt/portal-retro-tv/portal
sudo bash 1-remover-romm-e-instalar-emuladores.sh   # emuladores (RetroArch + cores)
python3 2-gerar-colecoes.py                         # coleções iniciais
sudo bash 3-acesso-remoto.sh                        # VNC (opcional)
sudo bash 4-finalizar-portal.sh                     # Pegasus, autostart, portal-abrir
sudo bash 5-adicionar-hbomax.sh
sudo bash 6-ajustar-retroarch.sh                    # tela cheia e pasta de BIOS
sudo bash 7-copiar-controle-p2.sh                   # controle 2 igual ao controle 1
sudo bash 8-atalho-sair-retroarch.sh                # Select+Start sai do jogo
sudo python3 9-capas-e-guias.py                     # capas, filmes, streaming, fotos
sudo bash 11-tema-familia.sh                        # tema com ícones das guias
```

Depois reinicie o PC. O script `10-instalar-tema` (gameOS) foi descartado por não ter ficado bonito, por isso não está incluído.

## Limitações conhecidas

- A GeForce 210 só decodifica **H.264** em hardware.
- HBO Max e Netflix ficam em **720p** nos navegadores Linux, o que na TV da sala é suficiente.
- Firefox deu erro de DRM nos streamings; por isso o Chrome com Widevine.
- PS1 e N64 dependem de BIOS e podem ter lentidão no E8500.

## Autor

**Rauni Sérgio Costa**: infraestrutura, docência técnica e desenvolvimento com IA.
[Portfólio](https://rauni-portfolio.web.app/) · [LinkedIn](https://www.linkedin.com/in/rauni-sergio-costa) · [GitHub](https://github.com/RauniCosta)

## Licença

[MIT](LICENSE)
