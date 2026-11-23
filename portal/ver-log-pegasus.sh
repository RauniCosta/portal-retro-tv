#!/bin/bash
# Copia o log do Pegasus e a lista do tema para /tmp, onde o Claude consegue ler.
# Rodar:  sudo bash /opt/portal-retro-tv/portal/ver-log-pegasus.sh
BASE=/home/portal/.var/app/org.pegasus_frontend.Pegasus/config/pegasus-frontend
cp "$BASE/lastrun.log" /tmp/pegasus-lastrun.log
{
  echo "--- settings.txt"
  cat "$BASE/settings.txt"
  echo "--- temas instalados"
  ls -la "$BASE/themes"
  echo "--- logos novos"
  ls -la "$BASE/themes/PegasusFamilia/assets/logos/filmes.svg" \
         "$BASE/themes/PegasusFamilia/assets/logos/streaming.svg" \
         "$BASE/themes/PegasusFamilia/assets/logos/fotos.svg"
  echo "--- theme.cfg"
  cat "$BASE/themes/PegasusFamilia/theme.cfg"
} > /tmp/pegasus-tema-info.txt 2>&1
chmod 644 /tmp/pegasus-lastrun.log /tmp/pegasus-tema-info.txt
echo "Pronto. Pode me avisar."
