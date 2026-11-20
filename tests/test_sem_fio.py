"""Pacotes do dongle 2.4 GHz conferidos byte a byte com a gravação do software oficial."""
from datetime import datetime

from k820_pro import protocolo as P
from k820_pro.layout import TECLAS

from .capturas import ler

SESSAO3 = "sessao3-dongle.log"


def _enviados():
    return [d for _t, i, tp, d in ler(SESSAO3) if tp == "OUT"]


def _primeiro(cmd, **campos):
    for q in _enviados():
        if q[0] == cmd and all(q[3 + int(k[1:])] == v for k, v in campos.items()):
            return q
    raise AssertionError(f"pacote 0x{cmd:02x} não achado")


def test_soma_de_verificacao():
    for q in _enviados():
        assert P.quadro_sem_fio(q[0], q[2], q[3:3 + q[1]]) == q


def test_identificacao():
    assert P.SEM_FIO_INFO == _enviados()[0]


def test_iluminacao():
    il = P.Iluminacao("onda", (255, 0, 0), True, 5, 3, "esquerda")
    assert P.sem_fio_iluminacao(il) == [_primeiro(0x05, b0=0x0B)]


def test_relogio():
    assert P.sem_fio_relogio(datetime(2026, 11, 20, 12, 5, 50)) == [_enviados()[2]]


def test_ajustes():
    assert P.sem_fio_ajustes(P.Ajustes("1", 2, 1, 0)) == [_primeiro(0x07, b8=2)]
    assert P.sem_fio_ajustes(P.Ajustes("1", 1, 1, 0)) == [_primeiro(0x07, b8=1)]


def test_tecla():
    assert P.sem_fio_tecla(55, P.acao_teclado(0, 0x04)) == [_primeiro(0x03, b2=0x04)]
    assert P.sem_fio_tecla(55, P.acao_teclado(0, 0x39)) == [_primeiro(0x03, b2=0x39)]


def test_luz_por_tecla():
    enviados = _enviados()
    inicio = [i for i, q in enumerate(enviados) if q[0] == 0x05 and q[3] == 0x80][1]
    oficial = [q for q in enviados[inicio:] if q[0] in (0x05, 0x14)][:22]
    cores = {1: (255, 0, 0)}  # Esc vermelho
    assert P.sem_fio_luz_por_tecla(cores, [t.indice for t in TECLAS]) == oficial


class _Falso:
    modo = "dongle"

    def __init__(self):
        self.enviados = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def executar(self, quadros):
        self.enviados += quadros


def test_remapear_pelo_dongle_manda_so_o_que_mudou(tmp_path, monkeypatch):
    from k820_pro import servico as S
    from k820_pro.estado import Estado
    falso = _Falso()
    monkeypatch.setattr(S, "conectar", lambda: falso)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    estado = Estado({"esc": "a"})
    S.remapear(estado, "capslock", "ctrl_esq")
    assert falso.enviados == P.sem_fio_tecla(55, P.acao_teclado(0x01, 0))
    falso.enviados.clear()
    S.remapear(estado, "capslock", "padrao")  # volta com o próprio código, 0x39
    assert falso.enviados == P.sem_fio_tecla(55, P.acao_teclado(0, 0x39))
    assert estado.teclas == {"esc": "a"}


def test_tela_e_restaurar_recusados_pelo_dongle(tmp_path, monkeypatch):
    import pytest
    from k820_pro import servico as S
    from k820_pro.dispositivo import ErroTeclado, TecladoSemFio
    from k820_pro.estado import Estado
    monkeypatch.setattr(S, "conectar", lambda: _Falso())
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    with pytest.raises(ErroTeclado):
        S.restaurar(Estado())
    with pytest.raises(ErroTeclado):
        TecladoSemFio.enviar_tela(None, [])
