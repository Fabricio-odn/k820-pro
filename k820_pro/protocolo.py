"""Montagem dos pacotes de configuração do Ajazz AK820 Pro (0c45:800a).

Só monta bytes; quem fala com o teclado é o módulo `dispositivo`.

O canal é o feature report de 64 bytes da interface 3 (usage page 0xff13). O
descritor dessa interface não declara report IDs, mas o firmware usa o primeiro
byte de cada pacote como se fosse um: o kernel o manda no wValue do SET_REPORT
e também no corpo do pacote, igual ao software original.

Formato dos pacotes de controle: [0x04, comando, b2, 0, 0, 0, 0, 0, b8, 0...].
Uma operação é uma sequência: INICIO, preâmbulo do comando, dados, e um
fechamento (FIM ou SALVAR, conforme o comando).

Origem dos bytes: capturas do software oficial (DeviceDriver.exe 1.0.0.5)
rodando no Wine, com os pacotes registrados via LD_PRELOAD (veja
docs/protocolo.md e captures/). O projeto github.com/gohv/EPOMAKER-Ajazz-AK820-Pro
(MIT) foi o ponto de partida.
"""
from dataclasses import dataclass
from datetime import datetime

TAM_PACOTE = 64
REPORT_ID = 0x04

CMD_INICIO = 0x18
CMD_FIM = 0xF0
CMD_ILUMINACAO = 0x13
CMD_AJUSTES = 0x17
CMD_RELOGIO = 0x28
CMD_TECLAS = 0x11       # tabela de remapeamento da camada normal
CMD_TECLAS_FN = 0x27    # tabela da camada Fn (só vista zerada, na restauração)
CMD_LUZ_TECLAS = 0x23   # cor de cada tecla no modo de luz personalizada
CMD_RESTAURAR = 0x19    # abre a restauração de fábrica, no lugar do INICIO
CMD_LIMPAR = 0x15       # vem logo depois do 0x19, com 8 pacotes zerados
CMD_SALVAR = 0x02
CMD_TELA = 0x72

# Tela: 128x128, RGB565 little-endian. Cabeçalho de 256 bytes: número de quadros
# e o tempo de cada um em unidades de 2 ms; o resto é 0xff.
TELA_LADO = 128
TELA_CABECALHO = 256
TELA_MAX_QUADROS = 140
TELA_BLOCO = 4096

BRILHO_MAX = 5
VELOCIDADE_MAX = 5

# Nome na linha de comando -> código do efeito no firmware.
EFEITOS = {
    "desligado": 0x00,
    "estatico": 0x01,
    "acende-ao-tocar": 0x02,
    "apaga-ao-tocar": 0x03,
    "cintilante": 0x04,
    "chuva": 0x05,
    "colorido": 0x06,
    "respiracao": 0x07,
    "espectro": 0x08,
    "do-centro": 0x09,
    "rolagem": 0x0A,
    "onda": 0x0B,
    "giro": 0x0C,
    "explosao": 0x0D,
    "lancamento": 0x0E,
    "ondulacao": 0x0F,
    "fluxo": 0x10,
    "pulsar": 0x11,
    "inclinado": 0x12,
    "vaivem": 0x13,
}

# Efeitos que aceitam direção, e quais.
DIRECOES_POR_EFEITO = {
    "rolagem": ("cima", "baixo"),
    "onda": ("esquerda", "direita"),
    "fluxo": ("esquerda", "direita"),
    "inclinado": ("esquerda", "direita"),
}
DIRECOES = {"esquerda": 0, "baixo": 1, "cima": 2, "direita": 3}

# Configurações (comando 0x17). Tempo até dormir -> código no byte 6.
SONO = {"nunca": 0, "1": 1, "5": 2, "30": 3}
RESPOSTA_NIVEIS = range(1, 6)  # tempo de resposta das teclas, byte 8 (nível 1 = ~2-3 ms no cabo)
EFEITO_PERSONALIZADO = 0x80    # efeito de luz que usa as cores da tabela 0x23

# Tabelas de 144 entradas de 4 bytes (576 bytes = 9 pacotes); a última entrada termina em AA 55.
TABELA_ENTRADAS = 144
TABELA_PACOTES = 9


