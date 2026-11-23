#!/bin/bash
# Define Select+Start no controle para FECHAR o jogo no RetroArch (volta ao Pegasus).
# Usa os mesmos botoes de Select e Start que ja estao mapeados no controle 1.
# Rodar:  sudo bash /opt/portal-retro-tv/portal/8-atalho-sair-retroarch.sh
set -u
if [ "$(id -u)" -ne 0 ]; then
  echo "Rode com sudo: sudo bash $0"
  exit 1
fi

CFG=/home/portal/.config/retroarch/retroarch.cfg
[ -f "$CFG" ] || { echo "Nao achei $CFG"; exit 1; }

SEL=$(grep -E '^input_player1_select_btn = ' "$CFG" | sed 's/.*= "\(.*\)"/\1/')
STA=$(grep -E '^input_player1_start_btn = ' "$CFG" | sed 's/.*= "\(.*\)"/\1/')
echo "Select do controle 1 = '${SEL}'   Start do controle 1 = '${STA}'"
if [ -z "$SEL" ] || [ -z "$STA" ] || [ "$SEL" = "nul" ] || [ "$STA" = "nul" ]; then
  echo "Select/Start do controle 1 nao estao mapeados. Mapeie no RetroArch e rode de novo."
  exit 1
fi

cp "$CFG" "$CFG.bak-saida"

set_cfg() {
  if grep -q "^$1 = " "$CFG"; then
    sed -i "s#^$1 = .*#$1 = \"$2\"#" "$CFG"
  else
    echo "$1 = \"$2\"" >> "$CFG"
  fi
}

# Select = botao de atalho; Start (com Select segurado) = fechar o RetroArch
set_cfg input_enable_hotkey_btn "$SEL"
set_cfg input_exit_emulator_btn "$STA"
# Mesmo atalho para o controle 2 (os dois adaptadores sao identicos)
set_cfg quit_press_twice false

chown portal:portal "$CFG" "$CFG.bak-saida"

echo
echo "Conferindo:"
grep -n -E "^(input_enable_hotkey_btn|input_exit_emulator_btn|quit_press_twice) " "$CFG"
echo
echo "Pronto. Abra um jogo e segure Select, depois aperte Start."
