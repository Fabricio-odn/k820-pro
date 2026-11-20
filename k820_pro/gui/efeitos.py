"""Simulação aproximada dos efeitos de luz para a prévia da interface.

Não é o firmware: reproduz a ideia de cada efeito (onda, respiração, espectro…)
com a cor, o brilho, a velocidade e a direção escolhidos. Os efeitos que reagem
ao toque são simulados com "toques" pseudoaleatórios.
"""
import colorsys
import math

from ..layout import TECLAS

CX = (min(t.x for t in TECLAS) + max(t.x + t.largura for t in TECLAS)) / 2
CY = (min(t.y for t in TECLAS) + max(t.y + t.altura for t in TECLAS)) / 2
LARG = max(t.x + t.largura for t in TECLAS) - min(t.x for t in TECLAS)
ALT = max(t.y + t.altura for t in TECLAS) - min(t.y for t in TECLAS)
X0 = min(t.x for t in TECLAS)
Y0 = min(t.y for t in TECLAS)


def _hsv(h, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, 1.0, max(0.0, min(1.0, v)))
    return r, g, b


def _ruido(*xs):
    """Número pseudoaleatório estável em [0, 1) a partir de inteiros."""
    h = 2166136261
    for x in xs:
        h = ((h ^ (int(x) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h / 2 ** 32


def cor_da_tecla(tecla, tempo, efeito, cor=(255, 0, 0), arco_iris=False, brilho=5, velocidade=3,
                 direcao="esquerda"):
    """Cor (r, g, b de 0 a 255) de uma tecla no instante `tempo` (segundos)."""
    ritmo = 0.25 + velocidade * 0.3
    tt = tempo * ritmo
    cx = ((tecla.x + tecla.largura / 2) - X0) / LARG   # 0..1
    cy = ((tecla.y + tecla.altura / 2) - Y0) / ALT     # 0..1
    sinal = -1 if direcao in ("direita", "baixo") else 1
    base = tuple(c / 255 for c in cor)

    def colorir(matiz, v=1.0):
        return _hsv(matiz, v) if arco_iris else tuple(c * v for c in base)

    if efeito == "desligado":
        rgb = (0, 0, 0)
    elif efeito == "estatico":
        rgb = colorir(cx, 1.0)
    elif efeito in ("respiracao", "pulsar"):
        f = 1.0 if efeito == "respiracao" else 2.2
        v = 0.5 - 0.5 * math.cos(tt * f * 2)
        rgb = colorir(tt * 0.05, v)
    elif efeito == "espectro":
        rgb = _hsv(tt * 0.15)
    elif efeito == "onda":
        rgb = colorir(cx * sinal + tt * 0.25, 0.5 + 0.5 * math.sin((cx * sinal + tt * 0.5) * 6.28))
        if arco_iris:
            rgb = _hsv(cx * sinal + tt * 0.25)
    elif efeito == "rolagem":
        pos = cy * sinal + tt * 0.3
        rgb = _hsv(pos) if arco_iris else colorir(0, 0.5 + 0.5 * math.sin(pos * 6.28))
    elif efeito == "fluxo":
        rgb = _hsv(cx * sinal * 0.6 + tt * 0.2) if arco_iris else colorir(0, (math.sin((cx * sinal - tt) * 9) + 1) / 2)
    elif efeito == "inclinado":
        d = (cx + cy) * sinal
        rgb = _hsv(d * 0.6 + tt * 0.2) if arco_iris else colorir(0, (math.sin((d - tt) * 7) + 1) / 2)
    elif efeito == "do-centro":
        dist = math.hypot(cx - 0.5, (cy - 0.5) * 0.4)
        rgb = _hsv(dist * 1.5 - tt * 0.25) if arco_iris else colorir(0, (math.sin((dist - tt * 0.3) * 18) + 1) / 2)
    elif efeito == "giro":
        ang = math.atan2((cy - 0.5) * 0.4, cx - 0.5) / (2 * math.pi)
        rgb = _hsv(ang + tt * 0.2) if arco_iris else colorir(0, (math.sin((ang - tt * 0.3) * 12.56) + 1) / 2)
    elif efeito in ("ondulacao", "explosao"):
        periodo = 2.0
        fase = (tt % periodo) / periodo
        foco = _ruido(int(tt / periodo), 7)
        dist = math.hypot(cx - foco, (cy - 0.5) * 0.4)
        largura = 0.06 if efeito == "ondulacao" else 0.25
        v = max(0.0, 1 - abs(dist - fase * 0.9) / largura)
        if efeito == "explosao":
            v = max(0.0, 1 - dist / (fase * 0.9 + 0.01)) * (1 - fase)
        rgb = colorir(dist + tt * 0.1, v)
    elif efeito == "lancamento":
        fase = (tt * 0.6) % 1.0
        coluna = _ruido(int(tt * 0.6), 3)
        v = max(0.0, 1 - abs(cx - coluna) * 12) * max(0.0, 1 - abs((1 - cy) - fase) * 4)
        rgb = colorir(coluna, v)
    elif efeito == "vaivem":
        pos = 0.5 + 0.5 * math.sin(tt * 1.5)
        v = max(0.0, 1 - abs(cx - pos) * 5)
        rgb = colorir(cx, v)
    elif efeito in ("cintilante", "colorido", "chuva"):
        passo = int(tt * 3)
        semente = _ruido(tecla.indice, passo)
        if efeito == "chuva":
            coluna = int(cx * 16)
            queda = (tt * 0.8 + _ruido(coluna, 1)) % 1.4
            v = max(0.0, 1 - abs(cy - queda) * 5)
        else:
            v = semente if semente > 0.55 else 0.0
        matiz = _ruido(tecla.indice, passo, 9) if (efeito == "colorido" or arco_iris) else 0
        rgb = _hsv(matiz, v) if (efeito == "colorido" or arco_iris) else tuple(c * v for c in base)
    elif efeito in ("acende-ao-tocar", "apaga-ao-tocar"):
        passo = int(tt * 2)
        tocada = _ruido(passo, 5) * len(TECLAS)
        fade = max(0.0, 1 - (tt * 2 - passo) * 1.2) if abs(TECLAS.index(tecla) - tocada) < 1.5 else 0.0
        v = fade if efeito == "acende-ao-tocar" else 1 - fade
        rgb = colorir(cx, v)
    else:
        rgb = colorir(cx, 1.0)

    escala = brilho / 5
    return tuple(int(max(0, min(1, c)) * 255 * escala) for c in rgb)
