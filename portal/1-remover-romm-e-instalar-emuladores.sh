#!/usr/bin/env bash
# Remove o RomM (e o Docker) e instala RetroArch + Pegasus.
# Rodar como root:  sudo bash 1-remover-romm-e-instalar-emuladores.sh
#
# NAO mexe em: /homelab/RomM/library (ROMs e BIOS), /homelab/Fotos, Jellyfin.
set -u

if [ "$(id -u)" -ne 0 ]; then
  echo "Rode com sudo." >&2
  exit 1
fi

LIBRETRO_DIR=/usr/lib/x86_64-linux-gnu/libretro

echo "=== 1/4 Removendo o RomM (containers, imagens e volumes do Docker) ==="
if command -v docker >/dev/null 2>&1 && [ -f /homelab/RomM/docker-compose.yml ]; then
  # -v apaga os volumes do RomM (banco, capas baixadas, cache). Os jogos nao ficam neles.
  (cd /homelab/RomM && docker compose down -v --rmi all --remove-orphans)
else
  echo "Docker ou docker-compose.yml nao encontrado, pulando."
fi

echo
echo "=== 2/4 Removendo o Docker ==="
apt-get purge -y docker-ce docker-ce-cli docker-ce-rootless-extras \
  docker-buildx-plugin docker-compose-plugin containerd.io
apt-get autoremove -y
echo "Sobras do Docker (dados de imagens antigas) ficam em /var/lib/docker e /var/lib/containerd."
echo "Se quiser liberar esse espaco: sudo rm -rf /var/lib/docker /var/lib/containerd"

echo
echo "=== 3/4 Instalando RetroArch e cores do repositorio ==="
apt-get update
apt-get install -y retroarch libretro-core-info libretro-snes9x libretro-nestopia \
  libretro-genesisplusgx libretro-mgba libretro-gambatte unzip curl

echo
echo "=== Cores que nao existem no apt (PS1 e N64), baixados do site do libretro ==="
BASE=https://buildbot.libretro.com/nightly/linux/x86_64/latest
TMP=$(mktemp -d)
for core in pcsx_rearmed mupen64plus_next; do
  if curl -fsSL -o "$TMP/$core.zip" "$BASE/${core}_libretro.so.zip"; then
    unzip -o -q "$TMP/$core.zip" -d "$LIBRETRO_DIR" && echo "ok: $core"
  else
    echo "FALHOU o download de $core (veja a internet e tente de novo)"
  fi
done
rm -rf "$TMP"

echo
echo "=== 4/4 Instalando o Pegasus (frontend) pelo Flatpak ==="
if command -v flatpak >/dev/null 2>&1; then
  flatpak install -y --system flathub org.pegasus_frontend.Pegasus
  # Permite ao Pegasus ler /homelab e chamar o RetroArch instalado no sistema.
  flatpak override --system --filesystem=/homelab --talk-name=org.freedesktop.Flatpak \
    org.pegasus_frontend.Pegasus
else
  echo "flatpak nao encontrado."
fi

echo
echo "Cores disponiveis em $LIBRETRO_DIR:"
ls "$LIBRETRO_DIR" | grep -E "snes9x|nestopia|genesis|mgba|gambatte|pcsx|mupen"
echo
echo "Pronto. Proximo passo (sem sudo, como admin): python3 /opt/portal-retro-tv/portal/2-gerar-colecoes.py"
free -h
