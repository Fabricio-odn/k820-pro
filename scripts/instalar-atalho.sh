#!/usr/bin/env bash
# Põe o "K820 Pro" no menu de aplicativos do usuário (sem sudo). Para remover: --remover
set -euo pipefail
id=io.github.k820pro.Configurador
apps=~/.local/share/applications; icones=~/.local/share/icons/hicolor/scalable/apps
simbolicos=~/.local/share/icons/hicolor/symbolic/apps
# Se já existe um icon-theme.cache na pasta de ícones do usuário, o GTK continua
# usando ele enquanto a pasta hicolor em si não mudar, e um ícone novo numa
# subpasta fica invisível. Por isso o cache é refeito sempre.
atualizar_caches() {
  local tema=~/.local/share/icons/hicolor
  if [[ -f $tema/icon-theme.cache ]]; then
    gtk4-update-icon-cache -q -f -t "$tema" 2>/dev/null || gtk-update-icon-cache -q -f -t "$tema" 2>/dev/null || rm -f "$tema/icon-theme.cache"
  fi
  touch "$tema"
  update-desktop-database -q "$apps" 2>/dev/null || true
}

if [[ ${1:-} == --remover ]]; then
  rm -f "$apps/$id.desktop" "$icones/$id.svg" "$simbolicos/$id-symbolic.svg"
  atualizar_caches; echo "atalho removido"; exit 0
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
atualizar_caches
echo "atalho instalado: procure por \"K820 Pro Studio\" no menu"
