"""Ponto de entrada da interface: python3 -m k820_pro.gui.app (ou o comando k820-gui)."""
import os
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from pathlib import Path  # noqa: E402

from gi.repository import Adw, Gdk, Gtk  # noqa: E402

from .. import i18n  # noqa: E402
from ..preferencias import Preferencias  # noqa: E402

ID_APLICATIVO = "io.github.k820pro.Configurador"


def _aplicar_idioma(prefs):
    """Escolha feita na interface; K820_IDIOMA no ambiente tem prioridade."""
    if prefs.idioma and "K820_IDIOMA" not in os.environ:
        i18n.definir(prefs.idioma)


def main(argv=None):
    _aplicar_idioma(Preferencias.carregar())
    from .janela import Janela
    from .tema import Tema

    app = Adw.Application(application_id=ID_APLICATIVO)

    def ativar(app):
        Gtk.IconTheme.get_for_display(Gdk.Display.get_default()).add_search_path(
            str(Path(__file__).with_name("icones")))
        Gtk.Window.set_default_icon_name(ID_APLICATIVO)
        janela = app.get_active_window()
        if janela is None:
            prefs = Preferencias.carregar()
            tema = Tema()
            tema.aplicar(prefs.tema)
            janela = Janela(app, tema)
        janela.present()

    app.connect("activate", ativar)
    return app.run(sys.argv if argv is None else argv)


if __name__ == "__main__":
    sys.exit(main())
