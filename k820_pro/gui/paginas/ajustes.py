"""Página Ajustes: tempo até dormir, tempo de resposta, versão do teclado e relógio."""
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from ... import servico as S  # noqa: E402
from ...i18n import t  # noqa: E402
from ..componentes import cabecalho_pagina, cartao, grade_de_opcoes, secao, segmentado  # noqa: E402
from ..versoes import VERSOES  # noqa: E402

SONO = [("nunca", "Nunca"), ("1", "1 minuto"), ("5", "5 minutos"), ("30", "30 minutos")]


class PaginaAjustes(Gtk.Box):
    def __init__(self, janela):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        self.janela = janela
        self._carregando = True
        self.append(cabecalho_pagina(t("Ajustes"), t("Ficam gravados no teclado e valem também sem fio.")))

        self.sono = segmentado([(k, t(r)) for k, r in SONO], lambda k: self._ajuste(sono=k))
        self.append(secao(t("Tempo até dormir"), self.sono))
        self.resposta = segmentado([(str(n), str(n)) for n in range(1, 6)],
                                   lambda k: self._ajuste(resposta=int(k)))
        self.append(secao(t("Tempo de resposta das teclas"), self.resposta,
                          t("Nível 1 é o mais rápido (~2-3 ms no cabo). Suba se alguma tecla repetir sozinha.")))

        grade, self.botoes_versao = grade_de_opcoes([(k, t(v.nome)) for k, v in VERSOES.items()],
                                                    self._versao, colunas=5)
        self.append(secao(t("Versão do teclado"), grade, t("Só muda o desenho do teclado no programa.")))

        linha = Gtk.Box(spacing=12)
        texto = Gtk.Label(label=t("Acertar com a hora do computador"), xalign=0, hexpand=True)
        botao = Gtk.Button(label=t("Acertar agora"))
        botao.connect("clicked", lambda *_: janela.executar(S.acertar_relogio, t("Relógio acertado")))
        linha.append(texto)
        linha.append(botao)
        self.append(secao(t("Relógio da tela"), cartao(linha)))
        self.mostrar()
        self._carregando = False

    def mostrar(self):
        self._carregando = True
        aj = self.janela.estado.ajustes
        self.sono.set_active_name(aj.sono)
        self.resposta.set_active_name(str(aj.resposta))
        self.botoes_versao[self.janela.prefs.versao].set_active(True)
        self._carregando = False

    def teclados(self):
        return []

    def definir_empilhado(self, _empilhado):
        pass

    def ao_sair(self):
        pass

    def escolher_versao(self, chave):
        self.botoes_versao[chave].set_active(True)

    def _versao(self, chave):
        if not self._carregando:
            self.janela.trocar_versao(chave)

    def _ajuste(self, **mudanca):
        if self._carregando:
            return
        self.janela.executar(lambda: S.aplicar_ajustes(self.janela.estado, **mudanca),
                             depois=lambda erro: erro and self.mostrar())

    def ao_restaurar(self):
        self.mostrar()
