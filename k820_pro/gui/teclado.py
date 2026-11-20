"""Desenho do teclado (81 teclas, geometria do software oficial) com seleção por clique."""
import math

import gi

gi.require_version("PangoCairo", "1.0")
from gi.repository import Gtk, Pango, PangoCairo  # noqa: E402

from ..layout import TECLAS
from .tema import CORES_DESENHO
from .versoes import VERSOES, cor_da_tecla, cor_de_selecao, cor_texto_bloqueado, fundo_da_tecla

ROTULOS = {
    "esc": "Esc", "delete": "Del", "grave": "`", "menos": "-", "igual": "=", "backspace": "⌫",
    "home": "Home", "tab": "Tab", "colchete_esq": "[", "colchete_dir": "]", "barra_invertida": "\\",
    "pgup": "PgUp", "capslock": "Caps", "ponto_virgula": ";", "aspas": "'", "enter": "Enter",
    "pgdn": "PgDn", "shift_esq": "Shift", "virgula": ",", "ponto": ".", "barra": "/",
    "shift_dir": "Shift", "cima": "↑", "ctrl_esq": "Ctrl", "win": "Win", "alt_esq": "Alt",
    "espaco": "", "alt_dir": "Alt", "fn": "Fn", "ctrl_dir": "Ctrl", "esquerda": "←",
    "baixo": "↓", "direita": "→",
}

MARGEM = 8
X0 = min(t.x for t in TECLAS)
Y0 = min(t.y for t in TECLAS)
LARGURA = max(t.x + t.largura for t in TECLAS) - X0
ALTURA = max(t.y + t.altura for t in TECLAS) - Y0


def rotulo(t):
    return ROTULOS.get(t.nome, t.nome.upper())


class Teclado(Gtk.DrawingArea):
    """cores: {nome: (r, g, b)} pinta o fundo; marcadas: nomes com borda de destaque."""

    def __init__(self, multipla=False, ao_mudar=None, bloqueadas=(), interativo=True):
        super().__init__()
        self.multipla = multipla
        self.ao_mudar = ao_mudar
        self.bloqueadas = set(bloqueadas)
        self.selecao = set()
        self.cores = {}
        self.marcadas = set()
        self.versao = VERSOES["neutro"]
        self.tema = "escuro"
        self.set_content_width(int(LARGURA * 0.55) + 2 * MARGEM)  # encolhe; o desenho se ajusta à largura
        self.set_content_height(int(ALTURA * 0.55) + 2 * MARGEM)
        self.set_hexpand(True)
        self.set_draw_func(self._desenhar)
        if interativo:
            clique = Gtk.GestureClick()
            clique.connect("pressed", self._clicar)
            self.add_controller(clique)

    def _escala(self, w, h):
        e = min((w - 2 * MARGEM) / LARGURA, (h - 2 * MARGEM) / ALTURA)
        dx = (w - LARGURA * e) / 2
        dy = (h - ALTURA * e) / 2
        return e, dx, dy

    def _retangulo(self, t, e, dx, dy):
        return (dx + (t.x - X0) * e, dy + (t.y - Y0) * e, t.largura * e, t.altura * e)

    def _desenhar(self, _area, cr, w, h):
        e, dx, dy = self._escala(w, h)
        fonte = Pango.FontDescription.from_string(f"Sans {max(6.5, 7.5 * e):.1f}")
        if self.versao.corpo:
            m = 10 * e
            _arredondado(cr, dx - m, dy - m, LARGURA * e + 2 * m, ALTURA * e + 2 * m, 10 * e)
            cr.set_source_rgb(*(c / 255 for c in self.versao.corpo))
            cr.fill()
        for t in TECLAS:
            x, y, lw, lh = self._retangulo(t, e, dx, dy)
            _arredondado(cr, x, y, lw, lh, 4 * e)
            fundo = fundo_da_tecla(self.versao, t.nome, self.cores)
            cr.set_source_rgb(*(c / 255 for c in fundo))
            cr.fill_preserve()
            cores_tema = CORES_DESENHO[self.tema]
            if t.nome in self.selecao:
                cr.set_source_rgb(*(c / 255 for c in cor_de_selecao(fundo)))
                cr.set_line_width(3)
            elif t.nome in self.marcadas:
                cr.set_source_rgb(*(c / 255 for c in cor_de_selecao(fundo)))
                cr.set_line_width(2.5)
                cr.set_dash([4 * e, 2 * e])
            else:
                cr.set_source_rgb(*(c / 255 for c in cores_tema["contorno"]))
                cr.set_line_width(1)
            cr.stroke()
            cr.set_dash([])
            texto = rotulo(t)
            if not texto:
                continue
            if t.nome in self.cores:
                claro = (0.299 * fundo[0] + 0.587 * fundo[1] + 0.114 * fundo[2]) > 140
                cr.set_source_rgb(*((0.1, 0.1, 0.1) if claro else (0.92, 0.92, 0.92)))
            else:
                cr.set_source_rgb(*(c / 255 for c in cor_da_tecla(self.versao, t.nome)[1]))
            if t.nome in self.bloqueadas:
                apagado = cor_texto_bloqueado(fundo, cor_da_tecla(self.versao, t.nome)[1])
                cr.set_source_rgb(*(c / 255 for c in apagado))
            camada = PangoCairo.create_layout(cr)
            camada.set_font_description(fonte)
            camada.set_text(texto, -1)
            tw, th = camada.get_pixel_size()
            cr.move_to(x + (lw - tw) / 2, y + (lh - th) / 2)
            PangoCairo.show_layout(cr, camada)

    def _clicar(self, _gesto, _n, px, py):
        e, dx, dy = self._escala(self.get_width(), self.get_height())
        for t in TECLAS:
            x, y, lw, lh = self._retangulo(t, e, dx, dy)
            if x <= px <= x + lw and y <= py <= y + lh:
                if t.nome in self.bloqueadas:
                    return
                if self.multipla:
                    self.selecao ^= {t.nome}
                else:
                    self.selecao = set() if t.nome in self.selecao else {t.nome}
                self.queue_draw()
                if self.ao_mudar:
                    self.ao_mudar(self.selecao)
                return

    def selecionar(self, nomes):
        self.selecao = set(nomes)
        self.queue_draw()
        if self.ao_mudar:
            self.ao_mudar(self.selecao)


def _arredondado(cr, x, y, w, h, r):
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()
