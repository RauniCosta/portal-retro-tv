#!/usr/bin/env bash
# Instala o x11vnc para ver e controlar a tela real do Mint (a mesma da TV).
# Rodar como root:  sudo bash 3-acesso-remoto.sh
# Acesso permitido so a partir da rede local (192.168.0.0/24) e do proprio Mint.
# Para acesso de fora de casa, o caminho recomendado e o Tailscale (nao abra a porta 5900 no roteador).
set -u

if [ "$(id -u)" -ne 0 ]; then
  echo "Rode com sudo." >&2
  exit 1
fi

echo "=== 1/3 Instalando o x11vnc ==="
apt-get update
apt-get install -y x11vnc

echo
echo "=== 2/3 Definindo a senha do acesso remoto ==="
echo "Digite uma senha FORTE quando pedido (ela fica em /etc/x11vnc.pass, so root le)."
x11vnc -storepasswd /etc/x11vnc.pass
chmod 600 /etc/x11vnc.pass

echo
echo "=== 3/3 Criando o servico ==="
cat > /etc/systemd/system/x11vnc.service <<'EOF'
[Unit]
Description=x11vnc - acesso remoto a tela do Mint
After=display-manager.service network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/bin/x11vnc -display :0 -auth /var/run/lightdm/root/:0 -rfbauth /etc/x11vnc.pass -rfbport 5900 -allow 192.168.0.,127.0.0.1 -forever -shared -noxdamage -repeat -logappend /var/log/x11vnc.log
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now x11vnc.service
sleep 2
systemctl --no-pager status x11vnc.service | head -n 12

echo
echo "Pronto. No Windows, abra um cliente VNC (TigerVNC Viewer ou RealVNC Viewer) e conecte em:"
echo "  IP-DO-PC:5900"
echo "Para remover: sudo systemctl disable --now x11vnc && sudo rm /etc/systemd/system/x11vnc.service /etc/x11vnc.pass"
