"""Página Cores: uma cor para cada tecla. Clique nas teclas, escolha a cor e pinte;
o teclado muda sozinho, meio segundo depois da última pintura."""
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from ... import protocolo as P  # noqa: E402
from ... import servico as S  # noqa: E402
from ...i18n import t  # noqa: E402
from ...layout import POR_NOME  # noqa: E402
from ..componentes import Debounce, Paleta, cabecalho_pagina, cartao, escala, secao  # noqa: E402
from ..teclado import Teclado  # noqa: E402

ATRASO_MS = 500


class PaginaCores(Gtk.Box):
    def __init__(self, janela):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.janela = janela
        self.debounce = Debounce(ATRASO_MS, self._gravar)
        self.append(cabecalho_pagina(t("Cores por tecla"), t("Clique nas teclas para selecionar; depois escolha a cor e pinte.")))

        self.teclado = Teclado(multipla=True, ao_mudar=lambda _s: self._atualizar_contagem())
        self.teclado.set_size_request(-1, 300)
        self.teclado.cores = {n: S.cor_hex(c) for n, c in janela.estado.cores.items()}
        self.contagem = Gtk.Label(xalign=0)
        self.contagem.add_css_class("secundario")
        self.contagem.add_css_class("caption")
        caixa = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        caixa.append(self.teclado)
        caixa.append(self.contagem)
        self.append(cartao(caixa))

        ferramentas = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.paleta = Paleta(lambda _c, _a: None, com_arco_iris=False)
        self.paleta.definir((0x00, 0xE5, 0xFF))
        ferramentas.append(secao(t("Cor"), self.paleta))
        acoes = Gtk.FlowBox(selection_mode=Gtk.SelectionMode.NONE, column_spacing=8, row_spacing=8,
                            max_children_per_line=4, homogeneous=False)
        for rotulo, funcao, sugerido in [(t("Pintar selecionadas"), self._pintar, True),
                                         (t("Pintar todas"), self._pintar_todas, False),
                                         (t("Apagar selecionadas"), self._apagar, False),
                                         (t("Limpar seleção"), self._limpar, False)]:
            b = Gtk.Button(label=rotulo)
            if sugerido:
                b.add_css_class("suggested-action")
            b.connect("clicked", lambda _b, f=funcao: f())
            acoes.append(b)
        ferramentas.append(acoes)
        self.append(ferramentas)

        self.brilho = escala(0, P.BRILHO_MAX, lambda _v: self.debounce.tocar())
        self.brilho.set_value(P.BRILHO_MAX)
        self.append(secao(t("Brilho"), self.brilho))
        self._atualizar_contagem()

    def teclados(self):
        return [self.teclado]

    def definir_empilhado(self, _empilhado):
        pass

    def ao_sair(self):
        self.debounce.disparar_agora()

    def _atualizar_contagem(self):
        self.contagem.set_label(t("{s} selecionada(s) · {c} colorida(s)",
                                  s=len(self.teclado.selecao), c=len(self.teclado.cores)))

    def _pintar(self):
        if not self.teclado.selecao:
            return self.janela.avisar(t("Clique nas teclas para selecionar; depois escolha a cor e pinte."))
        for n in self.teclado.selecao:
            self.teclado.cores[n] = self.paleta.cor
        self._mudou()

    def _pintar_todas(self):
        self.teclado.selecionar(POR_NOME)
        self._pintar()

    def _apagar(self):
        for n in self.teclado.selecao:
            self.teclado.cores.pop(n, None)
        self._mudou()

    def _limpar(self):
        self.teclado.selecionar(())
        self._atualizar_contagem()

    def _mudou(self):
        self.teclado.queue_draw()
        self._atualizar_contagem()
        self.debounce.tocar()

    def _gravar(self):
        cores = {n: "%02x%02x%02x" % c for n, c in self.teclado.cores.items()}
        brilho = int(self.brilho.get_value())
        self.janela.executar(lambda: S.aplicar_cores(self.janela.estado, cores, brilho))

    def ao_restaurar(self):
        self.teclado.cores = {}
        self._mudou_sem_gravar()

    def _mudou_sem_gravar(self):
        self.teclado.queue_draw()
        self._atualizar_contagem()
