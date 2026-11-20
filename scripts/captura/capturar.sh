#!/usr/bin/env bash
# Roda o software oficial do AK820 Pro no Wine registrando o que ele manda ao teclado.
#
# Uso: scripts/captura/capturar.sh <pasta com DeviceDriver.exe> <arquivo .log de saída> [cabo|dongle]
# Precisa do wine e do gcc. Usa um prefixo Wine próprio em ~/.cache/k820-pro/wine.
# O registro cobre os feature reports de todas as interfaces e write/read só das
# interfaces 2 e 3; a interface 0 (o que é digitado) nunca é gravada.
set -euo pipefail
app=${1:?pasta do DeviceDriver.exe}; saida=$(realpath -m "${2:?arquivo de saída}"); modo=${3:-cabo}
# cabo: interfaces 0-3 do 0c45:800a. dongle: interfaces 0, 2, 3 e 4 do 0c45:fdfd
# (no registro elas aparecem como if0, if1, if2 e if3, nessa ordem).
if [[ $modo == dongle ]]; then pid=FDFD; ifs=(0 2 3 4); else pid=800A; ifs=(0 1 2 3); fi
aqui=$(cd "$(dirname "$0")" && pwd)
cache=~/.cache/k820-pro; mkdir -p "$cache"
gcc -O2 -shared -fPIC -o "$cache/hidlog.so" "$aqui/hidlog.c" -ldl
hid() {  # caminho do hidraw da interface $1 do teclado (cabo) ou do dongle
  for h in /sys/class/hidraw/hidraw*; do
    grep -q "HID_ID=0003:00000C45:0000$pid" "$h/device/uevent" || continue
    [[ $(cat "$h/device/../bInterfaceNumber" 2>/dev/null) == "0$1" ]] && { echo "/dev/$(basename "$h")"; return; }
  done
  echo "AK820 Pro ($modo) não encontrado" >&2; exit 1
}
export WINEPREFIX=$cache/wine WINEDEBUG=-all HIDLOG=$saida
export HID_IF0=$(hid ${ifs[0]}) HID_IF1=$(hid ${ifs[1]}) HID_IF2=$(hid ${ifs[2]}) HID_IF3=$(hid ${ifs[3]})
wineserver -k 2>/dev/null || true
cd "$app" && LD_PRELOAD=$cache/hidlog.so wine DeviceDriver.exe
