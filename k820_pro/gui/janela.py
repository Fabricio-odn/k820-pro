"""Janela principal: cabeçalho, barra lateral com as seções e a pilha de páginas,
no mesmo desenho do dazz-mouse."""
import threading

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib, GObject, Gtk  # noqa: E402

from .. import i18n  # noqa: E402
from .. import servico as S  # noqa: E402
from ..dispositivo import ErroTeclado, achar_hidraw, versao_firmware  # noqa: E402
from ..estado import Estado  # noqa: E402
from ..i18n import t  # noqa: E402
from ..preferencias import Preferencias  # noqa: E402
from .paginas.ajustes import PaginaAjustes  # noqa: E402
from .paginas.atalhos import PaginaAtalhos  # noqa: E402
from .paginas.cores import PaginaCores  # noqa: E402
from .paginas.luz import PaginaLuz  # noqa: E402
from .paginas.tela import PaginaTela  # noqa: E402
from .paginas.teclas import PaginaTeclas  # noqa: E402
from .versoes import VERSOES  # noqa: E402

# (nome na pilha, rótulo, ícone, classe da página)
SECOES = [
    ("luz", "Iluminação", "keyboard-brightness-symbolic", PaginaLuz),
    ("cores", "Cores por tecla", "color-select-symbolic", PaginaCores),
    ("teclas", "Teclas", "input-keyboard-symbolic", PaginaTeclas),
    ("tela", "Tela", "video-display-symbolic", PaginaTela),
    ("ajustes", "Ajustes", "emblem-system-symbolic", PaginaAjustes),
    ("atalhos", "Atalhos", "preferences-desktop-keyboard-shortcuts-symbolic", PaginaAtalhos),
]

INTERVALO_CONEXAO_S = 2
TAMANHO_MINIMO = (360, 294)
LARGURA_EMPILHAR = "max-width: 1100sp"  # páginas de duas colunas viram uma
LARGURA_ESTREITA = "max-width: 720sp"   # a barra lateral se recolhe


class Trabalhador:
    """Uma operação por vez com o teclado, fora da thread da interface."""

    def __init__(self):
        self.ocupado = False

    def rodar(self, funcao, ao_terminar):
        if self.ocupado:
            return False
        self.ocupado = True

        def alvo():
            try:
                resultado, erro = funcao(), None
            except (ErroTeclado, ValueError, RuntimeError, OSError) as e:
                resultado, erro = None, e
            GLib.idle_add(self._fim, ao_terminar, resultado, erro)

        threading.Thread(target=alvo, daemon=True).start()
        return True

    def _fim(self, ao_terminar, resultado, erro):
        self.ocupado = False
        ao_terminar(resultado, erro)
        return False


