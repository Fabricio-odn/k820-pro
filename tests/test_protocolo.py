"""Confere byte a byte os pacotes com os do projeto de referência (gohv, PID 8009)."""
from datetime import datetime
from pathlib import Path

import pytest

from k820_pro import protocolo as P
from k820_pro.cli import main
from k820_pro.dispositivo import achar_hidraw, ErroTeclado, preparar_buffer


def hexa(b):
    return b.hex()


def pacote(**bytes_):
    p = bytearray(64)
    for pos, val in bytes_.items():
        p[int(pos[1:])] = val
    return bytes(p)


def test_pacotes_de_controle():
    assert P.inicio() == pacote(b0=4, b1=0x18)
    assert P.fim() == pacote(b0=4, b1=0xF0)
    assert P.salvar() == pacote(b0=4, b1=0x02)


def test_relogio_igual_ao_testado_no_teclado():
    seq = P.sequencia_relogio(datetime(2026, 11, 20, 12, 34, 0))
    assert seq[0] == P.inicio()
    assert seq[1] == pacote(b0=4, b1=0x28, b8=1)
    assert seq[2] == pacote(b1=1, b2=0x5A, b3=26, b4=11, b5=20, b6=12, b7=34, b8=0, b10=5, b62=0xAA, b63=0x55)  # sexta = 5
    assert seq[3] == P.salvar()


def test_ajustes():
    seq = P.sequencia_ajustes(P.Ajustes("30", 4))
    assert seq[1] == pacote(b0=4, b1=0x17, b2=1, b8=1)
    assert seq[2] == pacote(b1=1, b6=3, b8=4, b62=0xAA, b63=0x55)
    assert seq[3] == P.salvar() and len(seq) == 4
    with pytest.raises(ValueError):
        P.sequencia_ajustes(P.Ajustes("10"))
    with pytest.raises(ValueError):
        P.sequencia_ajustes(P.Ajustes(resposta=6))


def test_iluminacao_espectro():
    il = P.Iluminacao("espectro", (0x12, 0x34, 0x56), False, 4, 2, "esquerda")
    seq = P.sequencia_iluminacao(il)
    assert seq[1] == pacote(b0=4, b1=0x13, b8=1)
    assert seq[2] == pacote(b0=0x08, b1=0x12, b2=0x34, b3=0x56, b9=4, b10=2, b14=0xAA, b15=0x55)
    assert seq[3] == P.salvar() and seq[4] == P.fim()


def test_estatico_vira_respiracao_parada():
    p = P.pacote_iluminacao(P.Iluminacao("estatico", (0, 0, 255), velocidade=4))
    assert p[0] == 0x07 and p[10] == 0 and p[9] == 5 and p[3] == 255


def test_desligado_vira_acende_ao_tocar_sem_brilho():
    p = P.pacote_iluminacao(P.Iluminacao("desligado"))
    assert (p[0], p[9], p[10]) == (0x02, 0, 0)


def test_direcao_e_arco_iris():
    p = P.pacote_iluminacao(P.Iluminacao("rolagem", arco_iris=True, direcao="cima"))
    assert (p[0], p[8], p[11]) == (0x0A, 1, 2)
    with pytest.raises(ValueError):
        P.pacote_iluminacao(P.Iluminacao("rolagem", direcao="esquerda"))


@pytest.mark.parametrize("campo", [{"brilho": 6}, {"velocidade": -1}, {"cor": (256, 0, 0)}, {"efeito": "xyz"}])
def test_valores_invalidos(campo):
    with pytest.raises(ValueError):
        P.Iluminacao(**campo).validar()


def test_buffer_prefixa_zero():
    assert preparar_buffer(P.inicio()) == P.inicio()
    dados = P.sequencia_relogio(datetime(2026, 1, 1))[2]
    assert preparar_buffer(dados) == b"\x00" + dados


def _falso_sysfs(tmp_path, hid_id, iface):
    usb_iface = tmp_path / "usb" / "3-2:1.x"
    hid = usb_iface / "0003:0C45:800A.0001"
    hid.mkdir(parents=True)
    (usb_iface / "bInterfaceNumber").write_text(f"{iface:02x}\n")
    (hid / "uevent").write_text(f"DRIVER=hid-generic\nHID_ID={hid_id}\n")
    classe = tmp_path / "hidraw"
    (classe / "hidraw11").mkdir(parents=True)
    (classe / "hidraw11" / "device").symlink_to(hid)
    return classe


def test_acha_hidraw_pela_interface(tmp_path):
    classe = _falso_sysfs(tmp_path, "0003:00000C45:0000800A", 3)
    assert achar_hidraw(classe) == "/dev/hidraw11"


def test_ignora_outros_dispositivos(tmp_path):
    classe = _falso_sysfs(tmp_path, "0003:00000C45:00007643", 3)  # o mouse
    with pytest.raises(ErroTeclado):
        achar_hidraw(classe)


def test_cli_rejeita_direcao_errada(capsys):
    assert main(["luz", "onda", "-d", "cima"]) == 1
    assert "aceita só" in capsys.readouterr().err
