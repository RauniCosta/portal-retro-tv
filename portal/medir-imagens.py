#!/usr/bin/env python3
"""Mede as imagens das coleções (largura, altura, peso) para a revisão do visual."""
import glob
import os
import struct
from collections import Counter

RAIZ = "/homelab/RomM/library/roms"


def dim_png(caminho):
    with open(caminho, "rb") as f:
        cab = f.read(24)
    if cab[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", cab[16:24])
    return None


for sistema in ["nes", "snes", "megadrive", "gb", "gbc", "gba", "psx", "n64"]:
    pasta = f"{RAIZ}/{sistema}/images"
    if not os.path.isdir(pasta):
        print(f"{sistema}: sem pasta images")
        continue
    por_tipo = {"thumb": [], "image": [], "marquee": []}
    for arq in glob.glob(pasta + "/*.png"):
        for tipo in por_tipo:
            if arq.endswith(f"-{tipo}.png"):
                d = dim_png(arq)
                if d:
                    por_tipo[tipo].append((d, os.path.getsize(arq)))
    print(f"\n== {sistema} ==")
    for tipo, itens in por_tipo.items():
        if not itens:
            continue
        dims = Counter(d for d, _ in itens).most_common(3)
        pesos = [p for _, p in itens]
        print(f"  {tipo:8s} n={len(itens):3d} dimensoes mais comuns={dims} "
              f"peso medio={sum(pesos) / len(pesos) / 1024:.0f} KB "
              f"maior={max(pesos) / 1024:.0f} KB")
