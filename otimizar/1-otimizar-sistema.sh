#!/usr/bin/env bash
# Desliga servicos de sistema desnecessarios no PC-PORTAL.
# Rodar como root:  sudo bash 1-otimizar-sistema.sh
# Para desfazer:    sudo bash 3-reverter.sh
set -u

if [ "$(id -u)" -ne 0 ]; then
  echo "Rode com sudo." >&2
  exit 1
fi

# Servicos e motivos:
#  ModemManager             - gerencia modems 3G/4G, nao ha modem
#  cups / cups-browsed      - impressao e descoberta de impressoras
#  kerneloops               - envia relatorios de falhas do kernel
#  fwupd                    - atualizacao de firmware (pode ser ligado so quando precisar)
#  power-profiles-daemon    - perfis de energia de notebook
#  switcheroo-control       - alterna GPU em notebooks com placa hibrida
#  smbd / nmbd              - compartilhamento Samba (nao usado)
#  wpa_supplicant           - Wi-Fi (a maquina so usa cabo: enp0s25)
SERVICOS="
ModemManager.service
cups.service
cups.socket
cups.path
cups-browsed.service
kerneloops.service
fwupd.service
power-profiles-daemon.service
switcheroo-control.service
smbd.service
nmbd.service
wpa_supplicant.service
"

for s in $SERVICOS; do
  if systemctl cat "$s" >/dev/null 2>&1; then
    systemctl disable --now "$s" 2>&1 | sed "s/^/[$s] /"
  else
    echo "[$s] nao existe, pulando"
  fi
done

echo
echo "Pronto. Memoria agora:"
free -h
