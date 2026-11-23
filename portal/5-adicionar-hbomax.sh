#!/bin/bash
# Adiciona o HBO Max na colecao "Filmes e Series" do Pegasus.
# Rodar:  sudo bash /opt/portal-retro-tv/portal/5-adicionar-hbomax.sh
set -u
if [ "$(id -u)" -ne 0 ]; then
  echo "Rode com sudo: sudo bash $0"
  exit 1
fi

ABRIDOR=/usr/local/bin/portal-abrir
PASTA="/homelab/pegasus/apps/filmes"

# 1) Ensina o abridor a abrir o HBO Max (se ainda nao souber)
if ! grep -q '"HBO Max")' "$ABRIDOR"; then
  sed -i 's#^  Globoplay)#  "HBO Max")     URL="https://www.hbomax.com" ;;\n  Globoplay)#' "$ABRIDOR"
fi

# 2) Cria o item na colecao Filmes e Series
touch "$PASTA/HBO Max.app"
chmod -R a+rX /homelab/pegasus

echo "Conferindo:"
grep -n "HBO Max" "$ABRIDOR"
ls -l "$PASTA"
echo
echo "Pronto. Feche e abra o Pegasus (ou reinicie) para o item aparecer."