@dataclass(frozen=True)
class Iluminacao:
    efeito: str = "estatico"
    cor: tuple = (255, 0, 0)
    arco_iris: bool = False
    brilho: int = BRILHO_MAX
    velocidade: int = 3
    direcao: str = "esquerda"

    def validar(self):
        if self.efeito not in EFEITOS:
            raise ValueError(f"efeito desconhecido: {self.efeito}")
        if len(self.cor) != 3 or any(not 0 <= c <= 255 for c in self.cor):
            raise ValueError("a cor precisa de 3 valores de 0 a 255")
        if not 0 <= self.brilho <= BRILHO_MAX:
            raise ValueError(f"brilho vai de 0 a {BRILHO_MAX}")
        if not 0 <= self.velocidade <= VELOCIDADE_MAX:
            raise ValueError(f"velocidade vai de 0 a {VELOCIDADE_MAX}")
        if self.direcao not in DIRECOES:
            raise ValueError(f"direção desconhecida: {self.direcao}")
        aceitas = DIRECOES_POR_EFEITO.get(self.efeito)
        if aceitas and self.direcao not in aceitas:
            raise ValueError(f"o efeito {self.efeito} aceita só: {', '.join(aceitas)}")


def pacote_controle(comando, b2=0, b8=0):
    p = bytearray(TAM_PACOTE)
    p[0] = REPORT_ID
    p[1] = comando
    p[2] = b2
    p[8] = b8
    return bytes(p)


def inicio():
    return pacote_controle(CMD_INICIO)


def fim():
    return pacote_controle(CMD_FIM)


def salvar():
    return pacote_controle(CMD_SALVAR, 0x00, 0x00)


def pacote_iluminacao(il: Iluminacao):
    """Pacote de dados do efeito. O byte 0 é o código do efeito (vai como report ID).

    Como no software original, "desligado" vira "acende-ao-tocar" com brilho 0, e
    "estatico" vira "respiracao" com velocidade 0.
    """
    il.validar()
    codigo, velocidade, brilho = EFEITOS[il.efeito], il.velocidade, il.brilho
    if il.efeito == "desligado":
        codigo, velocidade, brilho = EFEITOS["acende-ao-tocar"], 0, 0
    elif il.efeito == "estatico":
        codigo, velocidade = EFEITOS["respiracao"], 0
    p = bytearray(TAM_PACOTE)
    p[0] = codigo
    p[1], p[2], p[3] = il.cor
    p[8] = int(il.arco_iris)
    p[9] = brilho
    p[10] = velocidade
    p[11] = DIRECOES[il.direcao]
    p[14], p[15] = 0xAA, 0x55
    return bytes(p)


def sequencia_iluminacao(il: Iluminacao):
    return [inicio(), pacote_controle(CMD_ILUMINACAO, 0x00, 0x01), pacote_iluminacao(il), salvar(), fim()]


@dataclass(frozen=True)
class Ajustes:
    """Os campos do pacote de configurações. Os padrões são os da restauração de fábrica.

    b1 e b5 aparecem nas capturas com valores 1 e 0/1, sem significado conhecido; são
    repassados como foram observados.
    """
    sono: str = "5"
    resposta: int = 2
    b1: int = 1
    b5: int = 0

    def validar(self):
        if self.sono not in SONO:
            raise ValueError(f"tempo até dormir inválido: {self.sono} (use {', '.join(SONO)})")
        if self.resposta not in RESPOSTA_NIVEIS:
            raise ValueError("o tempo de resposta vai do nível 1 ao 5")


def sequencia_ajustes(aj: Ajustes):
    aj.validar()
    dados = bytearray(TAM_PACOTE)
    dados[1] = aj.b1
    dados[5] = aj.b5
    dados[6] = SONO[aj.sono]
    dados[8] = aj.resposta
    dados[62], dados[63] = 0xAA, 0x55
    return [inicio(), pacote_controle(CMD_AJUSTES, 0x01, 0x01), bytes(dados), salvar()]


def sequencia_relogio(momento: datetime):
    if not 2000 <= momento.year <= 2255:
        raise ValueError("ano fora do intervalo aceito pelo teclado (2000 a 2255)")
    dados = bytearray(TAM_PACOTE)
    dados[1] = 0x01
    dados[2] = 0x5A
    dados[3] = momento.year - 2000
    dados[4] = momento.month
    dados[5] = momento.day
    dados[6] = momento.hour
    dados[7] = momento.minute
    dados[8] = momento.second
    dados[10] = momento.isoweekday() % 7  # dia da semana, domingo = 0
    dados[62], dados[63] = 0xAA, 0x55
    return [inicio(), pacote_controle(CMD_RELOGIO, 0x00, 0x01), bytes(dados), salvar()]


