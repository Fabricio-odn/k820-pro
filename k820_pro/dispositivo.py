"""Acesso ao AK820 Pro pelo hidraw da interface 3 (canal de configuração).

O teclado é achado pelo HID_ID no uevent, nunca por número fixo de hidraw.
Só funciona pelo cabo: pelo dongle 2.4G (0c45:fdfd) o protocolo é outro e
ainda não foi estudado.
"""
import fcntl
import os
import select
import time
from pathlib import Path

from . import protocolo as P
from .i18n import t
from .protocolo import REPORT_ID, TAM_PACOTE

HID_ID = "0003:00000C45:0000800A"
HID_ID_DONGLE = "0003:00000C45:0000FDFD"
INTERFACE_DONGLE = 3
ESPERA_ECO = 1.5  # segundos para o teclado responder pelo dongle
INTERFACE_CONFIG = 3
INTERFACE_TELA = 2
CONFIRMA_BLOCO = bytes((0x01, 0x5A, 0x02))  # resposta da interface 2 a cada bloco
ESPERA_BLOCO = 2.0
PAUSA = 0.01          # entre pacotes
PAUSA_FINAL = 0.1     # depois de cada sequência


class ErroTeclado(Exception):
    pass


def _ioc(direcao, nr, tamanho):
    return (direcao << 30) | (tamanho << 16) | (ord("H") << 8) | nr


def HIDIOCSFEATURE(n):
    return _ioc(3, 0x06, n)


def HIDIOCGFEATURE(n):
    return _ioc(3, 0x07, n)


def achar_hidraw(classe=Path("/sys/class/hidraw"), interface=INTERFACE_CONFIG, hid_id=HID_ID):
    """Caminho do hidraw da interface pedida do teclado, ou erro se não estiver ligado."""
    try:
        itens = sorted(Path(classe).iterdir())
    except OSError:
        itens = []
    for item in itens:
        disp = item / "device"
        try:
            if f"HID_ID={hid_id}" not in (disp / "uevent").read_text().split():
                continue
            num = int((disp.resolve().parent / "bInterfaceNumber").read_text(), 16)
        except (OSError, ValueError):
            continue
        if num == interface:
            return f"/dev/{item.name}"
    raise ErroTeclado(t("Teclado não encontrado. Ligue o AK820 Pro pelo cabo USB ou pelo dongle 2.4 GHz."))


def modo_conexao(classe=Path("/sys/class/hidraw")):
    """"cabo", "dongle" ou None. Com os dois ligados, vale o cabo."""
    for modo, hid_id, interface in (("cabo", HID_ID, INTERFACE_CONFIG),
                                    ("dongle", HID_ID_DONGLE, INTERFACE_DONGLE)):
        try:
            achar_hidraw(classe, interface, hid_id)
            return modo
        except ErroTeclado:
            pass
    return None


def conectar():
    """Abre o teclado pelo cabo ou, sem ele, pelo dongle 2.4 GHz."""
    if modo_conexao() == "dongle":
        return TecladoSemFio()
    return Teclado()


def versao_firmware(classe=Path("/sys/class/hidraw")):
    """bcdDevice do teclado como texto ("0110" -> "1.10"), ou None se não estiver ligado."""
    try:
        caminho = Path(classe) / Path(achar_hidraw(classe)).name / "device"
        bcd = (caminho.resolve().parent.parent / "bcdDevice").read_text().strip()
    except (ErroTeclado, OSError):
        return None
    return f"{int(bcd[:2])}.{bcd[2:]}" if len(bcd) == 4 and bcd.isdigit() else None


def preparar_buffer(pacote: bytes) -> bytes:
    """Buffer para o HIDIOCSFEATURE.

    O kernel trata o primeiro byte como report ID e, se ele for 0, o descarta.
    Por isso pacotes que começam com 0x00 ganham um 0x00 extra na frente.
    """
    if len(pacote) != TAM_PACOTE:
        raise ValueError(f"pacote com {len(pacote)} bytes, esperado {TAM_PACOTE}")
    return pacote if pacote[0] != 0 else b"\x00" + pacote


