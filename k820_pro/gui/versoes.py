"""Versões (cores) do AK820 Pro para o desenho do teclado na interface.

As cores são aproximações das fotos oficiais da Ajazz. Só mudam o desenho; a luz
e o GIF continuam com as próprias cores. Sem GTK, para poder ser testado.
"""
from dataclasses import dataclass


def _hex(t):
    return tuple(int(t[i:i + 2], 16) for i in (1, 3, 5))


@dataclass(frozen=True)
class Versao:
    nome: str                 # texto para a interface (passa por t())
    corpo: tuple | None       # None = sem corpo desenhado
    alfa: tuple
    modificadora: tuple
    destaque: tuple
    texto_alfa: tuple
    texto_mod: tuple
    texto_destaque: tuple
    teclas_destaque: frozenset


MODIFICADORAS = frozenset({
    "esc", "grave", "tab", "capslock", "shift_esq", "shift_dir", "ctrl_esq", "ctrl_dir", "win",
    "alt_esq", "alt_dir", "fn", "enter", "backspace", "delete", "home", "pgup", "pgdn",
    "cima", "baixo", "esquerda", "direita",
})

_CLARO = _hex("#EBEBEB")

VERSOES = {
    "neutro": Versao("Neutro", None, _hex("#28282E"), _hex("#28282E"), _hex("#28282E"),
                     _CLARO, _CLARO, _CLARO, frozenset()),
    "cinza-amarelo": Versao("Cinza e amarelo", _hex("#2E2F33"), _hex("#C9CACC"), _hex("#5A5C62"),
                            _hex("#F2C230"), _hex("#26272B"), _hex("#F0F0F0"), _hex("#26272B"),
                            frozenset({"esc", "enter"})),
    "branco-roxo": Versao("Branco e roxo", _hex("#EEEEF2"), _hex("#FFFFFF"), _hex("#C9B8EC"),
                          _hex("#8E6CCF"), _hex("#3B2E5A"), _hex("#3B2E5A"), _hex("#FFFFFF"),
                          frozenset({"esc", "enter"})),
    "preto": Versao("Preto", _hex("#141416"), _hex("#2A2A2E"), _hex("#1E1E21"), _hex("#2A2A2E"),
                    _hex("#E6E6E6"), _hex("#E6E6E6"), _hex("#E6E6E6"), frozenset()),
    "branco": Versao("Branco", _hex("#E9E9EC"), _hex("#FFFFFF"), _hex("#E0E0E4"), _hex("#FFFFFF"),
                     _hex("#2B2B2E"), _hex("#2B2B2E"), _hex("#2B2B2E"), frozenset()),
}


def cor_da_tecla(versao: Versao, nome: str):
    """(fundo, texto) da tecla nesta versão. Destaque tem prioridade sobre modificadora."""
    if nome in versao.teclas_destaque:
        return versao.destaque, versao.texto_destaque
    if nome in MODIFICADORAS:
        return versao.modificadora, versao.texto_mod
    return versao.alfa, versao.texto_alfa


def _luminancia(rgb):
    def canal(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (canal(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def cor_de_selecao(fundo):
    """Contorno de tecla selecionada ou marcada: preto ou branco, o que contrastar mais
    com o fundo da tecla, para aparecer em qualquer versão, tema e cor de luz."""
    escuro, claro = (0x0E, 0x0E, 0x10), (0xFF, 0xFF, 0xFF)
    lf = _luminancia(fundo)
    contraste = lambda c: (max(lf, _luminancia(c)) + 0.05) / (min(lf, _luminancia(c)) + 0.05)
    return max((escuro, claro), key=contraste)


def fundo_da_tecla(versao: Versao, nome: str, cores: dict):
    """Cor de fundo no desenho: a cor de luz da tecla, se houver, senão a da versão."""
    return cores[nome] if nome in cores else cor_da_tecla(versao, nome)[0]
