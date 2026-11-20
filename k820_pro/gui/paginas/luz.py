"""Página Iluminação: efeito, cor, brilho, velocidade e direção, com a prévia animada.
Tudo vai para o teclado sozinho, 300 ms depois da última mudança."""
import time
from dataclasses import replace

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk  # noqa: E402

from ... import protocolo as P  # noqa: E402
from ... import servico as S  # noqa: E402
from ...i18n import t  # noqa: E402
from ...layout import TECLAS  # noqa: E402
from ..componentes import (Colunas, Debounce, Paleta, cabecalho_pagina, cartao, escala,  # noqa: E402
                           grade_de_opcoes, secao, segmentado)
from ..efeitos import cor_da_tecla  # noqa: E402
from ..teclado import Teclado  # noqa: E402

ATRASO_MS = 300


class PaginaLuz(Gtk.Box):
    def __init__(self, janela):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.janela = janela
        self.il = P.Iluminacao("onda", (255, 0, 0), True, P.BRILHO_MAX, 3, "esquerda")
        self.debounce = Debounce(ATRASO_MS, self._gravar)
        self._carregando = True

        self.append(cabecalho_pagina(t("Iluminação"), t("Os 20 efeitos do teclado. A prévia acompanha o que você escolhe e o teclado muda junto.")))

        self.previa = Teclado(interativo=False)
        self.previa.set_size_request(-1, 300)
        self.legenda = Gtk.Label()
        self.legenda.add_css_class("secundario")
        self.legenda.add_css_class("caption")
        caixa_previa = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        caixa_previa.append(self.previa)
        caixa_previa.append(self.legenda)
        esquerda = cartao(caixa_previa)

        self.append(esquerda)
        grade, self.botoes_efeito = grade_de_opcoes([(e, t(e)) for e in P.EFEITOS], self._efeito, colunas=3)
        efeitos = secao(t("Efeito"), grade)
        direita = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=22)
        self.paleta = Paleta(self._cor)
        direita.append(secao(t("Cor"), self.paleta))
        self.brilho = escala(0, P.BRILHO_MAX, lambda v: self._mudar(brilho=v))
        direita.append(secao(t("Brilho"), self.brilho))
        self.velocidade = escala(0, P.VELOCIDADE_MAX, lambda v: self._mudar(velocidade=v))
        direita.append(secao(t("Velocidade"), self.velocidade))
        self.direcao = segmentado([(d, t(d)) for d in P.DIRECOES], lambda d: self._mudar(direcao=d))
        self.secao_direcao = secao(t("Direção"), self.direcao, t("Só para rolagem, onda, fluxo e inclinado"))
        direita.append(self.secao_direcao)

        self.colunas = Colunas(efeitos, direita, 420)
        self.append(self.colunas)
        self._mostrar(self.il)
        self._carregando = False
        self._inicio = time.monotonic()
        GLib.timeout_add(40, self._animar)

    def teclados(self):
        return [self.previa]

    def definir_empilhado(self, empilhado):
        self.colunas.definir_empilhado(empilhado)

    def ao_sair(self):
        self.debounce.disparar_agora()

    def _mostrar(self, il):
        self.botoes_efeito[il.efeito].set_active(True)
        self.paleta.definir(il.cor, il.arco_iris)
        self.brilho.set_value(il.brilho)
        self.velocidade.set_value(il.velocidade)
        self.direcao.set_active_name(il.direcao)
        self._atualizar_direcao()
        self._atualizar_legenda()

    def _atualizar_direcao(self):
        aceitas = P.DIRECOES_POR_EFEITO.get(self.il.efeito, ())
        self.secao_direcao.set_sensitive(bool(aceitas))
        for d in P.DIRECOES:
            self.direcao.get_toggle_by_name(d).set_enabled(d in aceitas)
        if aceitas and self.il.direcao not in aceitas:
            self.il = replace(self.il, direcao=aceitas[0])
            self.direcao.set_active_name(aceitas[0])

    def _atualizar_legenda(self):
        cor = t("arco-íris") if self.il.arco_iris else "#%02X%02X%02X" % self.il.cor
        self.legenda.set_label(t("Prévia: {efeito}, {cor}", efeito=t(self.il.efeito), cor=cor))

    def _efeito(self, efeito):
        self._mudar(efeito=efeito)

    def _cor(self, cor, arco_iris):
        self._mudar(cor=cor, arco_iris=arco_iris)

    def _mudar(self, **campos):
        if self._carregando:
            return
        self.il = replace(self.il, **campos)
        self._carregando = True
        self._atualizar_direcao()
        self._carregando = False
        self._atualizar_legenda()
        self.debounce.tocar()

    def _gravar(self):
        il = self.il
        self.janela.executar(lambda: S.aplicar_luz(il))

    def _animar(self):
        if self.previa.get_mapped():
            agora = time.monotonic() - self._inicio
            il = self.il
            self.previa.cores = {tec.nome: cor_da_tecla(tec, agora, il.efeito, il.cor, il.arco_iris,
                                                        il.brilho, il.velocidade, il.direcao)
                                 for tec in TECLAS}
            self.previa.queue_draw()
        return GLib.SOURCE_CONTINUE
