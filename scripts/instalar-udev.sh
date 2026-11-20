#!/usr/bin/env bash
# Instala a regra udev do AK820 Pro: libera só os canais de configuração para o
# usuário da sessão e impede que o teclado seja liberado inteiro como "câmera".
# Para remover: sudo bash scripts/instalar-udev.sh --remover
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "rode com sudo: sudo bash $0 ${1:-}" >&2; exit 1; }
cd "$(dirname "$0")/.."
rm -f /etc/udev/rules.d/71-ajazz-ak820.rules   # nome antigo da regra
if [[ ${1:-} == --remover ]]; then
  rm -f /etc/udev/rules.d/69-ajazz-ak820.rules
  udevadm control --reload
  echo "regra removida. Desconecte e reconecte o cabo do teclado para valer."
  exit 0
fi
install -m 644 udev/69-ajazz-ak820.rules /etc/udev/rules.d/
udevadm control --reload
echo "regra instalada. Desconecte e reconecte o cabo do teclado para valer."
