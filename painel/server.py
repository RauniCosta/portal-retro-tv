#!/usr/bin/env python3
"""Painel do homelab: servidor somente leitura, sem dependencias externas."""
import json
import os
import shutil
import socket
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = int(os.environ.get("PAINEL_PORT", "8088"))
BASE = Path(__file__).resolve().parent

# Atalhos exibidos no painel. Porta 80 = RomM, 8096 = Jellyfin.
SERVICOS = [
    {"nome": "RomM (jogos retro)", "porta": 80},
    {"nome": "Jellyfin (filmes)", "porta": 8096},
]


def memoria():
    info = {}
    with open("/proc/meminfo") as f:
        for linha in f:
            chave, valor = linha.split(":", 1)
            info[chave] = int(valor.split()[0]) * 1024  # kB -> bytes
    return {
        "total": info["MemTotal"],
        "disponivel": info["MemAvailable"],
        "swap_total": info["SwapTotal"],
        "swap_usada": info["SwapTotal"] - info["SwapFree"],
    }


def uptime_segundos():
    with open("/proc/uptime") as f:
        return float(f.read().split()[0])


def disco(caminho="/"):
    uso = shutil.disk_usage(caminho)
    return {"total": uso.total, "usado": uso.used, "livre": uso.free}


def containers():
    try:
        saida = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Image}}\t{{.Status}}"],
            capture_output=True, text=True, timeout=5, check=True,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    itens = []
    for linha in saida.splitlines():
        partes = linha.split("\t")
        if len(partes) == 3:
            itens.append({"nome": partes[0], "imagem": partes[1], "status": partes[2]})
    return itens


def status():
    return {
        "host": socket.gethostname(),
        "uptime": uptime_segundos(),
        "carga": os.getloadavg(),
        "memoria": memoria(),
        "disco": disco("/"),
        "containers": containers(),
        "servicos": SERVICOS,
    }


class Handler(BaseHTTPRequestHandler):
    def _enviar(self, codigo, tipo, corpo):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        if self.path == "/api/status":
            corpo = json.dumps(status()).encode()
            self._enviar(200, "application/json", corpo)
        elif self.path in ("/", "/index.html"):
            self._enviar(200, "text/html; charset=utf-8", (BASE / "index.html").read_bytes())
        else:
            self._enviar(404, "text/plain; charset=utf-8", b"nao encontrado")

    def log_message(self, formato, *args):
        pass  # sem ruido no terminal


if __name__ == "__main__":
    print(f"Painel em http://0.0.0.0:{PORT}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
