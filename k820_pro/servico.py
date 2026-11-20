"""Operações de alto nível, usadas pela linha de comando e pela interface.

Cada função valida tudo antes de abrir o teclado, manda a sequência e só então
atualiza o estado guardado; se o envio falhar, o estado continua como estava.
"""
import dataclasses
from datetime import datetime

from . import acoes as A
from . import protocolo as P
from .dispositivo import ErroTeclado, conectar
from .i18n import t
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


def _enviar(cabo, sem_fio):
    """Manda a sequência do cabo ou a do dongle, conforme a conexão (funções sem argumento)."""
    with conectar() as tec:
        tec.executar(cabo() if tec.modo == "cabo" else sem_fio())
        return tec.modo


def aplicar_luz(il: P.Iluminacao):
    _enviar(lambda: P.sequencia_iluminacao(il), lambda: P.sem_fio_iluminacao(il))


def aplicar_cores(estado: Estado, cores: dict, brilho=P.BRILHO_MAX):
    """cores: {nome da tecla: "rrggbb"}; substitui as cores guardadas."""
    indices = {tecla(n).indice: cor_hex(c) for n, c in cores.items()}
    todas = [tec.indice for tec in TECLAS]
    _enviar(lambda: P.sequencia_luz_por_tecla(indices, todas, brilho),
            lambda: P.sem_fio_luz_por_tecla(indices, todas, brilho))
    estado.cores = {n: c.strip().lstrip("#").lower() for n, c in cores.items()}
    estado.salvar()


def aplicar_teclas(estado: Estado, mapa: dict):
    """mapa: {nome da tecla: nome da ação}; substitui o remapeamento inteiro."""
    tabela = {}
    for nome, acao in mapa.items():
        tec = tecla(nome)
        if tec.nome == "fn":
            raise ValueError("a tecla Fn não pode ser remapeada")
        b = A.acao(acao)
        if b is not None:
            tabela[tec.indice] = b

    def sem_fio():
        # pelo dongle vai uma tecla por vez, só as que mudaram; a de volta ao padrão
        # recebe o próprio código, como o software oficial faz
        quadros = []
        for nome in sorted(set(mapa) | set(estado.teclas)):
            tec = tecla(nome)
            novo = tabela.get(tec.indice)
            antigo = A.acao(estado.teclas[nome]) if nome in estado.teclas else None
            if antigo == novo:
                continue
            quadros += P.sem_fio_tecla(tec.indice, novo or P.acao_teclado(0, tec.codigo))
        return quadros

    _enviar(lambda: P.sequencia_teclas(tabela), sem_fio)
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
    _enviar(lambda: P.sequencia_ajustes(novos), lambda: P.sem_fio_ajustes(novos))
    estado.ajustes = novos
    estado.salvar()


def acertar_relogio(momento=None):
    momento = momento or datetime.now()
    _enviar(lambda: P.sequencia_relogio(momento), lambda: P.sem_fio_relogio(momento))
    return momento


def teclado_acordado():
    """Pelo dongle: True se o teclado responde, False se não. Pelo cabo (ou sem
    conexão nenhuma), None: não há o que perguntar."""
    try:
        with conectar() as tec:
            return tec.presente() if tec.modo == "dongle" else None
    except ErroTeclado:
        return None


def enviar_tela(caminho, modo="cortar", progresso=None):
    from . import imagem
    quadros, tempos = imagem.carregar(caminho, modo)
    blocos = P.dados_tela(quadros, tempos)
    with conectar() as tec:
        tec.enviar_tela(blocos, progresso)
    return len(quadros)


def restaurar(estado: Estado):
    def sem_fio():
        raise ErroTeclado(t("A restauração de fábrica só funciona pelo cabo USB (ou segure Fn + Espaço por 3 a 5 s)."))

    _enviar(P.sequencia_restaurar, sem_fio)
    estado.teclas, estado.cores, estado.ajustes = {}, {}, P.Ajustes()
    estado.salvar()
