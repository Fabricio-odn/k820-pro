import re
import xml.etree.ElementTree as ET
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ICONES = RAIZ / "k820_pro" / "gui" / "icones" / "hicolor"
ID = "io.github.k820pro.Configurador"


def test_svgs_validos():
    colorido = ET.parse(ICONES / "scalable" / "apps" / f"{ID}.svg").getroot()
    simbolico = ET.parse(ICONES / "symbolic" / "apps" / f"{ID}-symbolic.svg").getroot()
    assert colorido.get("viewBox") == "0 0 128 128"
    assert simbolico.get("viewBox") == "0 0 16 16"


def test_simbolico_monocromatico():
    texto = (ICONES / "symbolic" / "apps" / f"{ID}-symbolic.svg").read_text()
    cores = set(re.findall(r'(?:fill|stroke)="([^"]+)"', texto))
    assert cores <= {"#241f31", "none"} and cores


def test_nome_na_janela_e_no_atalho():
    assert '"K820 Pro Studio"' in (RAIZ / "k820_pro" / "gui" / "janela.py").read_text()
    assert "Name=K820 Pro Studio" in (RAIZ / "scripts" / "instalar-atalho.sh").read_text()
