#!/usr/bin/env bash
# Roda o software oficial do AK820 Pro no Wine registrando o que ele manda ao teclado.
#
# Uso: scripts/captura/capturar.sh <pasta com DeviceDriver.exe> <arquivo .log de saída>
# Precisa do wine e do gcc. Usa um prefixo Wine próprio em ~/.cache/k820-pro/wine.
# O registro cobre os feature reports de todas as interfaces e write/read só das
# interfaces 2 e 3; a interface 0 (o que é digitado) nunca é gravada.
set -euo pipefail
app=${1:?pasta do DeviceDriver.exe}; saida=$(realpath -m "${2:?arquivo de saída}")
aqui=$(cd "$(dirname "$0")" && pwd)
cache=~/.cache/k820-pro; mkdir -p "$cache"
gcc -O2 -shared -fPIC -o "$cache/hidlog.so" "$aqui/hidlog.c" -ldl
hid() {  # caminho do hidraw da interface $1 do 0c45:800a
  for h in /sys/class/hidraw/hidraw*; do
    grep -q 'HID_ID=0003:00000C45:0000800A' "$h/device/uevent" || continue
    [[ $(cat "$h/device/../bInterfaceNumber" 2>/dev/null) == "0$1" ]] && { echo "/dev/$(basename "$h")"; return; }
  done
  echo "AK820 Pro (cabo) não encontrado" >&2; exit 1
}
export WINEPREFIX=$cache/wine WINEDEBUG=-all HIDLOG=$saida
export HID_IF0=$(hid 0) HID_IF1=$(hid 1) HID_IF2=$(hid 2) HID_IF3=$(hid 3)
wineserver -k 2>/dev/null || true
cd "$app" && LD_PRELOAD=$cache/hidlog.so wine DeviceDriver.exe
