"""Tema da interface: escuro (padrão) ou claro, os dois em preto e branco.

Troca o esquema de cores da libadwaita e a folha CSS na hora, sem reiniciar.
"""
from pathlib import Path

from gi.repository import Adw, Gdk, Gtk

from ..preferencias import TEMAS

FOLHAS = {"escuro": "estilo.css", "claro": "estilo-claro.css"}
ESQUEMAS = {"escuro": Adw.ColorScheme.FORCE_DARK, "claro": Adw.ColorScheme.FORCE_LIGHT}

# contorno normal das teclas no desenho, por tema (seleção e marcação usam
# versoes.cor_de_selecao, que depende da cor da tecla)
CORES_DESENHO = {
    "escuro": {"contorno": (0x5A, 0x5A, 0x60)},
    "claro": {"contorno": (0xB4, 0xB4, 0xBA)},
}


class Tema:
    def __init__(self):
        self.atual = None
        self.provedor = None
        self.registrados = 0

    def aplicar(self, nome):
        if nome not in TEMAS:
            raise ValueError(f"tema desconhecido: {nome}")
        tela = Gdk.Display.get_default()
        if self.provedor is not None:
            Gtk.StyleContext.remove_provider_for_display(tela, self.provedor)
            self.registrados -= 1
        provedor = Gtk.CssProvider()
        provedor.load_from_path(str(Path(__file__).with_name(FOLHAS[nome])))
        # acima da prioridade de usuário: um tema global (~/.config/gtk-4.0/gtk.css)
        # não pode tirar o preto e branco do app
        Gtk.StyleContext.add_provider_for_display(tela, provedor, Gtk.STYLE_PROVIDER_PRIORITY_USER + 1)
        self.provedor = provedor
        self.registrados += 1
        Adw.StyleManager.get_default().set_color_scheme(ESQUEMAS[nome])
        self.atual = nome
