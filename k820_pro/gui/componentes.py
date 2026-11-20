"""Peças repetidas das páginas, no mesmo desenho do dazz-mouse: cabeçalho de página,
título de seção, cartão, paleta de cores, deslizante de 0 a 5 e seletor segmentado."""
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, GLib, Gtk  # noqa: E402

from ..i18n import t  # noqa: E402

PALETA = (("Branco", (0xFF, 0xFF, 0xFF)), ("Vermelho", (0xFF, 0x1A, 0x1A)), ("Laranja", (0xFF, 0x7A, 0x00)),
          ("Amarelo", (0xFF, 0xE6, 0x00)), ("Verde", (0x00, 0xFF, 0x40)), ("Ciano", (0x00, 0xE5, 0xFF)),
          ("Azul", (0x2A, 0x4B, 0xFF)), ("Roxo", (0xB0, 0x00, 0xFF)))


class Debounce:
    """Junta toques seguidos: a ação roda uma vez, `atraso_ms` depois do último."""

    def __init__(self, atraso_ms, acao):
        self._atraso, self._acao, self._pendente = atraso_ms, acao, None

    def tocar(self):
        if self._pendente is not None:
            GLib.source_remove(self._pendente)
        self._pendente = GLib.timeout_add(self._atraso, self._vencer)

    def disparar_agora(self):
        if self._pendente is not None:
            GLib.source_remove(self._pendente)
            self._pendente = None
            self._acao()

    def _vencer(self):
        self._pendente = None
        self._acao()
        return GLib.SOURCE_REMOVE


def cabecalho_pagina(titulo, subtitulo):
    caixa = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    rotulo = Gtk.Label(label=titulo, xalign=0)
    rotulo.add_css_class("titulo-pagina")
    sub = Gtk.Label(label=subtitulo, xalign=0, wrap=True)
    sub.add_css_class("secundario")
    caixa.append(rotulo)
    caixa.append(sub)
    return caixa


def titulo_secao(texto, nota=None):
    caixa = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    rotulo = Gtk.Label(label=texto, xalign=0)
    rotulo.add_css_class("heading")
    caixa.append(rotulo)
    if nota:
        n = Gtk.Label(label=nota, xalign=0, wrap=True)
        n.add_css_class("secundario")
        n.add_css_class("caption")
        caixa.append(n)
    return caixa


def cartao(filho=None, espaco=10):
    caixa = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=espaco)
    caixa.add_css_class("cartao")
    if filho is not None:
        filho.set_margin_top(16)
        filho.set_margin_bottom(16)
        filho.set_margin_start(16)
        filho.set_margin_end(16)
        caixa.append(filho)
    return caixa


def pagina_com_margens(conteudo, largura=1100):
    clamp = Adw.Clamp(maximum_size=largura, child=conteudo)
    clamp.set_margin_top(28)
    clamp.set_margin_bottom(28)
    clamp.set_margin_start(24)
    clamp.set_margin_end(24)
    return clamp


def secao(titulo, filho, nota=None):
    caixa = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    caixa.append(titulo_secao(titulo, nota))
    caixa.append(filho)
    return caixa


class Colunas(Gtk.Box):
    """Duas colunas que viram uma só em janela estreita (definir_empilhado)."""

    def __init__(self, esquerda, direita, largura_direita=380):
        super().__init__(spacing=24)
        self.esquerda, self.direita = esquerda, direita
        esquerda.set_hexpand(True)
        esquerda.set_valign(Gtk.Align.START)
        direita.set_size_request(largura_direita, -1)
        self.append(esquerda)
        self.append(direita)

    def definir_empilhado(self, empilhado):
        self.set_orientation(Gtk.Orientation.VERTICAL if empilhado else Gtk.Orientation.HORIZONTAL)
        self.direita.set_size_request(-1 if empilhado else 380, -1)


def amostra(cor, tamanho=24):
    """Quadradinho pintado com a cor (a cor é conteúdo, não tema)."""
    area = Gtk.DrawingArea(content_width=tamanho, content_height=tamanho)

    def pintar(_a, cr, largura, altura):
        cr.set_source_rgb(*(c / 255 for c in cor))
        cr.rectangle(0, 0, largura, altura)
        cr.fill()

    area.set_draw_func(pintar)
    return area


