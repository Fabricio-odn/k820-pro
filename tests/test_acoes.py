import pytest

from k820_pro import protocolo as P
from k820_pro.acoes import acao
from k820_pro.estado import Estado
from k820_pro.cli import main


@pytest.mark.parametrize("texto,esperado", [
    ("a", bytes((2, 0, 0x04, 0))),
    ("ctrl_esq", bytes((2, 0x01, 0, 0))),
    ("ctrl_esq+c", bytes((2, 0x01, 0x06, 0))),
    ("ctrl_esq+shift_esq+esc", bytes((2, 0x03, 0x29, 0))),
    ("volume+", bytes((3, 0xE9, 0x00, 0))),
    ("web-parar", bytes((3, 0x26, 0x02, 0))),
    ("f13", bytes((2, 0, 0x68, 0))),
])
def test_acoes(texto, esperado):
    assert acao(texto) == esperado


def test_padrao_e_invalidas():
    assert acao("padrao") is None
    for ruim in ("xyz", "a+b", "fn"):
        with pytest.raises(ValueError):
            acao(ruim)


def test_estado_ida_e_volta(tmp_path):
    arq = tmp_path / "estado.json"
    e = Estado({"capslock": "ctrl_esq"}, {"esc": "ff0000"}, P.Ajustes("30", 1))
    e.salvar(arq)
    assert Estado.carregar(arq) == e
    assert Estado.carregar(tmp_path / "nada.json") == Estado()


def test_cli_recusa_antes_de_tocar_no_teclado(capsys, monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    assert main(["tecla", "fn", "a"]) == 1
    assert main(["tecla", "capslock", "xyz"]) == 1
    assert main(["cores", "esc=zzzzzz"]) == 1
    assert main(["ajustes"]) == 1
    assert not (tmp_path / "k820-pro").exists()


def test_estado_corrompido_vira_erro_claro(tmp_path):
    arq = tmp_path / "estado.json"
    for conteudo in ('{"teclas": {"capslock": "rm -rf"}}', '{"cores": {"esc": "zz"}}',
                     '{"ajustes": {"resposta": 99}}', '{"teclas": []}', "não é json"):
        arq.write_text(conteudo)
        with pytest.raises(ValueError):
            Estado.carregar(arq)


def test_imagem_gif_vira_quadros(tmp_path):
    PIL = pytest.importorskip("PIL.Image")
    from k820_pro import imagem
    quadros = [PIL.new("RGB", (300, 200), c) for c in ((255, 0, 0), (0, 0, 255))]
    arq = tmp_path / "t.gif"
    quadros[0].save(arq, save_all=True, append_images=quadros[1:], duration=[70, 60], loop=0)
    q, t = imagem.carregar(arq)
    assert len(q) == 2 and t == [70, 60] and len(q[0]) == 128 * 128 * 2
    assert q[0][:2] == P.rgb565(255, 0, 0)
    arq.write_bytes(b"lixo")
    with pytest.raises(ValueError):
        imagem.carregar(arq)


def test_apelidos_em_ingles(capsys):
    from k820_pro.cli import APELIDOS, montar_parser
    sub = next(a for a in montar_parser()._actions if a.dest == "comando")
    for en, pt in APELIDOS.items():
        assert sub.choices[en] is sub.choices[pt]
    assert main(["effects"]) == 0 and "onda" in capsys.readouterr().out
