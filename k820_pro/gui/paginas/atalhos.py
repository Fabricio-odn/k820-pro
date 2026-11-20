"""Página Atalhos: os atalhos de fábrica (Fn + tecla), desenhados como teclas."""
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk  # noqa: E402

from ... import i18n  # noqa: E402
from ...atalhos import FILEIRA_F, GERAIS, LUZES  # noqa: E402
from ...i18n import t  # noqa: E402
from ..componentes import cabecalho_pagina, secao, teclas_do_atalho  # noqa: E402


def _combinacao(texto):
    """Combinação de teclas desenhada como teclas; frase (girar o botão…) como texto."""
    traduzido = t(texto) if texto in i18n.TRADUCOES else texto
    if texto.startswith("Fn +") and "(" not in texto and "apertar" not in texto:
        return teclas_do_atalho(traduzido)
    rotulo = Gtk.Label(label=traduzido, xalign=0, wrap=True)
    rotulo.add_css_class("heading")
    return rotulo


def _linha(combinacao, funcao):
    linha = Adw.ActionRow(title=funcao, title_lines=0)
    prefixo = _combinacao(combinacao) if isinstance(combinacao, str) else combinacao
    prefixo.set_size_request(190, -1)
    linha.add_prefix(prefixo)
    return linha


class PaginaAtalhos(Gtk.Box):
    def __init__(self, janela):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        self.janela = janela
        self.append(cabecalho_pagina(t("Atalhos"), t("Atalhos de fábrica do teclado. Funcionam sem nenhum programa.")))
        nota = Gtk.Label(label=t("Fonte: manual do AK820 Pro. Confira no seu teclado; alguns lotes mudam a fileira F."),
                         xalign=0, wrap=True)
        nota.add_css_class("secundario")
        nota.add_css_class("caption")
        self.append(nota)
        for titulo, itens in GERAIS:
            lista = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE, css_classes=["boxed-list"])
            for comb, func in itens:
                lista.append(_linha(comb, t(func)))
            self.append(secao(t(titulo), lista))
        lista = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE, css_classes=["boxed-list"])
        for comb, win, mac in FILEIRA_F:
            lista.append(_linha(comb, t("Windows: {w} · Mac: {m}", w=t(win), m=t(mac))))
        self.append(secao(t("Fileira F"), lista))
        lista = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE, css_classes=["boxed-list"])
        for luz, texto in LUZES:
            lista.append(_linha(teclas_do_atalho(luz) if len(luz) == 1 else _combinacao(luz), t(texto)))
        self.append(secao(t("Luzes indicadoras"), lista))

    def teclados(self):
        return []

    def definir_empilhado(self, _empilhado):
        pass

    def ao_sair(self):
        pass