class Teclado:
    modo = "cabo"

    def __init__(self, caminho=None):
        self.caminho = caminho or achar_hidraw()
        try:
            self.fd = os.open(self.caminho, os.O_RDWR)
        except PermissionError:
            raise ErroTeclado(t("sem permissão em {c}. Instale a regra udev: sudo bash scripts/instalar-udev.sh",
                                c=self.caminho)) from None

    def fechar(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.fechar()

    def enviar(self, pacote: bytes):
        buf = bytearray(preparar_buffer(pacote))
        try:
            fcntl.ioctl(self.fd, HIDIOCSFEATURE(len(buf)), buf)
        except OSError as e:
            raise ErroTeclado(f"falha ao enviar o pacote 0x{pacote[1]:02x}: {e}") from None
        if pacote[0] == REPORT_ID:
            # GET_REPORT depois de cada pacote de controle: o firmware precisa
            # dele para avançar. A resposta não importa e pode falhar.
            resposta = bytearray(TAM_PACOTE)
            resposta[0] = REPORT_ID
            try:
                fcntl.ioctl(self.fd, HIDIOCGFEATURE(TAM_PACOTE), resposta)
            except OSError:
                pass
        time.sleep(PAUSA)

    def executar(self, sequencia):
        for pacote in sequencia:
            self.enviar(pacote)
        time.sleep(PAUSA_FINAL)

    def enviar_tela(self, blocos, progresso=None):
        """Manda os blocos de 4096 bytes pela interface 2, esperando a confirmação de cada um.

        Sequência do software oficial: INICIO, 0x72 0x02 com o número de blocos,
        os blocos (output report de 4096 bytes, confirmados com 01 5a 02) e SALVAR.
        """
        caminho = achar_hidraw(interface=INTERFACE_TELA)
        try:
            fd = os.open(caminho, os.O_RDWR | os.O_NONBLOCK)
        except PermissionError:
            raise ErroTeclado(t("sem permissão em {c}. Instale a regra udev: sudo bash scripts/instalar-udev.sh", c=caminho)) from None
        try:
            _descartar(fd)
            self.enviar(P.inicio())
            self.enviar(P.inicio_tela(len(blocos)))
            for i, bloco in enumerate(blocos):
                os.write(fd, b"\x00" + bloco)
                _esperar_confirmacao(fd, i)
                if progresso:
                    progresso(i + 1, len(blocos))
            self.enviar(P.salvar())
        finally:
            os.close(fd)
        time.sleep(PAUSA_FINAL)


def _descartar(fd):
    while select.select([fd], [], [], 0)[0]:
        try:
            os.read(fd, 64)
        except BlockingIOError:
            break


def _esperar_confirmacao(fd, i):
    limite = time.monotonic() + ESPERA_BLOCO
    while (resta := limite - time.monotonic()) > 0:
        if select.select([fd], [], [], resta)[0]:
            resp = os.read(fd, 64)
            if resp[:3] == CONFIRMA_BLOCO:
                return
    raise ErroTeclado(t("o teclado não confirmou o bloco {n} da imagem", n=i + 1))


class TecladoSemFio:
    """O teclado pelo dongle 2.4 GHz: pacotes de 32 bytes na interface 3, cada um
    confirmado por um eco do teclado."""
    modo = "dongle"

    def __init__(self, caminho=None):
        self.caminho = caminho or achar_hidraw(interface=INTERFACE_DONGLE, hid_id=HID_ID_DONGLE)
        try:
            self.fd = os.open(self.caminho, os.O_RDWR | os.O_NONBLOCK)
        except PermissionError:
            raise ErroTeclado(t("sem permissão em {c}. Instale a regra udev: sudo bash scripts/instalar-udev.sh",
                                c=self.caminho)) from None

    def fechar(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.fechar()

    def presente(self):
        """True se o teclado responde pelo dongle (ligado no 2.4 GHz e acordado)."""
        try:
            self.enviar(P.SEM_FIO_PRESENCA, espera=0.8)
            return True
        except ErroTeclado:
            return False

    def enviar(self, quadro: bytes, espera=ESPERA_ECO):
        if len(quadro) != P.SEM_FIO_TAM:
            raise ValueError(f"pacote com {len(quadro)} bytes, esperado {P.SEM_FIO_TAM}")
        _descartar(self.fd)
        os.write(self.fd, b"\x00" + quadro)
        limite = time.monotonic() + espera
        while (resta := limite - time.monotonic()) > 0:
            if select.select([self.fd], [], [], resta)[0]:
                resp = os.read(self.fd, 64)
                if len(resp) >= 3 and resp[0] == quadro[0] and resp[2] == quadro[2]:
                    return resp
        raise ErroTeclado(t("O teclado não respondeu pelo dongle. Ele está ligado no 2.4 GHz e acordado? Aperte uma tecla e tente de novo."))

    def executar(self, quadros):
        for q in quadros:
            self.enviar(q)
        time.sleep(PAUSA_FINAL)

    def enviar_tela(self, *_a, **_k):
        raise ErroTeclado(t("A tela só pode ser trocada pelo cabo USB."))
