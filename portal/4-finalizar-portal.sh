#!/bin/bash
# Finaliza o portal da TV: coleções Pegasus (jogos + filmes/streaming),
# abertura automática em tela cheia e sem proteção de tela.
# Rodar no PuTTY:  sudo bash /opt/portal-retro-tv/portal/4-finalizar-portal.sh
set -u

if [ "$(id -u)" -ne 0 ]; then
  echo "Rode com sudo: sudo bash $0"
  exit 1
fi

USUARIO=portal
UID_U=$(id -u "$USUARIO")
HOME_U=/home/$USUARIO
ORIGEM=/opt/portal-retro-tv/portal/pegasus/metadata.pegasus.txt
DESTINO=/homelab/pegasus
CONF=$HOME_U/.var/app/org.pegasus_frontend.Pegasus/config/pegasus-frontend

echo "=== 1/5 Abridor de streaming (/usr/local/bin/portal-abrir) ==="
cat > /usr/local/bin/portal-abrir <<'EOF'
#!/bin/bash
# Abre um servico no Firefox em tela cheia. Uso: portal-abrir "Nome"
# Para adicionar servicos: inclua uma linha abaixo e um arquivo vazio
# em /homelab/pegasus/apps/streaming/ com o mesmo nome (ex.: Netflix.app).
export DISPLAY="${DISPLAY:-:0}"
case "$1" in
  Jellyfin)      URL="http://localhost:8096" ;;
  Netflix)       URL="https://www.netflix.com" ;;
  YouTube)       URL="https://www.youtube.com" ;;
  "Disney+")     URL="https://www.disneyplus.com" ;;
  "Prime Video") URL="https://www.primevideo.com" ;;
  Globoplay)     URL="https://globoplay.globo.com" ;;
  *)             URL="$1" ;;
esac
exec firefox --kiosk "$URL"
EOF
chmod 755 /usr/local/bin/portal-abrir

echo "=== 2/5 Colecoes do Pegasus em $DESTINO ==="
mkdir -p "$DESTINO/apps/filmes" "$DESTINO/apps/streaming"
cp "$ORIGEM" "$DESTINO/metadata.pegasus.txt"
touch "$DESTINO/apps/filmes/Jellyfin.app"
for s in Netflix YouTube "Disney+" "Prime Video" Globoplay; do
  touch "$DESTINO/apps/streaming/$s.app"
done
cat >> "$DESTINO/metadata.pegasus.txt" <<'EOF'

collection: Filmes e Series
shortname: filmes
directory: /homelab/pegasus/apps/filmes
extensions: app
launch: /usr/local/bin/portal-abrir "{file.basename}"

collection: Streaming
shortname: streaming
directory: /homelab/pegasus/apps/streaming
extensions: app
launch: /usr/local/bin/portal-abrir "{file.basename}"
EOF
chmod -R a+rX "$DESTINO"

echo "=== 3/5 Pegasus: pasta de jogos e tela cheia ==="
sudo -u "$USUARIO" mkdir -p "$CONF"
echo "$DESTINO" | sudo -u "$USUARIO" tee "$CONF/game_dirs.txt" >/dev/null
if [ -f "$CONF/settings.txt" ]; then
  if grep -q "^general.fullscreen" "$CONF/settings.txt"; then
    sed -i 's/^general.fullscreen.*/general.fullscreen: true/' "$CONF/settings.txt"
  else
    echo "general.fullscreen: true" >> "$CONF/settings.txt"
  fi
else
  echo "general.fullscreen: true" | sudo -u "$USUARIO" tee "$CONF/settings.txt" >/dev/null
fi

echo "=== 4/5 Abrir o Pegasus sozinho ao ligar ==="
sudo -u "$USUARIO" mkdir -p "$HOME_U/.config/autostart"
cat > "$HOME_U/.config/autostart/pegasus.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=Portal (Pegasus)
Exec=flatpak run org.pegasus_frontend.Pegasus
X-GNOME-Autostart-enabled=true
EOF
chown "$USUARIO":"$USUARIO" "$HOME_U/.config/autostart/pegasus.desktop"

echo "=== 5/5 Sem protecao de tela nem desligar o monitor ==="
GS="sudo -u $USUARIO env DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/$UID_U DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_U/bus gsettings set"
$GS org.mate.screensaver idle-activation-enabled false || true
$GS org.mate.screensaver lock-enabled false || true
$GS org.mate.power-manager sleep-display-ac 0 || true
$GS org.mate.power-manager sleep-computer-ac 0 || true

echo
echo "Pronto. Conferindo:"
ls -l "$DESTINO" "$CONF"
echo
echo "Agora reinicie:  sudo reboot"
