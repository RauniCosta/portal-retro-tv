#!/usr/bin/env bash
# Desfaz o 1-otimizar-sistema.sh.  Rodar com:  sudo bash 3-reverter.sh
# Para desfazer o 2-otimizar-desktop.sh, rode como portal:
#   rm ~/.config/autostart/{blueman,org.gnome.Evolution-alarm-notify,geoclue-demo-agent,mintreport,print-applet,warpinator-autostart}.desktop
#   systemctl --user unmask evolution-addressbook-factory evolution-calendar-factory evolution-source-registry goa-daemon obex
set -u

if [ "$(id -u)" -ne 0 ]; then
  echo "Rode com sudo." >&2
  exit 1
fi

for s in ModemManager.service cups.service cups.socket cups.path cups-browsed.service \
         kerneloops.service fwupd.service power-profiles-daemon.service \
         switcheroo-control.service smbd.service nmbd.service wpa_supplicant.service; do
  if systemctl cat "$s" >/dev/null 2>&1; then
    systemctl enable --now "$s" 2>&1 | sed "s/^/[$s] /"
  fi
done
