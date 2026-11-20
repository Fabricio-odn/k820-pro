"""Página Teclas: clique numa tecla e escolha o que ela faz (outra tecla, atalho ou
multimídia). A troca vai para o teclado assim que é escolhida."""
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk  # noqa: E402

from ... import acoes as A  # noqa: E402
from ... import servico as S  # noqa: E402
from ...i18n import t  # noqa: E402
from ...layout import POR_NOME  # noqa: E402
from ..componentes import Colunas, Debounce, cabecalho_pagina, cartao, secao, segmentado  # noqa: E402
from ..teclado import Teclado, rotulo  # noqa: E402

ATRASO_MS = 400
MODS = [("ctrl_esq", "Ctrl"), ("shift_esq", "Shift"), ("alt_esq", "Alt"), ("win", "Win")]
TECLAS_ALVO = sorted(A.TECLAS_HID, key=lambda n: (
    0 if (len(n) == 1 and n.isalpha()) else 1 if n.isdigit() else 2 if n[0] == "f" and n[1:].isdigit() else 3,
    int(n[1:]) if n[0] == "f" and n[1:].isdigit() else 0, n))


def nome_tecla(nome):
    tec = POR_NOME.get(nome)
    r = rotulo(tec) if tec else ""
    if r and r.upper() != nome.upper():
        return f"{r} ({nome})"
    return nome.upper() if len(nome) <= 3 else nome


def nome_acao(acao):
    if acao in A.MULTIMIDIA:
        return t(acao)
    return " + ".join(nome_tecla(p) for p in acao.split("+"))


class PaginaTeclas(Gtk.Box):
    def __init__(self, janela):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.janela = janela
        self.debounce = Debounce(ATRASO_MS, self._gravar)
        self._carregando = False
        self.append(cabecalho_pagina(t("Teclas"), t("Clique numa tecla e escolha o que ela deve fazer.")))

        self.teclado = Teclado(ao_mudar=lambda _s: self._tecla_escolhida(), bloqueadas={"fn"})
        self.teclado.set_size_request(-1, 300)
        self.append(cartao(self.teclado))

        # painel da tecla escolhida
        painel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.titulo_tecla = Gtk.Label(xalign=0)
        self.titulo_tecla.add_css_class("title-3")
        painel.append(self.titulo_tecla)
        self.tipo = segmentado([("padrao", t("Padrão de fábrica")), ("tecla", t("Tecla ou atalho")),
                                ("multimidia", t("Multimídia"))], lambda _k: self._controles_mudaram())
        painel.append(secao(t("Tipo"), self.tipo))
        self.alvo_tecla = Gtk.DropDown.new_from_strings([nome_tecla(n) for n in TECLAS_ALVO])
        self.alvo_tecla.set_enable_search(True)
        self.alvo_tecla.connect("notify::selected", lambda *_: self._controles_mudaram())
        self.mods = {}
        caixa_mods = Gtk.Box(spacing=8, homogeneous=True)
        for chave, rot in MODS:
            b = Gtk.ToggleButton(label=rot)
            b.add_css_class("opcao")
            b.connect("toggled", lambda *_: self._controles_mudaram())
            self.mods[chave] = b
            caixa_mods.append(b)
        self.secao_tecla = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.secao_tecla.append(secao(t("Ação"), self.alvo_tecla))
        self.secao_tecla.append(secao(t("Modificadores"), caixa_mods))
        painel.append(self.secao_tecla)
        self.alvo_media = Gtk.DropDown.new_from_strings([t(m) for m in A.MULTIMIDIA])
        self.alvo_media.connect("notify::selected", lambda *_: self._controles_mudaram())
        self.secao_media = secao(t("Ação"), self.alvo_media)
        painel.append(self.secao_media)
        self.painel = cartao(painel)

        # lista do que já foi remapeado
        self.lista = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE, css_classes=["boxed-list"])
        direita = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        direita.append(secao(t("Teclas remapeadas"), self.lista))
        self.colunas = Colunas(self.painel, direita, 340)
        self.append(self.colunas)
        self._tecla_escolhida()
        self.atualizar_lista()

    def teclados(self):
        return [self.teclado]

    def definir_empilhado(self, empilhado):
        self.colunas.definir_empilhado(empilhado)

    def ao_sair(self):
        self.debounce.disparar_agora()

    def _tecla(self):
        return next(iter(self.teclado.selecao), None)

    def _tecla_escolhida(self):
        nome = self._tecla()
        self.painel.set_sensitive(nome is not None)
        self.titulo_tecla.set_label(nome_tecla(nome) if nome else t("Clique numa tecla e escolha o que ela deve fazer."))
        self._carregando = True
        acao = self.janela.estado.teclas.get(nome) if nome else None
        if acao is None:
            self.tipo.set_active_name("padrao")
        elif acao in A.MULTIMIDIA:
            self.tipo.set_active_name("multimidia")
            self.alvo_media.set_selected(list(A.MULTIMIDIA).index(acao))
        else:
            self.tipo.set_active_name("tecla")
            partes = acao.split("+")
            for chave, b in self.mods.items():
                b.set_active(chave in partes)
            alvo = next((p for p in partes if p in A.TECLAS_HID), None)
            if alvo:
                self.alvo_tecla.set_selected(TECLAS_ALVO.index(alvo))
        self._carregando = False
        self._mostrar_secoes()

    def _mostrar_secoes(self):
        tipo = self.tipo.get_active_name()
        self.secao_tecla.set_visible(tipo == "tecla")
        self.secao_media.set_visible(tipo == "multimidia")

    def _acao(self):
        tipo = self.tipo.get_active_name()
        if tipo == "multimidia":
            return list(A.MULTIMIDIA)[self.alvo_media.get_selected()]
        if tipo == "tecla":
            partes = [k for k, b in self.mods.items() if b.get_active()]
            return "+".join(partes + [TECLAS_ALVO[self.alvo_tecla.get_selected()]])
        return A.PADRAO

    def _controles_mudaram(self):
        self._mostrar_secoes()
        if not self._carregando and self._tecla():
            self.debounce.tocar()

    def _gravar(self):
        nome, acao = self._tecla(), self._acao()
        if nome:
            self.janela.executar(lambda: S.remapear(self.janela.estado, nome, acao),
                                 depois=lambda _e: self.atualizar_lista())

    def _desfazer(self, nome):
        self.janela.executar(lambda: S.remapear(self.janela.estado, nome, A.PADRAO),
                             depois=lambda _e: (self.atualizar_lista(), self._tecla_escolhida()))

    def atualizar_lista(self):
        self.lista.remove_all()
        self.teclado.marcadas = set(self.janela.estado.teclas)
        self.teclado.queue_draw()
        if not self.janela.estado.teclas:
            self.lista.append(Adw.ActionRow(title=t("Nenhuma tecla remapeada")))
            return
        for nome, acao in sorted(self.janela.estado.teclas.items()):
            linha = Adw.ActionRow(title=nome_tecla(nome), subtitle="→ " + nome_acao(acao))
            b = Gtk.Button(icon_name="edit-undo-symbolic", valign=Gtk.Align.CENTER,
                           tooltip_text=t("Voltar ao padrão"), css_classes=["flat"])
            b.connect("clicked", lambda _b, n=nome: self._desfazer(n))
            linha.add_suffix(b)
            self.lista.append(linha)

    def ao_restaurar(self):
        self.atualizar_lista()
        self._tecla_escolhida()
