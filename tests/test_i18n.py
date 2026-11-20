"""Todo texto passado a t("...") no projeto precisa ter tradução em inglês e chinês."""
import ast
from pathlib import Path

from k820_pro import i18n
from k820_pro.atalhos import FILEIRA_F, GERAIS, LUZES
from k820_pro import acoes, protocolo

PACOTE = Path(__file__).resolve().parent.parent / "k820_pro"


def _textos_do_codigo():
    for arq in PACOTE.rglob("*.py"):
        for no in ast.walk(ast.parse(arq.read_text())):
            if (isinstance(no, ast.Call) and getattr(no.func, "id", None) == "t" and no.args
                    and isinstance(no.args[0], ast.Constant) and isinstance(no.args[0].value, str)):
                yield arq.name, no.args[0].value


def _textos_de_dados():
    for grupo, itens in GERAIS:
        yield "atalhos", grupo
        for comb, func in itens:
            yield "atalhos", func
    for _c, win, mac in FILEIRA_F:
        yield "atalhos", win
        yield "atalhos", mac
    for _l, texto in LUZES:
        yield "atalhos", texto
    yield from (("efeitos", e) for e in protocolo.EFEITOS)
    yield from (("direcoes", d) for d in protocolo.DIRECOES)
    yield from (("multimidia", m) for m in acoes.MULTIMIDIA)


def test_tudo_traduzido():
    faltando = sorted({(a, txt) for a, txt in [*_textos_do_codigo(), *_textos_de_dados()]
                       if not {"en", "zh"} <= set(i18n.TRADUCOES.get(txt, {}))})
    assert not faltando, "\n".join(f"{a}: {txt!r}" for a, txt in faltando)


def test_campos_iguais_nas_traducoes():
    import string
    campos = lambda s: {f for _, f, _, _ in string.Formatter().parse(s) if f}
    for pt, trad in i18n.TRADUCOES.items():
        for idioma, texto in trad.items():
            assert campos(texto) == campos(pt), (pt, idioma)


def test_troca_de_idioma():
    i18n.definir("en")
    assert i18n.t("Aplicar") == "Apply"
    i18n.definir("zh")
    assert i18n.t("Enviado: {n} quadro(s)", n=3) == "已发送：3 帧"
    i18n.definir("pt")
    assert i18n.t("Aplicar") == "Aplicar"
