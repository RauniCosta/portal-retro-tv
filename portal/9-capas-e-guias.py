#!/usr/bin/env python3
"""Monta o visual do portal no Pegasus:
  - jogos com capa, logo, print, video, descricao, genero e nota (vindos dos
    gamelist.xml que ja existem nas pastas de ROMs);
  - guias Filmes e Series, Streaming e Fotos com banners coloridos.

Rodar:  sudo python3 /opt/portal-retro-tv/portal/9-capas-e-guias.py
"""
import html
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROMS = Path("/homelab/RomM/library/roms")
DEST = Path("/homelab/pegasus")
CORES = "/usr/lib/x86_64-linux-gnu/libretro"

# nome da guia, pasta, extensoes, core
SISTEMAS = [
    ("Nintendo 8 bits (NES)", "nes", "nes, zip", "nestopia_libretro.so"),
    ("Super Nintendo", "snes", "smc, sfc, zip", "snes9x_libretro.so"),
    ("Mega Drive", "megadrive", "md, gen, bin, zip", "genesis_plus_gx_libretro.so"),
    ("Game Boy", "gb", "gb, zip", "gambatte_libretro.so"),
    ("Game Boy Color", "gbc", "gbc, zip", "gambatte_libretro.so"),
    ("Game Boy Advance", "gba", "gba, zip", "mgba_libretro.so"),
    ("PlayStation", "psx", "chd, cue, pbp", "pcsx_rearmed_libretro.so"),
    ("Nintendo 64", "n64", "z64, n64, v64", "mupen64plus_next_libretro.so"),
]

# apps: (arquivo, nome na tela, cor1, cor2, subtitulo)
FILMES = [
    ("Jellyfin", "Meus Filmes", "#5b3fd1", "#00a4dc", "Biblioteca da familia"),
    ("HBO Max", "HBO Max", "#2a1b6e", "#8a3ffc", "Series e filmes"),
]
STREAMING = [
    ("Netflix", "Netflix", "#7a0b12", "#e50914", "Series e filmes"),
    ("YouTube", "YouTube", "#8a0f0f", "#ff3d3d", "Videos e desenhos"),
    ("Disney+", "Disney+", "#0b2a6b", "#2f6df6", "Desenhos e filmes"),
    ("Prime Video", "Prime Video", "#0a4a66", "#1fb4e6", "Series e filmes"),
    ("Globoplay", "Globoplay", "#a1280b", "#ff7a2f", "Novelas e programas"),
]
FOTOS = [
    ("Fotos", "Fotos da Familia", "#0f6b4f", "#5fd39a", "Nossas lembrancas"),
]


def limpar(texto):
    return re.sub(r"\s+", " ", (texto or "")).strip()


def data_pegasus(valor):
    m = re.match(r"(\d{4})(\d{2})(\d{2})", valor or "")
    if not m:
        return ""
    ano, mes, dia = m.groups()
    if ano == "0000":
        return ""
    return f"{ano}-{mes if mes != '00' else '01'}-{dia if dia != '00' else '01'}"


def caminho(pasta, relativo):
    if not relativo:
        return None
    p = (pasta / relativo).resolve()
    return str(p) if p.exists() else None


def blocos_jogos(pasta):
    gl = pasta / "gamelist.xml"
    if not gl.exists():
        return [], 0
    try:
        raiz = ET.parse(gl).getroot()
    except ET.ParseError as e:
        print(f"  aviso: {gl} invalido ({e})")
        return [], 0
    saidas = []
    for jogo in raiz.findall("game"):
        arq = (jogo.findtext("path") or "").strip()
        arq = arq[2:] if arq.startswith("./") else arq
        if not arq or not (pasta / arq).exists():
            continue
        nome = limpar(jogo.findtext("name")) or Path(arq).stem
        linhas = [f"game: {nome}", f"file: {pasta / arq}"]
        desc = limpar(jogo.findtext("desc"))
        if desc:
            linhas.append(f"description: {desc}")
        for chave, tag in (("developer", "developer"), ("publisher", "publisher"),
                           ("genre", "genre")):
            v = limpar(jogo.findtext(tag))
            if v:
                linhas.append(f"{chave}: {v}")
        jog = limpar(jogo.findtext("players"))
        if jog:
            linhas.append(f"players: {jog}")
        data = data_pegasus(jogo.findtext("releasedate"))
        if data:
            linhas.append(f"release: {data}")
        try:
            nota = float(jogo.findtext("rating") or 0)
            if nota > 0:
                linhas.append(f"rating: {round(nota * 100)}%")
        except ValueError:
            pass
        capa = caminho(pasta, jogo.findtext("thumbnail")) or caminho(pasta, jogo.findtext("image"))
        if capa:
            linhas.append(f"assets.boxFront: {capa}")
        logo = caminho(pasta, jogo.findtext("marquee"))
        if logo:
            linhas.append(f"assets.logo: {logo}")
        print_ = caminho(pasta, jogo.findtext("image"))
        if print_:
            linhas.append(f"assets.screenshot: {print_}")
        video = caminho(pasta, jogo.findtext("video"))
        if video:
            linhas.append(f"assets.video: {video}")
        saidas.append("\n".join(linhas))
    return saidas, len(saidas)


