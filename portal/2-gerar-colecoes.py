#!/usr/bin/env python3
"""Gera o arquivo de colecoes do Pegasus a partir da biblioteca de ROMs.

Nao altera nada dentro de /homelab: escreve so em /opt/portal-retro-tv/portal/pegasus.
Rodar como o usuario que vai usar o Pegasus:  python3 2-gerar-colecoes.py
"""
import os
from pathlib import Path

ROMS = Path("/homelab/RomM/library/roms")
SAIDA = Path(__file__).resolve().parent / "pegasus"
CORES = Path("/usr/lib/x86_64-linux-gnu/libretro")

# (nome exibido, pasta, core, extensoes)
SISTEMAS = [
    ("Nintendo 8 bits (NES)", "nes", "nestopia_libretro.so", "nes, zip"),
    ("Super Nintendo", "snes", "snes9x_libretro.so", "smc, sfc, zip"),
    ("Mega Drive", "megadrive", "genesis_plus_gx_libretro.so", "md, gen, bin, zip"),
    ("Game Boy", "gb", "gambatte_libretro.so", "gb, zip"),
    ("Game Boy Color", "gbc", "gambatte_libretro.so", "gbc, zip"),
    ("Game Boy Advance", "gba", "mgba_libretro.so", "gba, zip"),
    ("PlayStation", "psx", "pcsx_rearmed_libretro.so", "chd, cue, pbp"),
    ("Nintendo 64", "n64", "mupen64plus_next_libretro.so", "z64, n64, v64"),
]


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    linhas = []
    for nome, pasta, core, exts in SISTEMAS:
        diretorio = ROMS / pasta
        if not diretorio.is_dir():
            print(f"pulando {nome}: pasta {diretorio} nao existe")
            continue
        if not (CORES / core).exists():
            print(f"AVISO {nome}: core {core} nao encontrado em {CORES}")
        linhas += [
            f"collection: {nome}",
            f"shortname: {pasta}",
            f"directory: {diretorio}",
            f"extensions: {exts}",
            f'launch: retroarch -L "{CORES / core}" "{{file.path}}"',
            "",
        ]
        print(f"ok: {nome}")

    arquivo = SAIDA / "metadata.pegasus.txt"
    arquivo.write_text("\n".join(linhas), encoding="utf-8")
    print(f"\nEscrito: {arquivo}")

    # Diz ao Pegasus onde procurar. Escreve nos dois locais possiveis (Flatpak e nativo).
    home = Path.home()
    for conf in (
        home / ".var/app/org.pegasus_frontend.Pegasus/config/pegasus-frontend",
        home / ".config/pegasus-frontend",
    ):
        conf.mkdir(parents=True, exist_ok=True)
        (conf / "game_dirs.txt").write_text(str(SAIDA) + "\n", encoding="utf-8")
        print(f"game_dirs.txt atualizado em {conf}")


if __name__ == "__main__":
    main()
