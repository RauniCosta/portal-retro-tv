#!/bin/bash
# Ajusta o RetroArch do usuario portal: tela cheia e pasta de BIOS.
# Rodar:  sudo bash /opt/portal-retro-tv/portal/6-ajustar-retroarch.sh
set -u
if [ "$(id -u)" -ne 0 ]; then
  echo "Rode com sudo: sudo bash $0"
  exit 1
fi

CFG=/home/portal/.config/retroarch/retroarch.cfg
if [ ! -f "$CFG" ]; then
  echo "Nao achei $CFG. Abra um jogo uma vez pelo Pegasus e feche, depois rode de novo."
  exit 1
fi

cp "$CFG" "$CFG.bak-portal"

# define chave = "valor" (troca se existir, senao acrescenta)
set_cfg() {
  local chave="$1" valor="$2"
  if grep -q "^$chave = " "$CFG"; then
    sed -i "s#^$chave = .*#$chave = \"$valor\"#" "$CFG"
  else
    echo "$chave = \"$valor\"" >> "$CFG"
  fi
}

set_cfg video_fullscreen true
set_cfg video_windowed_fullscreen true     # tela cheia sem borda, troca de janela rapida
set_cfg system_directory /homelab/RomM/library/roms/bios
set_cfg input_autodetect_enable true
set_cfg config_save_on_exit true

chown portal:portal "$CFG" "$CFG.bak-portal"

echo "Conferindo:"
grep -n -E "^(video_fullscreen|video_windowed_fullscreen|system_directory|input_autodetect_enable|input_joypad_driver) " "$CFG"
echo
echo "Pronto. Backup em $CFG.bak-portal"