def dados_tela(quadros, tempos_ms):
    """Junta os quadros (bytes RGB565, 32768 cada) com o cabeçalho e completa com 0xff
    até um múltiplo de 4096. Devolve a lista de blocos de 4096 bytes."""
    n = len(quadros)
    if not 1 <= n <= TELA_MAX_QUADROS:
        raise ValueError(f"a tela aceita de 1 a {TELA_MAX_QUADROS} quadros")
    if len(tempos_ms) != n:
        raise ValueError("é preciso um tempo por quadro")
    tam = TELA_LADO * TELA_LADO * 2
    cab = bytearray(b"\xff" * TELA_CABECALHO)
    cab[0] = n
    for i, ms in enumerate(tempos_ms):
        cab[1 + i] = max(1, min(255, round(ms / 2)))
    corpo = bytearray(cab)
    for q in quadros:
        if len(q) != tam:
            raise ValueError(f"quadro com {len(q)} bytes, esperado {tam}")
        corpo += q
    corpo += b"\xff" * (-len(corpo) % TELA_BLOCO)
    return [bytes(corpo[i:i + TELA_BLOCO]) for i in range(0, len(corpo), TELA_BLOCO)]


def inicio_tela(n_blocos):
    """Preâmbulo do envio para a tela: 0x72 0x02 e o número de blocos de 4096 bytes."""
    if not 1 <= n_blocos <= 0xFFFF:
        raise ValueError("número de blocos fora do intervalo")
    p = bytearray(pacote_controle(CMD_TELA, 0x02))
    p[8] = n_blocos & 0xFF
    p[9] = n_blocos >> 8  # observado só até 161 blocos (cabe no byte 8)
    return bytes(p)


def rgb565(r, g, b):
    v = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
    return bytes((v & 0xFF, v >> 8))


def tabela(entradas):
    """Monta os 576 bytes de uma tabela a partir de {índice: 4 bytes}; o resto fica zerado."""
    t = bytearray(TABELA_ENTRADAS * 4)
    for indice, valor in entradas.items():
        if not 0 <= indice < TABELA_ENTRADAS - 1:
            raise ValueError(f"índice de tecla fora da tabela: {indice}")
        if len(valor) != 4:
            raise ValueError("cada entrada da tabela tem 4 bytes")
        t[indice * 4:indice * 4 + 4] = valor
    t[-2:] = b"\xaa\x55"
    return bytes(t)


def sequencia_tabela(comando, dados_tabela):
    pacotes = [dados_tabela[i:i + TAM_PACOTE] for i in range(0, len(dados_tabela), TAM_PACOTE)]
    return [inicio(), pacote_controle(comando, 0x00, TABELA_PACOTES), *pacotes, salvar(), fim()]


# Remapeamento: cada entrada é [tipo, a, b, 0]. Tudo zerado = função de fábrica.
TIPO_TECLADO = 0x02     # [02, modificadores, código HID, 0]
TIPO_MULTIMIDIA = 0x03  # [03, uso consumer (little-endian, 2 bytes), 0]


def acao_teclado(modificadores=0, codigo=0):
    return bytes((TIPO_TECLADO, modificadores, codigo, 0))


def acao_multimidia(uso):
    return bytes((TIPO_MULTIMIDIA, uso & 0xFF, uso >> 8, 0))


def sequencia_teclas(mapa):
    """mapa: {índice da tecla: 4 bytes da ação}. Teclas fora do mapa voltam ao padrão."""
    return sequencia_tabela(CMD_TECLAS, tabela(mapa))


def sequencia_luz_por_tecla(cores, indices, brilho=BRILHO_MAX):
    """Liga o efeito personalizado e manda a cor de cada tecla.

    cores: {índice: (r, g, b)}; indices: todos os índices de teclas que existem (o software
    oficial manda o índice em cada entrada que tem tecla, mesmo sem cor).
    """
    if not 0 <= brilho <= BRILHO_MAX:
        raise ValueError(f"brilho vai de 0 a {BRILHO_MAX}")
    efeito = bytearray(TAM_PACOTE)
    efeito[0] = EFEITO_PERSONALIZADO
    efeito[9] = brilho
    efeito[14], efeito[15] = 0xAA, 0x55
    entradas = {}
    for i in indices:
        r, g, b = cores.get(i, (0, 0, 0))
        entradas[i] = bytes((i, r, g, b))
    luz = [inicio(), pacote_controle(CMD_ILUMINACAO, 0x00, 0x01), bytes(efeito), salvar(), fim()]
    return luz + sequencia_tabela(CMD_LUZ_TECLAS, tabela(entradas))