def banner_svg(titulo, sub, cor1, cor2):
    t, s = html.escape(titulo), html.escape(sub)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="800" viewBox="0 0 600 800">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{cor1}"/>
      <stop offset="1" stop-color="{cor2}"/>
    </linearGradient>
  </defs>
  <rect width="600" height="800" rx="48" fill="url(#g)"/>
  <circle cx="480" cy="140" r="170" fill="#ffffff" fill-opacity="0.10"/>
  <circle cx="90" cy="700" r="210" fill="#ffffff" fill-opacity="0.08"/>
  <polygon points="250,300 250,500 420,400" fill="#ffffff" fill-opacity="0.92"/>
  <text x="300" y="610" font-family="sans-serif" font-size="58" font-weight="bold"
        fill="#ffffff" text-anchor="middle">{t}</text>
  <text x="300" y="670" font-family="sans-serif" font-size="30"
        fill="#ffffff" fill-opacity="0.85" text-anchor="middle">{s}</text>
</svg>
"""


def colecao_apps(nome, curto, pasta_app, itens):
    pasta = DEST / "apps" / pasta_app
    pasta.mkdir(parents=True, exist_ok=True)
    (DEST / "assets").mkdir(parents=True, exist_ok=True)
    partes = [
        f"collection: {nome}\nshortname: {curto}\ndirectory: {pasta}\n"
        f"extensions: app\n"
        f'launch: /usr/local/bin/portal-abrir "{{file.basename}}"'
    ]
    for arquivo, titulo, c1, c2, sub in itens:
        (pasta / f"{arquivo}.app").touch()
        svg = DEST / "assets" / f"{arquivo.replace(' ', '_')}.svg"
        svg.write_text(banner_svg(titulo, sub, c1, c2), encoding="utf-8")
        partes.append(
            f"game: {titulo}\nfile: {pasta}/{arquivo}.app\ndescription: {sub}\n"
            f"assets.boxFront: {svg}\nassets.logo: {svg}\n"
            f'launch: /usr/local/bin/portal-abrir "{arquivo}"'
        )
    return "\n\n".join(partes)


def garantir_fotos_no_abridor():
    abridor = Path("/usr/local/bin/portal-abrir")
    if not abridor.exists():
        print("aviso: /usr/local/bin/portal-abrir nao existe")
        return
    texto = abridor.read_text(encoding="utf-8")
    if "Fotos)" in texto:
        return
    novo = texto.replace(
        '  Netflix)',
        '  Fotos)         URL="http://localhost:8096" ;;\n  Netflix)', 1)
    if novo != texto:
        abridor.write_text(novo, encoding="utf-8")
        print("portal-abrir: guia Fotos adicionada (abre o Jellyfin)")


def main():
    if os.geteuid() != 0:
        print("Rode com sudo: sudo python3", sys.argv[0])
        sys.exit(1)
    DEST.mkdir(parents=True, exist_ok=True)
    antigo = DEST / "metadata.pegasus.txt"
    if antigo.exists():
        shutil.move(str(antigo), str(DEST / "metadata.pegasus.txt.antigo"))
    (DEST / "meta").mkdir(exist_ok=True)
    meta = DEST / "meta" / "metadata.pegasus.txt"

    partes = []
    for nome, pasta, exts, core in SISTEMAS:
        diretorio = ROMS / pasta
        if not diretorio.is_dir():
            continue
        cab = (
            f"collection: {nome}\nshortname: {pasta}\ndirectory: {diretorio}\n"
            f"extensions: {exts}\n"
            f'launch: retroarch -L "{CORES}/{core}" "{{file.path}}"'
        )
        jogos, qtd = blocos_jogos(diretorio)
        print(f"{nome}: {qtd} jogos com capa/descricao")
        partes.append(cab + ("\n\n" + "\n\n".join(jogos) if jogos else ""))

    partes.append(colecao_apps("Filmes e Series", "filmes", "filmes", FILMES))
    partes.append(colecao_apps("Streaming", "streaming", "streaming", STREAMING))
    partes.append(colecao_apps("Fotos", "fotos", "fotos", FOTOS))

    meta.write_text("\n\n".join(partes) + "\n", encoding="utf-8")
    garantir_fotos_no_abridor()
    gd = Path("/home/portal/.var/app/org.pegasus_frontend.Pegasus/config/pegasus-frontend/game_dirs.txt")
    gd.parent.mkdir(parents=True, exist_ok=True)
    gd.write_text(str(DEST / "meta") + "\n", encoding="utf-8")
    os.system(f"chown -R portal:portal {gd.parent.parent}")
    os.system(f"chmod -R a+rX {DEST}")
    print(f"\nGravado: {meta}")
    print("Feche e abra o Pegasus para carregar.")


if __name__ == "__main__":
    main()
