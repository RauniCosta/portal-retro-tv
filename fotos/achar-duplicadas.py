#!/usr/bin/env python3
"""Procura arquivos repetidos (mesmo conteudo) em /homelab/Fotos.
SOMENTE LE: nao move, nao apaga e nao altera nada em /homelab/Fotos.

Estrategia (para 442 GB em um PC antigo):
  1. agrupa por tamanho exato (arquivo de tamanho unico nao tem copia);
  2. dentro do grupo, compara um "resumo" do comeco, meio e fim do arquivo;
  3. so entao calcula o SHA-256 completo dos que continuam iguais.

Gera, em /opt/portal-retro-tv/fotos/:
  relatorio-duplicadas.txt   grupos de copias, com o espaco que se ganharia
  duplicadas.csv             uma linha por copia (grupo, manter?, caminho, tamanho)
  progresso.log              andamento (pode ser lido enquanto roda)

Rodar em segundo plano (continua mesmo se o PuTTY fechar):
  nohup nice -n 19 ionice -c3 sudo python3 /opt/portal-retro-tv/fotos/achar-duplicadas.py > /dev/null 2>&1 &
"""
import csv
import hashlib
import os
import sys
import time
from collections import defaultdict

RAIZ = "/homelab/Fotos"
SAIDA = "/opt/portal-retro-tv/fotos"
IGNORAR_PASTAS = {".comments", "@eaDir", ".thumbnails"}
IGNORAR_ARQ = {"Thumbs.db", "desktop.ini", ".DS_Store"}
BLOCO = 1024 * 1024

t0 = time.time()
log = open(os.path.join(SAIDA, "progresso.log"), "w", buffering=1, encoding="utf-8")


def info(msg):
    log.write(f"[{int(time.time() - t0):>6}s] {msg}\n")


def resumo_parcial(caminho, tamanho):
    """SHA-256 de 1 MB do comeco + 1 MB do meio + 1 MB do fim + o tamanho."""
    h = hashlib.sha256()
    h.update(str(tamanho).encode())
    with open(caminho, "rb") as f:
        h.update(f.read(BLOCO))
        if tamanho > 3 * BLOCO:
            f.seek(tamanho // 2)
            h.update(f.read(BLOCO))
            f.seek(max(0, tamanho - BLOCO))
            h.update(f.read(BLOCO))
    return h.hexdigest()


def sha_completo(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        while True:
            b = f.read(BLOCO)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main():
    if not os.path.isdir(RAIZ):
        print(f"{RAIZ} nao existe")
        sys.exit(1)

    # 1) inventario e agrupamento por tamanho
    por_tamanho = defaultdict(list)
    total = 0
    bytes_total = 0
    for pasta, subs, arquivos in os.walk(RAIZ):
        subs[:] = [d for d in subs if d not in IGNORAR_PASTAS]
        for nome in arquivos:
            if nome in IGNORAR_ARQ:
                continue
            c = os.path.join(pasta, nome)
            try:
                st = os.stat(c, follow_symlinks=False)
            except OSError:
                continue
            if not os.path.isfile(c) or os.path.islink(c) or st.st_size == 0:
                continue
            por_tamanho[st.st_size].append((c, st.st_mtime))
            total += 1
            bytes_total += st.st_size
            if total % 20000 == 0:
                info(f"inventario: {total} arquivos")
    candidatos = {t: v for t, v in por_tamanho.items() if len(v) > 1}
    n_cand = sum(len(v) for v in candidatos.values())
    info(f"inventario pronto: {total} arquivos, {bytes_total / 1e9:.1f} GB; "
         f"{n_cand} com tamanho repetido")

    # 2) resumo parcial e 3) hash completo
    grupos = defaultdict(list)  # sha -> [(caminho, mtime, tamanho)]
    feitos = 0
    for tamanho, itens in candidatos.items():
        parcial = defaultdict(list)
        for c, mt in itens:
            try:
                parcial[resumo_parcial(c, tamanho)].append((c, mt))
            except OSError as e:
                info(f"nao li {c}: {e}")
            feitos += 1
            if feitos % 500 == 0:
                info(f"resumo parcial: {feitos}/{n_cand}")
        for lista in parcial.values():
            if len(lista) < 2:
                continue
            for c, mt in lista:
                try:
                    grupos[sha_completo(c)].append((c, mt, tamanho))
                except OSError as e:
                    info(f"nao li {c}: {e}")

    repetidos = [g for g in grupos.values() if len(g) > 1]
    info(f"{len(repetidos)} grupos de arquivos repetidos")

    # Qual manter: o mais antigo; empate -> caminho mais curto
    repetidos.sort(key=lambda g: -g[0][2] * (len(g) - 1))
    espaco = 0
    with open(os.path.join(SAIDA, "duplicadas.csv"), "w", newline="", encoding="utf-8") as fcsv, \
            open(os.path.join(SAIDA, "relatorio-duplicadas.txt"), "w", encoding="utf-8") as rel:
        w = csv.writer(fcsv)
        w.writerow(["grupo", "acao", "tamanho_bytes", "caminho"])
        for i, g in enumerate(repetidos, 1):
            g.sort(key=lambda x: (x[1], len(x[0])))
            tam = g[0][2]
            espaco += tam * (len(g) - 1)
            rel.write(f"\n=== Grupo {i}: {len(g)} copias de {tam / 1e6:.2f} MB ===\n")
            for j, (c, mt, _) in enumerate(g):
                acao = "MANTER" if j == 0 else "COPIA"
                rel.write(f"  [{acao}] {c}\n")
                w.writerow([i, acao, tam, c])
        rel.write(f"\nRESUMO: {len(repetidos)} grupos; "
                  f"espaco recuperavel: {espaco / 1e9:.2f} GB\n")
    info(f"FIM. {len(repetidos)} grupos; recuperavel {espaco / 1e9:.2f} GB")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        info("interrompido")
