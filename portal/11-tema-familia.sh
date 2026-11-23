#!/bin/bash
# Cria o tema "Pegasus Familia": o Pegasus Grid (que voce gostou) com icones
# proprios nas abas Filmes e Series, Streaming e Fotos. Tambem aplica icones
# dos streamings que voce colocar em /homelab/pegasus/assets/.
# Rodar:  sudo bash /opt/portal-retro-tv/portal/11-tema-familia.sh
set -u
if [ "$(id -u)" -ne 0 ]; then
  echo "Rode com sudo: sudo bash $0"
  exit 1
fi

ORIGEM=/opt/portal-retro-tv/temas/pegasus-theme-grid
BASE=/home/portal/.var/app/org.pegasus_frontend.Pegasus/config/pegasus-frontend
TEMA=$BASE/themes/PegasusFamilia
ASSETS=/homelab/pegasus/assets
META=/homelab/pegasus/meta/metadata.pegasus.txt

[ -d "$ORIGEM" ] || { echo "Nao achei $ORIGEM"; exit 1; }

echo "=== 1/3 Copiando o tema ==="
mkdir -p "$BASE/themes"
rm -rf "$TEMA"
cp -r "$ORIGEM" "$TEMA"
rm -rf "$TEMA/.git"
sed -i 's#^name: .*#name: Pegasus Familia#' "$TEMA/theme.cfg"

echo "=== 2/3 Icones das abas (brancos, como os do tema) ==="
LOGOS=$TEMA/assets/logos

cat > "$LOGOS/filmes.svg" <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" width="567" height="113" viewBox="0 0 567 113">
  <g fill="#fff">
    <rect x="8" y="14" width="96" height="85" rx="10" fill="none" stroke="#fff" stroke-width="7"/>
    <rect x="14" y="22" width="10" height="12"/><rect x="14" y="50" width="10" height="12"/><rect x="14" y="78" width="10" height="12"/>
    <rect x="88" y="22" width="10" height="12"/><rect x="88" y="50" width="10" height="12"/><rect x="88" y="78" width="10" height="12"/>
    <polygon points="42,34 42,79 76,56"/>
    <text x="130" y="82" font-family="sans-serif" font-size="74" font-weight="bold">FILMES</text>
  </g>
</svg>
EOF

cat > "$LOGOS/streaming.svg" <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" width="567" height="113" viewBox="0 0 567 113">
  <g fill="#fff">
    <rect x="8" y="12" width="100" height="66" rx="9" fill="none" stroke="#fff" stroke-width="7"/>
    <rect x="42" y="88" width="32" height="8"/><rect x="30" y="96" width="56" height="8" rx="4"/>
    <polygon points="44,28 44,62 74,45"/>
    <text x="128" y="82" font-family="sans-serif" font-size="74" font-weight="bold">STREAMING</text>
  </g>
</svg>
EOF

cat > "$LOGOS/fotos.svg" <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" width="567" height="113" viewBox="0 0 567 113">
  <g fill="#fff">
    <rect x="8" y="14" width="104" height="85" rx="10" fill="none" stroke="#fff" stroke-width="7"/>
    <circle cx="82" cy="40" r="10"/>
    <polygon points="18,90 46,52 66,76 78,64 102,90"/>
    <text x="134" y="82" font-family="sans-serif" font-size="74" font-weight="bold">FOTOS</text>
  </g>
</svg>
EOF

chown -R portal:portal "$BASE"

echo "=== 3/3 Icones proprios dos streamings (se existirem) ==="
python3 - <<'PY'
import os
ASSETS = "/homelab/pegasus/assets"
META = "/homelab/pegasus/meta/metadata.pegasus.txt"
if not os.path.exists(META):
    raise SystemExit("metadata nao encontrado")
texto = open(META, encoding="utf-8").read()
trocas = 0
for stem in ["Jellyfin", "HBO_Max", "Netflix", "YouTube", "Disney+",
             "Prime_Video", "Globoplay", "Fotos"]:
    for ext in ("png", "jpg", "jpeg", "webp", "svg"):
        propria = f"{ASSETS}/{stem}.{ext}"
        gerado = f"{ASSETS}/{stem}.svg"
        if ext != "svg" and os.path.exists(propria) and gerado in texto:
            texto = texto.replace(gerado, propria)
            trocas += 1
            print(f"  usando seu icone: {propria}")
            break
open(META, "w", encoding="utf-8").write(texto)
print(f"{trocas} icone(s) proprio(s) aplicados")
PY
chmod -R a+rX /homelab/pegasus

sudo -u portal flatpak kill org.pegasus_frontend.Pegasus 2>/dev/null || true

echo
echo "Pronto. Abra o Pegasus, aperte Esc > Configuracoes > Tema e escolha Pegasus Familia."