class Paleta(Gtk.Box):
    """Cores prontas, arco-íris e uma cor livre. ao_mudar(cor, arco_iris)."""

    def __init__(self, ao_mudar, com_arco_iris=True):
        super().__init__(spacing=8)
        self.ao_mudar = ao_mudar
        self.cor, self.arco_iris = (255, 0, 0), False
        self._botoes = []
        self._mudando = False
        for nome, cor in PALETA:
            b = Gtk.ToggleButton(child=amostra(cor), tooltip_text=t(nome))
            b.add_css_class("amostra")
            b.connect("toggled", self._escolhida, cor, False)
            self._botoes.append((b, cor, False))
            self.append(b)
        if com_arco_iris:
            b = Gtk.ToggleButton(child=_amostra_arco_iris(), tooltip_text=t("Arco-íris"))
            b.add_css_class("amostra")
            b.connect("toggled", self._escolhida, None, True)
            self._botoes.append((b, None, True))
            self.append(b)
        self.livre = Gtk.ColorDialogButton(dialog=Gtk.ColorDialog(with_alpha=False),
                                           tooltip_text=t("Outra cor"), valign=Gtk.Align.CENTER)
        self.livre.connect("notify::rgba", self._livre_mudou)
        self.append(self.livre)

    def definir(self, cor, arco_iris=False):
        self._mudando = True
        self.cor, self.arco_iris = tuple(cor), arco_iris
        for b, c, ai in self._botoes:
            b.set_active(ai if arco_iris else (not ai and c == self.cor))
        rgba = Gdk.RGBA()
        rgba.red, rgba.green, rgba.blue, rgba.alpha = (*(c / 255 for c in self.cor), 1)
        self.livre.set_rgba(rgba)
        self._mudando = False

    def _escolhida(self, botao, cor, arco_iris):
        if self._mudando or not botao.get_active():
            return
        self.definir(cor or self.cor, arco_iris)
        self.ao_mudar(self.cor, self.arco_iris)

    def _livre_mudou(self, botao, _p):
        if self._mudando:
            return
        c = botao.get_rgba()
        self.definir(tuple(round(x * 255) for x in (c.red, c.green, c.blue)), False)
        self.ao_mudar(self.cor, self.arco_iris)


def _amostra_arco_iris(tamanho=24):
    area = Gtk.DrawingArea(content_width=tamanho, content_height=tamanho)

    def pintar(_a, cr, largura, altura):
        import cairo
        g = cairo.LinearGradient(0, 0, largura, 0)
        for i, c in enumerate(((1, .1, .1), (1, .5, 0), (1, .9, 0), (0, 1, .25), (0, .6, 1), (.7, 0, 1))):
            g.add_color_stop_rgb(i / 5, *c)
        cr.set_source(g)
        cr.rectangle(0, 0, largura, altura)
        cr.fill()

    area.set_draw_func(pintar)
    return area


def escala(minimo, maximo, ao_mudar):
    """Deslizante com marcas inteiras; ao_mudar(valor int)."""
    e = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, minimo, maximo, 1)
    e.set_round_digits(0)
    e.set_draw_value(False)
    e.set_hexpand(True)
    for v in range(minimo, maximo + 1):
        e.add_mark(v, Gtk.PositionType.BOTTOM, str(v))
    e.connect("value-changed", lambda w: ao_mudar(int(round(w.get_value()))))
    return e


def segmentado(opcoes, ao_mudar):
    """Seletor segmentado (Adw.ToggleGroup). opcoes: [(chave, rótulo)]; ao_mudar(chave)."""
    grupo = Adw.ToggleGroup(homogeneous=True)
    for chave, rotulo in opcoes:
        grupo.add(Adw.Toggle(name=chave, label=rotulo))
    grupo.connect("notify::active-name", lambda g, _p: g.get_active_name() and ao_mudar(g.get_active_name()))
    return grupo


def grade_de_opcoes(opcoes, ao_mudar, colunas=4):
    """Botões .opcao em grade, um marcado por vez. Devolve (grade, {chave: botão})."""
    grade = Gtk.Grid(column_spacing=8, row_spacing=8, column_homogeneous=True)
    botoes, primeiro = {}, None
    for i, (chave, rotulo) in enumerate(opcoes):
        b = Gtk.ToggleButton(label=rotulo, group=primeiro)
        b.add_css_class("opcao")
        b.get_child().set_ellipsize(3)  # Pango.EllipsizeMode.END
        b.connect("toggled", lambda w, k=chave: w.get_active() and ao_mudar(k))
        primeiro = primeiro or b
        botoes[chave] = b
        grade.attach(b, i % colunas, i // colunas, 1, 1)
    return grade, botoes


def teclas_do_atalho(texto):
    """Desenha "Fn + Q / W / E" como teclas: cada parte entre + vira uma tecla."""
    caixa = Gtk.Box(spacing=4, valign=Gtk.Align.CENTER)
    partes = [p.strip() for p in texto.split(" + ")]
    for i, parte in enumerate(partes):
        if i:
            mais = Gtk.Label(label="+")
            mais.add_css_class("secundario")
            caixa.append(mais)
        for j, sub in enumerate(parte.split(" / ")):
            if j:
                barra = Gtk.Label(label="/")
                barra.add_css_class("secundario")
                caixa.append(barra)
            rotulo = Gtk.Label(label=sub)
            rotulo.add_css_class("tecla-atalho")
            caixa.append(rotulo)
    return caixa
