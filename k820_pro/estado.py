"""O que já foi gravado no teclado, guardado em ~/.config/k820-pro/estado.json.

As tabelas de teclas e de cores vão inteiras a cada mudança, e o pacote de
configurações junta sono e tempo de resposta; sem guardar o resto, uma mudança
apagaria as anteriores. O teclado não tem comando conhecido para ler isso de volta.
"""
import json
import os
from dataclasses import asdict, dataclass, field
from dataclasses import fields as dataclasses_fields
from pathlib import Path

from .protocolo import Ajustes


def caminho_padrao():
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / "k820-pro" / "estado.json"


@dataclass
class Estado:
    teclas: dict = field(default_factory=dict)   # nome da tecla -> nome da ação
    cores: dict = field(default_factory=dict)    # nome da tecla -> "rrggbb"
    ajustes: Ajustes = field(default_factory=Ajustes)

    @classmethod
    def carregar(cls, caminho=None):
        caminho = Path(caminho or caminho_padrao())
        try:
            dados = json.loads(caminho.read_text())
        except FileNotFoundError:
            return cls()
        except (OSError, ValueError) as e:
            raise ValueError(f"estado ilegível em {caminho}: {e}. Apague o arquivo para recomeçar.") from None
        return cls._validar(dados, caminho)

    @classmethod
    def _validar(cls, dados, caminho):
        """Só aceita o que o próprio programa grava; qualquer coisa estranha vira erro claro."""
        from . import acoes
        from .layout import POR_NOME
        from .servico import cor_hex
        try:
            if not isinstance(dados, dict) or not all(
                    isinstance(dados.get(k, {}), dict) for k in ("teclas", "cores", "ajustes")):
                raise ValueError("formato inesperado")
            teclas = {str(k): str(v) for k, v in dict(dados.get("teclas", {})).items()}
            cores = {str(k): str(v) for k, v in dict(dados.get("cores", {})).items()}
            campos = {f.name for f in dataclasses_fields(Ajustes)}
            aj = {k: v for k, v in dict(dados.get("ajustes", {})).items() if k in campos}
            ajustes = Ajustes(**aj)
            ajustes.validar()
            for nome, acao in teclas.items():
                if nome not in POR_NOME or nome == "fn":
                    raise ValueError(f"tecla desconhecida: {nome}")
                acoes.acao(acao)
            for nome, cor in cores.items():
                if nome not in POR_NOME:
                    raise ValueError(f"tecla desconhecida: {nome}")
                cor_hex(cor)
            if not (isinstance(ajustes.b1, int) and isinstance(ajustes.b5, int)
                    and 0 <= ajustes.b1 <= 255 and 0 <= ajustes.b5 <= 255):
                raise ValueError("ajustes b1/b5 fora de 0..255")
        except (TypeError, ValueError, AttributeError) as e:
            raise ValueError(f"estado inválido em {caminho}: {e}. Apague o arquivo para recomeçar.") from None
        return cls(teclas, cores, ajustes)

    def salvar(self, caminho=None):
        caminho = Path(caminho or caminho_padrao())
        caminho.parent.mkdir(parents=True, exist_ok=True)
        dados = {"teclas": self.teclas, "cores": self.cores, "ajustes": asdict(self.ajustes)}
        tmp = caminho.with_suffix(".tmp")
        tmp.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n")
        tmp.replace(caminho)
