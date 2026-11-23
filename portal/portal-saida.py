#!/usr/bin/env python3
"""Fica de olho nos controles /dev/input/js*. Quando Select e Start estao
apertados ao mesmo tempo, fecha o Chrome do portal (volta ao Pegasus).
Iniciado e encerrado pelo portal-abrir.
"""
import glob
import os
import select
import struct
import subprocess
import sys

CONF = "/homelab/pegasus/saida.conf"
FMT = "IhBB"
TAM = struct.calcsize(FMT)


def ler_conf():
    valores = {}
    try:
        with open(CONF, encoding="utf-8") as f:
            for linha in f:
                if "=" in linha:
                    k, v = linha.strip().split("=", 1)
                    valores[k] = int(v)
    except (OSError, ValueError):
        pass
    return valores.get("select"), valores.get("start")


def main():
    sel, sta = ler_conf()
    if sel is None or sta is None:
        print("saida.conf ausente: atalho Select+Start desativado", flush=True)
        return
    fds = {}
    for caminho in glob.glob("/dev/input/js*"):
        try:
            fds[os.open(caminho, os.O_RDONLY | os.O_NONBLOCK)] = set()
        except OSError:
            pass
    if not fds:
        print("nenhum controle encontrado", flush=True)
        return
    print(f"vigiando {len(fds)} controle(s): select={sel} start={sta}", flush=True)
    while True:
        prontos, _, _ = select.select(list(fds), [], [], 5.0)
        for fd in prontos:
            try:
                dados = os.read(fd, TAM)
            except OSError:
                continue
            if len(dados) < TAM:
                continue
            _, valor, tipo, numero = struct.unpack(FMT, dados)
            if tipo != 1:
                continue
            apertados = fds[fd]
            if valor:
                apertados.add(numero)
            else:
                apertados.discard(numero)
            if sel in apertados and sta in apertados:
                print("Select+Start: fechando o Chrome do portal", flush=True)
                subprocess.run(["pkill", "-f", "portal-chrome"])
                apertados.clear()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
