#!/usr/bin/env bash
# Instala a regra udev que libera o canal de configuração do AK820 Pro para o usuário da sessão.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "rode com sudo: sudo bash $0" >&2; exit 1; }
cd "$(dirname "$0")/.."
install -m 644 udev/71-ajazz-ak820.rules /etc/udev/rules.d/
udevadm control --reload
udevadm trigger --subsystem-match=hidraw --subsystem-match=usb --action=change
echo "regra instalada; se o teclado já estava ligado, desconecte e reconecte o cabo"