def sequencia_restaurar():
    """Restauração de fábrica, como o software oficial faz: limpa e regrava os padrões."""
    limpar = [pacote_controle(CMD_RESTAURAR), pacote_controle(CMD_LIMPAR, 0x00, 0x08)]
    zerada = bytearray(8 * TAM_PACOTE)
    zerada[-2:] = b"\xaa\x55"
    limpar += [bytes(zerada[i:i + TAM_PACOTE]) for i in range(0, len(zerada), TAM_PACOTE)] + [salvar()]
    vazia = tabela({})
    padrao_luz = Iluminacao("onda", (255, 0, 0), True, BRILHO_MAX, 3, "esquerda")
    return (limpar
            + sequencia_tabela(CMD_TECLAS, vazia)
            + sequencia_tabela(CMD_TECLAS_FN, vazia)
            + sequencia_iluminacao(padrao_luz)
            + sequencia_ajustes(Ajustes()))


# --- Dongle 2.4 GHz (0c45:fdfd, interface 3) -------------------------------------------
# Output reports de 32 bytes: [comando, tamanho, posição, até 28 bytes de dados, soma],
# onde o último byte é a soma dos 31 anteriores. O teclado devolve um eco de cada um
# (mesmo comando e posição) na mesma interface. Os dados são os mesmos do cabo:
# o pacote de luz, a tabela de 576 bytes, os campos de ajustes e do relógio.
# Não há tela nem restauração de fábrica pelo dongle (não observadas).
SEM_FIO_TAM = 32
SEM_FIO_DADOS = 28
SF_INFO, SF_TECLA, SF_LUZ, SF_AJUSTES, SF_RELOGIO, SF_TABELA_LUZ, SF_PRESENCA = (
    0x02, 0x03, 0x05, 0x07, 0x0C, 0x14, 0x20)


def quadro_sem_fio(comando, posicao=0, dados=b""):
    if len(dados) > SEM_FIO_DADOS:
        raise ValueError("dados demais para um pacote do dongle")
    q = bytearray(SEM_FIO_TAM)
    q[0], q[1], q[2] = comando, len(dados), posicao
    q[3:3 + len(dados)] = dados
    q[-1] = sum(q[:-1]) & 0xFF
    return bytes(q)


SEM_FIO_INFO = quadro_sem_fio(SF_INFO)


def _curto(dados64):
    """Os 14 primeiros bytes de um pacote de dados do cabo, com o AA 55 logo depois."""
    return bytes(dados64[:14]) + b"\xaa\x55"


def sem_fio_iluminacao(il: Iluminacao):
    return [quadro_sem_fio(SF_LUZ, 0, pacote_iluminacao(il)[:16])]


def sem_fio_relogio(momento: datetime):
    return [quadro_sem_fio(SF_RELOGIO, 0, _curto(sequencia_relogio(momento)[2]))]


def sem_fio_ajustes(aj: Ajustes):
    return [quadro_sem_fio(SF_AJUSTES, 0, _curto(sequencia_ajustes(aj)[2]))]


def sem_fio_tecla(indice, entrada):
    """Uma tecla da tabela de remapeamento: posição = índice da tecla, 4 bytes da ação."""
    if not 0 <= indice < TABELA_ENTRADAS - 1 or len(entrada) != 4:
        raise ValueError("tecla ou ação inválida")
    return [quadro_sem_fio(SF_TECLA, indice, entrada)]


def sem_fio_luz_por_tecla(cores, indices, brilho=BRILHO_MAX):
    cabo = sequencia_luz_por_tecla(cores, indices, brilho)
    efeito = quadro_sem_fio(SF_LUZ, 0, cabo[2][:16])
    tabela = b"".join(cabo[7:7 + TABELA_PACOTES])
    pedacos = [tabela[i:i + SEM_FIO_DADOS] for i in range(0, len(tabela), SEM_FIO_DADOS)]
    return [efeito] + [quadro_sem_fio(SF_TABELA_LUZ, n, p) for n, p in enumerate(pedacos)]
