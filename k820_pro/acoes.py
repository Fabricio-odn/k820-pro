"""Nomes das ações que uma tecla pode receber no remapeamento.

Formatos (vistos nas capturas do software oficial):
- tecla comum ou atalho: [02, modificadores, código HID, 0], como "a", "ctrl_esq+c";
- só modificador: [02, bit do modificador, 0, 0], como "ctrl_esq";
- multimídia: [03, uso consumer em 2 bytes little-endian, 0], como "volume+".
"""
from . import protocolo as P
from .layout import TECLAS

# Bits do byte de modificadores (padrão HID).
MODIFICADORES = {
    "ctrl_esq": 0x01, "shift_esq": 0x02, "alt_esq": 0x04, "win": 0x08,
    "ctrl_dir": 0x10, "shift_dir": 0x20, "alt_dir": 0x40, "win_dir": 0x80,
}

# Teclas do próprio teclado (menos modificadores e Fn) e algumas que ele não tem.
TECLAS_HID = {t.nome: t.codigo for t in TECLAS if t.nome not in MODIFICADORES and t.nome != "fn"}
TECLAS_HID.update({
    "insert": 0x49, "end": 0x4D, "printscreen": 0x46, "scrolllock": 0x47, "pause": 0x48,
    "menu": 0x65, "numlock": 0x53,
    **{f"f{n}": 0x68 + n - 13 for n in range(13, 25)},
})

MULTIMIDIA = {
    "volume+": 0x00E9, "volume-": 0x00EA, "mudo": 0x00E2,
    "play-pause": 0x00CD, "proxima": 0x00B5, "anterior": 0x00B6, "parar": 0x00B7,
    "brilho+": 0x006F, "brilho-": 0x0070,
    "email": 0x018A, "calculadora": 0x0192, "meu-computador": 0x0194, "navegador": 0x0196,
    "web-pesquisar": 0x0221, "web-inicio": 0x0223, "web-voltar": 0x0224, "web-avancar": 0x0225,
    "web-parar": 0x0226, "web-atualizar": 0x0227, "web-favoritos": 0x022A,
}

PADRAO = "padrao"


def acao(texto):
    """Converte o nome de uma ação nos 4 bytes da tabela (None = função de fábrica)."""
    t = texto.strip().lower()
    if t == PADRAO:
        return None
    if t in MULTIMIDIA:
        return P.acao_multimidia(MULTIMIDIA[t])
    mods, codigo = 0, 0
    for parte in t.split("+"):
        if parte in MODIFICADORES:
            mods |= MODIFICADORES[parte]
        elif parte in TECLAS_HID and codigo == 0:
            codigo = TECLAS_HID[parte]
        else:
            raise ValueError(f"ação desconhecida: {parte!r} (veja `k820 acoes`)")
    return P.acao_teclado(mods, codigo)
