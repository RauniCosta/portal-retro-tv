#!/usr/bin/env bash
# Tira da sessao MATE itens que consomem memoria e nao sao usados.
# Rodar como o usuario do desktop (portal), SEM sudo:  bash 2-otimizar-desktop.sh
# Vale na proxima vez que a sessao for iniciada (faca logout/login ou reinicie).
set -u

if [ "$(id -u)" -eq 0 ]; then
  echo "Rode como o usuario do desktop, sem sudo." >&2
  exit 1
fi

AUTOSTART="$HOME/.config/autostart"
mkdir -p "$AUTOSTART"

# Itens iniciados com a sessao: Bluetooth (blueman), alarmes do Evolution,
# agente de localizacao (geoclue) e bandeja de relatorios do Mint.
for nome in blueman org.gnome.Evolution-alarm-notify geoclue-demo-agent mintreport print-applet warpinator-autostart; do
  origem="/etc/xdg/autostart/$nome.desktop"
  if [ -f "$origem" ]; then
    cp "$origem" "$AUTOSTART/$nome.desktop"
    if grep -q '^Hidden=' "$AUTOSTART/$nome.desktop"; then
      sed -i 's/^Hidden=.*/Hidden=true/' "$AUTOSTART/$nome.desktop"
    else
      echo 'Hidden=true' >> "$AUTOSTART/$nome.desktop"
    fi
    echo "autostart desativado: $nome"
  else
    echo "nao encontrado em /etc/xdg/autostart: $nome (pulando)"
  fi
done

# Servicos de calendario, contatos e contas online, ativados sob demanda.
# O mask impede que sejam iniciados de novo.
for u in evolution-addressbook-factory.service evolution-calendar-factory.service \
         evolution-source-registry.service goa-daemon.service obex.service; do
  systemctl --user mask "$u" 2>&1 | sed "s/^/[$u] /"
done

echo
echo "Feito. Faca logout e login na sessao para valer."
