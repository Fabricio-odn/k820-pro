"""Confere byte a byte que o que montamos é igual ao que o software oficial mandou."""
from datetime import datetime

from k820_pro import protocolo as P

from .capturas import enviados, transacao

SESSAO1 = "sessao1-luz-teclas-tft-sono-reset.log"


def test_iluminacao_igual_ao_oficial():
    # primeira troca de efeito da sessão: onda, vermelho, arco-íris, brilho 5, velocidade 3
    oficial = transacao(SESSAO1, P.CMD_ILUMINACAO, 0)
    il = P.Iluminacao("onda", (255, 0, 0), True, 5, 3, "esquerda")
    assert P.sequencia_iluminacao(il) == oficial


def test_iluminacao_respiracao_sem_arco_iris():
    oficial = transacao(SESSAO1, P.CMD_ILUMINACAO, 2)
    il = P.Iluminacao("respiracao", (255, 0, 0), False, 5, 3)
    assert P.sequencia_iluminacao(il) == oficial


def test_relogio_igual_ao_oficial():
    oficial = transacao(SESSAO1, P.CMD_RELOGIO, 0)
    assert P.sequencia_relogio(datetime(2026, 11, 20, 10, 13, 59)) == oficial


def test_tela_reconstruida_byte_a_byte():
    blocos = [d for _t, i, tp, d in enviados(SESSAO1) if i == "if2" and tp == "OUT"]
    tudo = b"".join(blocos)
    n = tudo[0]
    tempos = [b * 2 for b in tudo[1:1 + n]]
    tam = P.TELA_LADO * P.TELA_LADO * 2
    quadros = [tudo[256 + k * tam:256 + (k + 1) * tam] for k in range(n)]
    assert P.dados_tela(quadros, tempos) == blocos
    preambulo = transacao(SESSAO1, P.CMD_TELA, 0)[1]
    assert preambulo == P.inicio_tela(len(blocos))


SESSAO2 = "sessao2-teclas-luz-por-tecla-config-reset.log"
CAPS = 55  # índice do Caps Lock


def test_capslock_vira_a():
    assert P.sequencia_teclas({CAPS: P.acao_teclado(0, 0x04)}) == transacao(SESSAO2, P.CMD_TECLAS, 0)


def test_capslock_vira_aumentar_volume():
    assert P.sequencia_teclas({CAPS: P.acao_multimidia(0x00E9)}) == transacao(SESSAO2, P.CMD_TECLAS, 1)


def test_capslock_vira_ctrl():
    assert P.sequencia_teclas({CAPS: P.acao_teclado(0x01, 0)}) == transacao(SESSAO2, P.CMD_TECLAS, 2)


def test_luz_por_tecla():
    from k820_pro.layout import TECLAS
    indices = [t.indice for t in TECLAS]
    cores = {1: (255, 0, 0), 2: (0, 255, 0), 3: (0, 0, 255)}  # Esc, F1, F2
    seq = P.sequencia_luz_por_tecla(cores, indices)
    assert seq[:5] == transacao(SESSAO2, P.CMD_ILUMINACAO, 3)
    assert seq[5:] == transacao(SESSAO2, P.CMD_LUZ_TECLAS, 3)


def test_ajustes_sono_e_resposta():
    # 30 min (byte 6 = 3), nível 2, com o b5 = 1 que estava ligado naquele momento
    assert P.sequencia_ajustes(P.Ajustes("30", 2, 1, 1)) == transacao(SESSAO2, P.CMD_AJUSTES, 5)
    # 1 min, nível 5
    assert P.sequencia_ajustes(P.Ajustes("1", 5, 1, 1)) == transacao(SESSAO2, P.CMD_AJUSTES, 12)


def test_restauracao_de_fabrica():
    pac = [d for _t, i, tp, d in enviados(SESSAO2)
           if tp == "SETF" and not (d[0] == 4 and d[1] == 0xF5)]
    k = next(i for i, d in enumerate(pac) if d[0] == 4 and d[1] == P.CMD_RESTAURAR)
    assert P.sequencia_restaurar() == pac[k:]
