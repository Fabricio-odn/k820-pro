"""Preferências da interface (tema, versão do teclado e idioma), em
~/.config/k820-pro/preferencias.json.

Valores estranhos voltam ao padrão campo a campo; o app nunca deixa de abrir por
causa deste arquivo. O arquivo `idioma` da primeira versão publicada é lido
quando ainda não existe preferencias.json.
"""
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from . import i18n
from .estado import caminho_padrao as _caminho_estado

TEMAS = ("escuro", "claro")


def versoes_validas():
    try:
        from .gui.versoes import VERSOES
    except ImportError:
        return ("neutro",)
    return tuple(VERSOES)


def caminho_padrao():
    return _caminho_estado().with_name("preferencias.json")


@dataclass
class Preferencias:
    tema: str = "escuro"
    versao: str = "neutro"
    idioma: str | None = None

    @classmethod
    def carregar(cls, caminho=None):
        caminho = Path(caminho or caminho_padrao())
        try:
            dados = json.loads(caminho.read_text())
        except FileNotFoundError:
            dados = {}
            try:
                antigo = caminho.with_name("idioma").read_text().strip()
                dados["idioma"] = antigo
            except (OSError, ValueError):
                pass
        except (OSError, ValueError):
            dados = {}
        if not isinstance(dados, dict):
            dados = {}
        p = cls()
        if isinstance(dados.get("tema"), str) and dados["tema"] in TEMAS:
            p.tema = dados["tema"]
        if isinstance(dados.get("versao"), str) and dados["versao"] in versoes_validas():
            p.versao = dados["versao"]
        if isinstance(dados.get("idioma"), str) and dados["idioma"] in i18n.IDIOMAS:
            p.idioma = dados["idioma"]
        return p

    def salvar(self, caminho=None):
        caminho = Path(caminho or caminho_padrao())
        caminho.parent.mkdir(parents=True, exist_ok=True)
        tmp = caminho.with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2) + "\n")
        tmp.replace(caminho)
