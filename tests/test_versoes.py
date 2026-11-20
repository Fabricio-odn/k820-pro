from k820_pro import i18n
from k820_pro.gui.versoes import VERSOES, cor_da_tecla, fundo_da_tecla
from k820_pro.layout import TECLAS
from k820_pro.preferencias import Preferencias


def test_cinco_versoes_na_ordem():
    assert list(VERSOES) == ["neutro", "cinza-amarelo", "branco-roxo", "preto", "branco"]


def test_tipos_de_tecla():
    v = VERSOES["cinza-amarelo"]
    assert cor_da_tecla(v, "esc")[0] == (0xF2, 0xC2, 0x30)
    assert cor_da_tecla(v, "a")[0] == (0xC9, 0xCA, 0xCC)
    assert cor_da_tecla(v, "tab")[0] == (0x5A, 0x5C, 0x62)


def _luminancia(rgb):
    def canal(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (canal(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def test_contraste_legivel():
    for chave, v in VERSOES.items():
        for tec in TECLAS:
            fundo, texto = cor_da_tecla(v, tec.nome)
            a, b = sorted((_luminancia(fundo), _luminancia(texto)), reverse=True)
            assert (a + 0.05) / (b + 0.05) >= 3.0, (chave, tec.nome)


def test_toda_versao_traduzida():
    assert all({"en", "zh"} <= set(i18n.TRADUCOES[v.nome]) for v in VERSOES.values())


def test_cor_de_luz_tem_prioridade():
    v = VERSOES["cinza-amarelo"]
    assert fundo_da_tecla(v, "esc", {"esc": (1, 2, 3)}) == (1, 2, 3)
    assert fundo_da_tecla(v, "esc", {}) == (0xF2, 0xC2, 0x30)


def test_preferencia_aceita_as_versoes(tmp_path):
    arq = tmp_path / "p.json"
    arq.write_text('{"versao": "cinza-amarelo"}')
    assert Preferencias.carregar(arq).versao == "cinza-amarelo"


def test_contorno_de_selecao_visivel():
    from k820_pro.gui.versoes import cor_de_selecao
    for v in VERSOES.values():
        for tec in TECLAS:
            fundo = cor_da_tecla(v, tec.nome)[0]
            a, b = sorted((_luminancia(fundo), _luminancia(cor_de_selecao(fundo))), reverse=True)
            assert (a + 0.05) / (b + 0.05) >= 3.0, (v.nome, tec.nome)


def test_rotulo_bloqueado_legivel():
    from k820_pro.gui.versoes import cor_texto_bloqueado
    for v in VERSOES.values():
        fundo, texto = cor_da_tecla(v, "fn")
        apagado = cor_texto_bloqueado(fundo, texto)
        assert apagado != texto
        a, b = sorted((_luminancia(fundo), _luminancia(apagado)), reverse=True)
        assert (a + 0.05) / (b + 0.05) >= 2.5, v.nome
