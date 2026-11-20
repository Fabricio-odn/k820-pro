from pathlib import Path

import pytest

PASTA = Path(__file__).resolve().parent.parent / "k820_pro" / "gui"


def test_folhas_existem_e_tem_as_cores():
    escuro = (PASTA / "estilo.css").read_text()
    claro = (PASTA / "estilo-claro.css").read_text()
    assert "--window-bg-color: #0E0E10" in escuro and "--accent-bg-color: #FFFFFF" in escuro
    assert "--window-bg-color: #FAFAFA" in claro and "--accent-bg-color: #0E0E10" in claro


def _gtk():
    gi = pytest.importorskip("gi")
    gi.require_version("Gtk", "4.0")
    gi.require_version("Adw", "1")
    from gi.repository import Adw, Gtk
    if not Gtk.init_check():
        pytest.skip("sem display")
    Adw.init()
    return Gtk


def test_trocar_tema_mantem_um_provedor():
    _gtk()
    from k820_pro.gui.tema import Tema
    tema = Tema()
    tema.aplicar("claro")
    primeiro = tema.provedor
    tema.aplicar("escuro")
    tema.aplicar("claro")
    assert tema.atual == "claro"
    assert tema.provedor is not primeiro
    assert tema.registrados == 1


def test_tema_desconhecido():
    _gtk()
    from k820_pro.gui.tema import Tema
    with pytest.raises(ValueError):
        Tema().aplicar("roxo")


def test_idioma_sobrevive_a_troca_de_tema(tmp_path, monkeypatch):
    _gtk()
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    from gi.repository import GLib
    from k820_pro.gui.janela import Janela
    from k820_pro.preferencias import Preferencias
    j = Janela(None)
    j.lookup_action("idioma").activate(GLib.Variant.new_string("en"))
    j._alternar_tema()
    j.aj_versao.set_selected(1)
    assert Preferencias.carregar().idioma == "en"
    j.destroy()
