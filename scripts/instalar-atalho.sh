#!/usr/bin/env bash
# Põe o "K820 Pro" no menu de aplicativos do usuário (sem sudo). Para remover: --remover
set -euo pipefail
id=io.github.k820pro.Configurador
apps=~/.local/share/applications; icones=~/.local/share/icons/hicolor/scalable/apps
simbolicos=~/.local/share/icons/hicolor/symbolic/apps
if [[ ${1:-} == --remover ]]; then
  rm -f "$apps/$id.desktop" "$icones/$id.svg" "$simbolicos/$id-symbolic.svg"; echo "atalho removido"; exit 0
fi
raiz=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$apps" "$icones" "$simbolicos"
install -m 644 "$raiz/k820_pro/gui/icones/hicolor/scalable/apps/$id.svg" "$icones/"
install -m 644 "$raiz/k820_pro/gui/icones/hicolor/symbolic/apps/$id-symbolic.svg" "$simbolicos/"
if command -v k820-gui >/dev/null; then exec_linha="k820-gui"
else exec_linha="env PYTHONPATH=\"$raiz\" python3 -m k820_pro.gui.app"; fi
cat > "$apps/$id.desktop" <<FIM
[Desktop Entry]
Type=Application
Name=K820 Pro Studio
Comment=Configure the Ajazz AK820 Pro keyboard
Comment[pt_BR]=Configura o teclado Ajazz AK820 Pro
Comment[zh_CN]=配置 Ajazz AK820 Pro 键盘
Exec=$exec_linha
Icon=$id
Terminal=false
Categories=Settings;HardwareSettings;
Keywords=keyboard;teclado;ajazz;rgb;键盘;
FIM
echo "atalho instalado: procure por \"K820 Pro Studio\" no menu"
