#!/usr/bin/env python3
"""Descobre os numeros dos botoes SELECT e START do controle (js0) e grava em
/homelab/pegasus/saida.conf, para o atalho Select+Start fechar o Chrome.
Rodar:  sudo python3 /opt/portal-retro-tv/portal/calibrar-saida.py
"""
import os
import select
import struct
import sys
import time

DEV = "/dev/input/js0"
SAIDA = "/homelab/pegasus/saida.conf"
FMT = "IhBB"  # tempo, valor, tipo, numero
TAM = struct.calcsize(FMT)


def esvaziar(fd):
    while select.select([fd], [], [], 0.2)[0]:
        os.read(fd, TAM * 64)


def esperar_botao(fd, nome, ignorar=()):
    print(f"\nAperte e SOLTE o botao {nome} no controle 1 ...", flush=True)
    esvaziar(fd)
    limite = time.time() + 40
    while time.time() < limite:
        if not select.select([fd], [], [], 1.0)[0]:
            continue
        dados = os.read(fd, TAM)
        if len(dados) < TAM:
            continue
        _, valor, tipo, numero = struct.unpack(FMT, dados)
        if tipo == 1 and valor == 1 and numero not in ignorar:
            print(f"  {nome} = botao {numero}")
            time.sleep(0.6)
            esvaziar(fd)
            return numero
    print("Nenhum botao detectado em 40 segundos.")
    sys.exit(1)


def main():
    if not os.path.exists(DEV):
        print(f"{DEV} nao existe (controle desconectado?)")
        sys.exit(1)
    fd = os.open(DEV, os.O_RDONLY | os.O_NONBLOCK)
    sel = esperar_botao(fd, "SELECT")
    sta = esperar_botao(fd, "START", ignorar=(sel,))
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write(f"select={sel}\nstart={sta}\n")
    os.chmod(SAIDA, 0o644)
    print(f"\nGravado em {SAIDA}: select={sel} start={sta}")


if __name__ == "__main__":
    main()