class Janela(Adw.ApplicationWindow):
    def __init__(self, app, tema=None):
        super().__init__(application=app, title="K820 Pro Studio", default_width=1200, default_height=820)
        self.tema = tema
        self.trabalho = Trabalhador()
        self._fila = None  # última operação pedida enquanto outra rodava
        self.prefs = Preferencias.carregar()
        try:
            self.estado = Estado.carregar()
        except ValueError as e:
            self.estado = Estado()
            GLib.idle_add(self.avisar, str(e))

        # cabeçalho
        self.titulo = Adw.WindowTitle(title="K820 Pro Studio", subtitle="")
        cabecalho = Adw.HeaderBar(title_widget=self.titulo)
        self.botao_barra = Gtk.ToggleButton(icon_name="sidebar-show-symbolic", tooltip_text=t("Seções"),
                                            visible=False)
        cabecalho.pack_start(self.botao_barra)
        self.botao_restaurar = Gtk.Button(label=t("Restaurar padrão"), tooltip_text=t("Padrão de fábrica do teclado"))
        self.botao_restaurar.connect("clicked", lambda *_: self._confirmar_restaurar())
        self.botao_tema = Gtk.Button()
        self.botao_tema.connect("clicked", lambda *_: self._alternar_tema())
        cabecalho.pack_end(self._menu_idioma())
        cabecalho.pack_end(self.botao_tema)
        cabecalho.pack_end(self.botao_restaurar)

        # barra lateral
        self.lista = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        self.lista.add_css_class("navigation-sidebar")
        self._linhas = {}
        for nome, rotulo, icone, _ in SECOES:
            caixa = Gtk.Box(spacing=12, margin_start=6)
            caixa.append(Gtk.Image(icon_name=icone))
            caixa.append(Gtk.Label(label=t(rotulo), xalign=0))
            linha = Gtk.ListBoxRow(child=caixa)
            linha.nome = nome
            self.lista.append(linha)
            self._linhas[nome] = linha
        self.lista.connect("row-selected", self._secao_escolhida)
        self.rodape = Gtk.Label(xalign=0, margin_start=18, margin_bottom=12)
        self.rodape.add_css_class("secundario")
        self.rodape.add_css_class("caption")
        barra = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        barra.add_css_class("barra-lateral")
        self.lista.set_vexpand(True)
        self.lista.set_margin_top(12)
        self.lista.set_margin_start(8)
        self.lista.set_margin_end(8)
        barra.append(self.lista)
        barra.append(self.rodape)

        # páginas
        self.pilha = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE, hexpand=True)
        self.paginas = {}
        for nome, _, _, classe in SECOES:
            pagina = classe(self)
            self.paginas[nome] = pagina
            clamp = Adw.Clamp(maximum_size=1100, child=pagina, margin_top=28, margin_bottom=28,
                              margin_start=24, margin_end=24)
            self.pilha.add_named(Gtk.ScrolledWindow(child=clamp, hscrollbar_policy=Gtk.PolicyType.NEVER), nome)

        self.divisao = Adw.OverlaySplitView(sidebar=barra, content=self.pilha,
                                            min_sidebar_width=200, max_sidebar_width=240)
        self.divisao.bind_property("show-sidebar", self.botao_barra, "active",
                                   GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
        self.toasts = Adw.ToastOverlay(child=self.divisao)
        vista = Adw.ToolbarView(content=self.toasts)
        vista.add_top_bar(cabecalho)
        self.set_content(vista)
        self.set_size_request(*TAMANHO_MINIMO)

        empilhar = Adw.Breakpoint.new(Adw.BreakpointCondition.parse(LARGURA_EMPILHAR))
        empilhar.connect("apply", lambda *_: self._empilhar(True))
        empilhar.connect("unapply", lambda *_: self._empilhar(False))
        estreita = Adw.Breakpoint.new(Adw.BreakpointCondition.parse(LARGURA_ESTREITA))
        estreita.connect("apply", lambda *_: self._estreitar(True))
        estreita.connect("unapply", lambda *_: self._estreitar(False))
        self.add_breakpoint(empilhar)
        self.add_breakpoint(estreita)

        for kb in self.teclados():
            kb.versao = VERSOES[self.prefs.versao]
            kb.tema = self.prefs.tema
        self._atualizar_botao_tema()
        self.mostrar("luz")
        self._checar_conexao()
        self._fonte = GLib.timeout_add_seconds(INTERVALO_CONEXAO_S, self._checar_conexao)
        self.connect("close-request", self._fechando)

    # utilidades usadas pelas páginas ------------------------------------------------
    def pagina(self, nome):
        return self.paginas[nome]

    def teclados(self):
        return [kb for p in self.paginas.values() for kb in p.teclados()]

    def avisar(self, texto):
        self.toasts.add_toast(Adw.Toast(title=texto, timeout=5))
        return False

    def executar(self, funcao, sucesso=None, depois=None):
        """Roda `funcao` fora da interface. Erros viram aviso; `sucesso` (texto ou função do
        resultado) só aparece quando é dado. Se outra operação estiver rodando, esta espera e
        roda em seguida (a mais recente substitui a que estava esperando)."""
        def fim(resultado, erro):
            if erro:
                self.avisar(t("Erro: {erro}", erro=erro))
            elif sucesso:
                self.avisar(sucesso(resultado) if callable(sucesso) else sucesso)
            if depois:
                depois(erro)
            if self._fila:
                proxima, self._fila = self._fila, None
                self.executar(*proxima)

        if not self.trabalho.rodar(funcao, fim):
            self._fila = (funcao, sucesso, depois)

    def mostrar(self, nome):
        self.lista.select_row(self._linhas[nome])

    def trocar_versao(self, chave):
        self.prefs.versao = chave
        self._salvar_prefs()
        for kb in self.teclados():
            kb.versao = VERSOES[chave]
            kb.queue_draw()

    # internos ------------------------------------------------------------------------
    def _empilhar(self, empilhado):
        for p in self.paginas.values():
            p.definir_empilhado(empilhado)

    def _estreitar(self, estreito):
        self.divisao.set_collapsed(estreito)
        self.divisao.set_show_sidebar(not estreito)
        self.botao_barra.set_visible(estreito)
        if estreito:
            self.botao_restaurar.set_icon_name("edit-undo-symbolic")
        else:
            self.botao_restaurar.set_label(t("Restaurar padrão"))
        self._empilhar(estreito)

    def _secao_escolhida(self, _lista, linha):
        if linha is None:
            return
        if self.divisao.get_collapsed():
            self.divisao.set_show_sidebar(False)
        anterior = self.pilha.get_visible_child_name()
        if anterior and anterior != linha.nome:
            self.paginas[anterior].ao_sair()
        self.pilha.set_visible_child_name(linha.nome)

    def _checar_conexao(self):
        try:
            achar_hidraw()
            self.titulo.set_subtitle(t("Conectado pelo cabo"))
        except ErroTeclado:
            self.titulo.set_subtitle(t("Desconectado: ligue o cabo USB"))
        versao = versao_firmware()
        if versao:
            self.rodape.set_label(t("Firmware {v}", v=versao))
        return GLib.SOURCE_CONTINUE

    def _salvar_prefs(self):
        """A mudança já vale na tela; se não der para gravar, avisa em vez de quebrar."""
        try:
            self.prefs.salvar()
        except OSError as e:
            self.avisar(t("Não consegui salvar a preferência: {erro}", erro=e))

    def _menu_idioma(self):
        menu = Gio.Menu()
        for codigo, nome in i18n.IDIOMAS.items():
            menu.append(nome, f"win.idioma::{codigo}")
        acao = Gio.SimpleAction.new_stateful("idioma", GLib.VariantType.new("s"),
                                             GLib.Variant.new_string(i18n.ativo()))
        acao.connect("activate", self._trocar_idioma)
        self.add_action(acao)
        return Gtk.MenuButton(icon_name="preferences-desktop-locale-symbolic", menu_model=menu,
                              tooltip_text=t("Idioma"))

    def _trocar_idioma(self, acao, valor):
        acao.set_state(valor)
        self.prefs.idioma = valor.get_string()
        self._salvar_prefs()
        self.avisar(t("Reinicie o programa para trocar o idioma."))

    def _atualizar_botao_tema(self):
        claro = self.prefs.tema == "claro"
        self.botao_tema.set_icon_name("weather-clear-night-symbolic" if claro else "weather-clear-symbolic")
        self.botao_tema.set_tooltip_text(t("Tema escuro") if claro else t("Tema claro"))

    def _alternar_tema(self):
        self.prefs.tema = "claro" if self.prefs.tema == "escuro" else "escuro"
        if self.tema:
            self.tema.aplicar(self.prefs.tema)
        self._salvar_prefs()
        self._atualizar_botao_tema()
        for kb in self.teclados():
            kb.tema = self.prefs.tema
            kb.queue_draw()

    def _confirmar_restaurar(self):
        d = Adw.AlertDialog(heading=t("Restaurar o padrão de fábrica?"),
                            body=t("Apaga luz, cores, teclas remapeadas e ajustes."))
        d.add_response("cancelar", t("Cancelar"))
        d.add_response("restaurar", t("Restaurar"))
        d.set_response_appearance("restaurar", Adw.ResponseAppearance.DESTRUCTIVE)

        def resposta(_d, r):
            if r == "restaurar":
                self.executar(lambda: S.restaurar(self.estado), t("Teclado restaurado"),
                              depois=lambda erro: erro or self._apos_restaurar())

        d.connect("response", resposta)
        d.present(self)

    def _apos_restaurar(self):
        for p in self.paginas.values():
            if hasattr(p, "ao_restaurar"):
                p.ao_restaurar()

    def _fechando(self, *_):
        for p in self.paginas.values():
            p.ao_sair()
        GLib.source_remove(self._fonte)
        return False
