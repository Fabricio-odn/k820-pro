"""Lê os registros do tráfego do software oficial (captures/*.log).

Cada linha: <tempo> if<n> <SETF|GETF|OUT|IN> <tamanho> <hex>. Nos SETF e OUT o
primeiro byte é o report ID 0 que o Wine põe na frente; aqui ele é removido.
"""
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent / "captures"


def ler(nome):
    eventos = []
    for linha in (PASTA / nome).read_text().splitlines():
        t, iface, tipo, _tam, hexa = linha.split()
        dados = bytes.fromhex(hexa)
        if tipo in ("SETF", "GETF", "OUT"):
            dados = dados[1:]
        eventos.append((float(t), iface, tipo, dados))
    return eventos


def enviados(nome):
    """Só o que o software mandou ao teclado: feature reports da interface 3 e blocos da 2."""
    return [(t, i, tp, d) for t, i, tp, d in ler(nome) if tp in ("SETF", "OUT")]


def transacao(nome, comando, n=0):
    """A n-ésima transação de feature reports cujo preâmbulo é `comando`, de INICIO até antes
    do próximo INICIO (ou do fim)."""
    # 0xf5 é a consulta que o software repete enquanto está aberto; não faz parte das escritas
    pac = [d for _t, i, tp, d in enviados(nome) if tp == "SETF" and not (d[0] == 4 and d[1] == 0xF5)]
    inicios = [k for k, d in enumerate(pac) if d[0] == 4 and d[1] in (0x18, 0x19)]
    achadas = []
    for a, b in zip(inicios, inicios[1:] + [len(pac)]):
        trecho = pac[a:b]
        if len(trecho) > 1 and trecho[1][0] == 4 and trecho[1][1] == comando:
            achadas.append(trecho)
    return achadas[n]
