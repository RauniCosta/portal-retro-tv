#!/bin/bash
# Copia o mapeamento do controle 1 (que funciona) para o controle 2 no RetroArch.
# Rodar:  sudo bash /opt/portal-retro-tv/portal/7-copiar-controle-p2.sh
set -u
if [ "$(id -u)" -ne 0 ]; then
  echo "Rode com sudo: sudo bash $0"
  exit 1
fi

DIR=/home/portal/.config/retroarch
CFG=$DIR/retroarch.cfg
[ -f "$CFG" ] || { echo "Nao achei $CFG"; exit 1; }

cp "$CFG" "$CFG.bak-p2"

echo "--- Perfis de controle salvos (autoconfig):"
ls -l "$DIR/autoconfig" 2>/dev/null || echo "(nenhum)"
echo
echo "--- Mapeamento atual do controle 1 (botoes/eixos):"
grep -E "^input_player1_[a-z0-9_]+_(btn|axis|mbtn) = " "$CFG"
echo
echo "--- Indices de controle atuais:"
grep -E "^input_player[12]_joypad_index" "$CFG"
echo

# define chave = "valor" (troca se existir, senao acrescenta)
set_cfg() {
  if grep -q "^$1 = " "$CFG"; then
    sed -i "s#^$1 = .*#$1 = \"$2\"#" "$CFG"
  else
    echo "$1 = \"$2\"" >> "$CFG"
  fi
}

# Copia cada bind de joypad do jogador 1 para o jogador 2
grep -E "^input_player1_[a-z0-9_]+_(btn|axis|mbtn) = " "$CFG" | while IFS= read -r linha; do
  chave="${linha%% = *}"
  valor="${linha#* = }"
  valor="${valor//\"/}"
  nova="${chave/input_player1_/input_player2_}"
  set_cfg "$nova" "$valor"
done

set_cfg input_player1_joypad_index 0
set_cfg input_player2_joypad_index 1

chown portal:portal "$CFG" "$CFG.bak-p2"

echo "--- Resultado do controle 2:"
grep -E "^input_player2_[a-z0-9_]+_(btn|axis|mbtn) = |^input_player[12]_joypad_index" "$CFG"
echo
echo "Pronto. Backup em $CFG.bak-p2. Abra um jogo de 2 jogadores e teste o controle 2."
