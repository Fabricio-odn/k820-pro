"""Operações de alto nível, usadas pela linha de comando e pela interface.

Cada função valida tudo antes de abrir o teclado, manda a sequência e só então
atualiza o estado guardado; se o envio falhar, o estado continua como estava.
"""
import dataclasses
from datetime import datetime

from . import acoes as A
from . import protocolo as P
from .dispositivo import Teclado
from .estado import Estado
from .layout import POR_NOME, TECLAS


def cor_hex(texto):
    t = texto.strip().lstrip("#").lower()
    if len(t) != 6 or any(c not in "0123456789abcdef" for c in t):
        raise ValueError(f"cor inválida: {texto!r} (use rrggbb, como ff0000)")
    return tuple(int(t[i:i + 2], 16) for i in (0, 2, 4))


def tecla(nome):
    if nome not in POR_NOME:
        raise ValueError(f"tecla desconhecida: {nome!r}")
    return POR_NOME[nome]


def _enviar(seq):
    with Teclado() as t:
        t.executar(seq)


def aplicar_luz(il: P.Iluminacao):
    _enviar(P.sequencia_iluminacao(il))


def aplicar_cores(estado: Estado, cores: dict, brilho=P.BRILHO_MAX):
    """cores: {nome da tecla: "rrggbb"}; substitui as cores guardadas."""
    indices = {tecla(n).indice: cor_hex(c) for n, c in cores.items()}
    _enviar(P.sequencia_luz_por_tecla(indices, [t.indice for t in TECLAS], brilho))
    estado.cores = {n: c.strip().lstrip("#").lower() for n, c in cores.items()}
    estado.salvar()


def aplicar_teclas(estado: Estado, mapa: dict):
    """mapa: {nome da tecla: nome da ação}; substitui o remapeamento inteiro."""
    tabela = {}
    for nome, acao in mapa.items():
        t = tecla(nome)
        if t.nome == "fn":
            raise ValueError("a tecla Fn não pode ser remapeada")
        b = A.acao(acao)
        if b is not None:
            tabela[t.indice] = b
    _enviar(P.sequencia_teclas(tabela))
    estado.teclas = {n: a.lower() for n, a in mapa.items() if A.acao(a) is not None}
    estado.salvar()


def remapear(estado: Estado, nome, acao):
    novo = dict(estado.teclas)
    if A.acao(acao) is None:
        novo.pop(nome, None)
    else:
        novo[nome] = acao
    aplicar_teclas(estado, novo)


def aplicar_ajustes(estado: Estado, **mudancas):
    novos = dataclasses.replace(estado.ajustes, **mudancas)
    _enviar(P.sequencia_ajustes(novos))
    estado.ajustes = novos
    estado.salvar()


def acertar_relogio(momento=None):
    momento = momento or datetime.now()
    _enviar(P.sequencia_relogio(momento))
    return momento


def enviar_tela(caminho, modo="cortar", progresso=None):
    from . import imagem
    quadros, tempos = imagem.carregar(caminho, modo)
    blocos = P.dados_tela(quadros, tempos)
    with Teclado() as t:
        t.enviar_tela(blocos, progresso)
    return len(quadros)


def restaurar(estado: Estado):
    _enviar(P.sequencia_restaurar())
    estado.teclas, estado.cores, estado.ajustes = {}, {}, P.Ajustes()
    estado.salvar()
