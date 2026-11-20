"""Janela principal: uma aba para cada parte do teclado."""
import threading
import time
from pathlib import Path

from gi.repository import Adw, Gdk, Gio, GLib, Gtk

from .. import acoes as A
from .. import i18n
from .. import protocolo as P
from .. import servico as S
from ..atalhos import FILEIRA_F, GERAIS, LUZES
from ..dispositivo import ErroTeclado, achar_hidraw
from ..estado import Estado
from ..i18n import t
from ..layout import POR_NOME
from .efeitos import cor_da_tecla
from .versoes import VERSOES
from ..preferencias import Preferencias
from .teclado import Teclado
from ..layout import TECLAS

SONO_OPCOES = [("nunca", "Nunca"), ("1", "1 minuto"), ("5", "5 minutos"), ("30", "30 minutos")]
MODS = [("ctrl_esq", "Ctrl"), ("shift_esq", "Shift"), ("alt_esq", "Alt"), ("win", "Win")]
TECLAS_ALVO = sorted(A.TECLAS_HID, key=lambda n: (
    0 if (len(n) == 1 and n.isalpha()) else 1 if n.isdigit() else 2 if n[0] == "f" and n[1:].isdigit() else 3,
    int(n[1:]) if n[0] == "f" and n[1:].isdigit() else 0, n))


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


def _rgb(cor_rgba):
    return tuple(round(c * 255) for c in (cor_rgba.red, cor_rgba.green, cor_rgba.blue))


def _rgba(rgb):
    c = Gdk.RGBA()
    c.red, c.green, c.blue, c.alpha = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, 1
    return c


def _combo(titulo, itens, ativo=0):
    row = Adw.ComboRow(title=titulo)
    row.set_model(Gtk.StringList.new(itens))
    row.set_selected(ativo)
    return row


def _botao(rotulo, ao_clicar, sugerido=True):
    b = Gtk.Button(label=rotulo, halign=Gtk.Align.END, margin_top=12)
    if sugerido:
        b.add_css_class("suggested-action")
    b.connect("clicked", lambda *_: ao_clicar())
    return b


class Janela(Adw.ApplicationWindow):
    def __init__(self, app, tema=None):
        super().__init__(application=app, title="K820 Pro Studio", default_width=1000, default_height=720)
        self.tema = tema
        self.trabalho = Trabalhador()
        self.prefs = Preferencias.carregar()
        try:
            self.estado = Estado.carregar()
        except ValueError as e:
            self.estado = Estado()
            GLib.idle_add(self.avisar, str(e))

        self.toasts = Adw.ToastOverlay()
        pilha = Adw.ViewStack()
        cab = Adw.HeaderBar()
        cab.set_title_widget(Adw.ViewSwitcher(stack=pilha, policy=Adw.ViewSwitcherPolicy.WIDE))
        cab.pack_end(self._menu_idioma())
        self.botao_tema = Gtk.Button(css_classes=["flat"])
        self.botao_tema.connect("clicked", lambda *_: self._alternar_tema())
        cab.pack_end(self.botao_tema)

        self.faixa = Adw.Banner(title=t("Teclado não encontrado. Ligue o AK820 Pro pelo cabo USB."))
        caixa = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        caixa.append(cab)
        caixa.append(self.faixa)
        caixa.append(pilha)
        pilha.set_vexpand(True)
        self.toasts.set_child(caixa)
        self.set_content(self.toasts)

        for nome, titulo, icone, pagina in [
            ("luz", t("Iluminação"), "weather-clear-symbolic", self._pagina_luz()),
            ("cores", t("Cores"), "applications-graphics-symbolic", self._pagina_cores()),
            ("teclas", t("Teclas"), "input-keyboard-symbolic", self._pagina_teclas()),
            ("tela", t("Tela"), "image-x-generic-symbolic", self._pagina_tela()),
            ("ajustes", t("Ajustes"), "emblem-system-symbolic", self._pagina_ajustes()),
            ("atalhos", t("Atalhos"), "help-about-symbolic", self._pagina_atalhos()),
        ]:
            pilha.add_titled_with_icon(pagina, nome, titulo, icone)

        self._atualizar_botao_tema()
        for kb in self._teclados() + [self.luz_previa]:
            kb.tema = self.prefs.tema
        self._verificar_conexao()
        GLib.timeout_add_seconds(2, self._verificar_conexao)

    # utilidades -------------------------------------------------------------
    def avisar(self, texto):
        self.toasts.add_toast(Adw.Toast(title=texto, timeout=4))
        return False

    def executar(self, funcao, sucesso=None, depois=None):
        def fim(resultado, erro):
            if erro:
                self.avisar(t("Erro: {erro}", erro=erro))
            else:
                self.avisar(sucesso(resultado) if callable(sucesso) else (sucesso or t("Aplicado")))
            if depois:
                depois(erro)

        if not self.trabalho.rodar(funcao, fim):
            self.avisar(t("Enviando…"))

    def _verificar_conexao(self):
        try:
            achar_hidraw()
            self.faixa.set_revealed(False)
        except ErroTeclado:
            self.faixa.set_revealed(True)
        return True

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
        salvar_idioma(valor.get_string())
        self.avisar(t("Reinicie o programa para trocar o idioma."))

    # iluminação -------------------------------------------------------------
    def _pagina_luz(self):
        pag = Adw.PreferencesPage()
        previa = Adw.PreferencesGroup(title=t("Prévia"), description=t("Simulação aproximada; o teclado só muda ao aplicar."))
        self.luz_previa = Teclado(interativo=False)
        self.luz_previa.set_size_request(-1, 300)
        previa.add(self.luz_previa)
        pag.add(previa)
        grupo = Adw.PreferencesGroup(title=t("Iluminação"))
        pag.add(grupo)
        efeitos = list(P.EFEITOS)
        self.luz_efeito = _combo(t("Efeito"), [t(e) for e in efeitos], efeitos.index("onda"))
        self.luz_cor = Gtk.ColorDialogButton(dialog=Gtk.ColorDialog(with_alpha=False), valign=Gtk.Align.CENTER)
        self.luz_cor.set_rgba(_rgba((255, 0, 0)))
        cor = Adw.ActionRow(title=t("Cor"))
        cor.add_suffix(self.luz_cor)
        self.luz_arco = Adw.SwitchRow(title=t("Arco-íris"), active=True)
        self.luz_brilho = Adw.SpinRow.new_with_range(0, P.BRILHO_MAX, 1)
        self.luz_brilho.set_title(t("Brilho"))
        self.luz_brilho.set_value(P.BRILHO_MAX)
        self.luz_vel = Adw.SpinRow.new_with_range(0, P.VELOCIDADE_MAX, 1)
        self.luz_vel.set_title(t("Velocidade"))
        self.luz_vel.set_value(3)
        self.luz_dir = _combo(t("Direção"), [t(d) for d in P.DIRECOES])
        self.luz_dir.set_subtitle(t("Só para rolagem, onda, fluxo e inclinado"))
        for w in (self.luz_efeito, cor, self.luz_arco, self.luz_brilho, self.luz_vel, self.luz_dir):
            grupo.add(w)
        grupo.add(_botao(t("Aplicar"), self._aplicar_luz))
        self._inicio_previa = time.monotonic()
        GLib.timeout_add(40, self._animar_luz)
        return pag

    def _escolha_luz(self):
        efeito = list(P.EFEITOS)[self.luz_efeito.get_selected()]
        direcao = list(P.DIRECOES)[self.luz_dir.get_selected()]
        aceitas = P.DIRECOES_POR_EFEITO.get(efeito)
        if aceitas and direcao not in aceitas:
            direcao = aceitas[0]
        return P.Iluminacao(efeito, _rgb(self.luz_cor.get_rgba()), self.luz_arco.get_active(),
                            int(self.luz_brilho.get_value()), int(self.luz_vel.get_value()), direcao)

    def _animar_luz(self):
        if self.luz_previa.get_mapped():
            il = self._escolha_luz()
            agora = time.monotonic() - self._inicio_previa
            self.luz_previa.cores = {tec.nome: cor_da_tecla(tec, agora, il.efeito, il.cor, il.arco_iris,
                                                            il.brilho, il.velocidade, il.direcao)
                                     for tec in TECLAS}
            self.luz_previa.queue_draw()
        return True

    def _aplicar_luz(self):
        il = self._escolha_luz()
        self.executar(lambda: S.aplicar_luz(il))

    # cores por tecla --------------------------------------------------------
    def _pagina_cores(self):
        caixa = _caixa_pagina(t("Clique nas teclas para selecionar; depois escolha a cor e pinte."))
        self.kb_cores = Teclado(multipla=True)
        self.kb_cores.versao = VERSOES[self.prefs.versao]
        self.kb_cores.cores = {n: S.cor_hex(c) for n, c in self.estado.cores.items()}
        caixa.append(self.kb_cores)
        barra = Gtk.Box(spacing=8, halign=Gtk.Align.CENTER, margin_top=8)
        self.cores_cor = Gtk.ColorDialogButton(dialog=Gtk.ColorDialog(with_alpha=False))
        self.cores_cor.set_rgba(_rgba((0, 170, 255)))
        barra.append(self.cores_cor)
        for rot, f in [(t("Pintar selecionadas"), self._pintar_sel), (t("Pintar todas"), self._pintar_todas),
                       (t("Apagar selecionadas"), self._apagar_sel), (t("Limpar seleção"), self._limpar_sel)]:
            b = Gtk.Button(label=rot)
            b.connect("clicked", lambda _b, f=f: f())
            barra.append(b)
        caixa.append(barra)
        self.cores_brilho = Adw.SpinRow.new_with_range(0, P.BRILHO_MAX, 1)
        self.cores_brilho.set_title(t("Brilho"))
        self.cores_brilho.set_value(P.BRILHO_MAX)
        lista = Gtk.ListBox(css_classes=["boxed-list"], margin_top=12)
        lista.append(self.cores_brilho)
        caixa.append(lista)
        caixa.append(_botao(t("Aplicar"), self._aplicar_cores))
        return _rolavel(caixa)

    def _pintar_sel(self):
        for n in self.kb_cores.selecao:
            self.kb_cores.cores[n] = _rgb(self.cores_cor.get_rgba())
        self.kb_cores.queue_draw()

    def _pintar_todas(self):
        self.kb_cores.selecionar(POR_NOME)
        self._pintar_sel()

    def _apagar_sel(self):
        for n in self.kb_cores.selecao:
            self.kb_cores.cores.pop(n, None)
        self.kb_cores.queue_draw()

    def _limpar_sel(self):
        self.kb_cores.selecionar(())

    def _aplicar_cores(self):
        cores = {n: "%02x%02x%02x" % c for n, c in self.kb_cores.cores.items()}
        brilho = int(self.cores_brilho.get_value())
        self.executar(lambda: S.aplicar_cores(self.estado, cores, brilho))

    # teclas -----------------------------------------------------------------
    def _pagina_teclas(self):
        caixa = _caixa_pagina(t("Clique numa tecla e escolha o que ela deve fazer."))
        self.kb_teclas = Teclado(ao_mudar=self._tecla_escolhida, bloqueadas={"fn"})
        self.kb_teclas.versao = VERSOES[self.prefs.versao]
        caixa.append(self.kb_teclas)

        grupo = Gtk.ListBox(css_classes=["boxed-list"], margin_top=12)
        self.tec_sel = Adw.ActionRow(title=t("Tecla selecionada"), subtitle=t("nenhuma"))
        self.tec_tipo = _combo(t("Tipo"), [t("Padrão de fábrica"), t("Tecla ou atalho"), t("Multimídia")], 1)
        self.tec_tipo.connect("notify::selected", lambda *_: self._atualizar_tipo())
        self.tec_alvo_tecla = _combo(t("Ação"), [_nome_tecla(n) for n in TECLAS_ALVO])
        self.tec_alvo_media = _combo(t("Ação"), [t(m) for m in A.MULTIMIDIA])
        self.tec_mods = Adw.ActionRow(title=t("Modificadores"))
        self.tec_checks = {}
        for chave, rot in MODS:
            c = Gtk.CheckButton(label=rot, valign=Gtk.Align.CENTER)
            self.tec_checks[chave] = c
            self.tec_mods.add_suffix(c)
        for w in (self.tec_sel, self.tec_tipo, self.tec_alvo_tecla, self.tec_mods, self.tec_alvo_media):
            grupo.append(w)
        caixa.append(grupo)
        caixa.append(_botao(t("Remapear"), self._remapear))

        self.tec_lista = Adw.PreferencesGroup(title=t("Teclas remapeadas"), margin_top=18)
        caixa.append(self.tec_lista)
        self._linhas_remap = []
        self._atualizar_tipo()
        self._atualizar_remaps()
        return _rolavel(caixa)

    def _tecla_escolhida(self, selecao):
        nome = next(iter(selecao), None)
        self.tec_sel.set_subtitle(_nome_tecla(nome) if nome else t("nenhuma"))

    def _atualizar_tipo(self):
        tipo = self.tec_tipo.get_selected()
        self.tec_alvo_tecla.set_visible(tipo == 1)
        self.tec_mods.set_visible(tipo == 1)
        self.tec_alvo_media.set_visible(tipo == 2)

    def _acao_escolhida(self):
        tipo = self.tec_tipo.get_selected()
        if tipo == 0:
            return A.PADRAO
        if tipo == 2:
            return list(A.MULTIMIDIA)[self.tec_alvo_media.get_selected()]
        partes = [k for k, c in self.tec_checks.items() if c.get_active()]
        alvo = TECLAS_ALVO[self.tec_alvo_tecla.get_selected()]
        return "+".join(partes + [alvo])

    def _remapear(self):
        nome = next(iter(self.kb_teclas.selecao), None)
        if not nome:
            return self.avisar(t("Clique numa tecla e escolha o que ela deve fazer."))
        acao = self._acao_escolhida()
        self.executar(lambda: S.remapear(self.estado, nome, acao), depois=lambda _e: self._atualizar_remaps())

    def _desfazer(self, nome):
        self.executar(lambda: S.remapear(self.estado, nome, A.PADRAO), depois=lambda _e: self._atualizar_remaps())

    def _atualizar_remaps(self):
        for linha in self._linhas_remap:
            self.tec_lista.remove(linha)
        self._linhas_remap = []
        self.kb_teclas.marcadas = set(self.estado.teclas)
        self.kb_teclas.queue_draw()
        itens = sorted(self.estado.teclas.items()) or [(None, None)]
        for nome, acao in itens:
            if nome is None:
                linha = Adw.ActionRow(title=t("Nenhuma tecla remapeada"))
            else:
                linha = Adw.ActionRow(title=_nome_tecla(nome), subtitle="→ " + _nome_acao(acao))
                b = Gtk.Button(icon_name="edit-undo-symbolic", valign=Gtk.Align.CENTER,
                               tooltip_text=t("Voltar ao padrão"), css_classes=["flat"])
                b.connect("clicked", lambda _b, n=nome: self._desfazer(n))
                linha.add_suffix(b)
            self.tec_lista.add(linha)
            self._linhas_remap.append(linha)

    # tela -------------------------------------------------------------------
    def _pagina_tela(self):
        pag = Adw.PreferencesPage()
        grupo = Adw.PreferencesGroup(title=t("Imagem ou GIF"), description=t("Até 140 quadros. Leva uns 20 segundos."))
        pag.add(grupo)
        self.tela_arquivo = None
        self.tela_previa = Gtk.Picture(content_fit=Gtk.ContentFit.CONTAIN, width_request=256,
                                       height_request=256, halign=Gtk.Align.CENTER, margin_bottom=12,
                                       css_classes=["card"])
        self.tela_linha = Adw.ActionRow(title=t("Nenhum arquivo escolhido"))
        escolher = Gtk.Button(label=t("Escolher arquivo…"), valign=Gtk.Align.CENTER)
        escolher.connect("clicked", lambda *_: self._escolher_imagem())
        self.tela_linha.add_suffix(escolher)
        self.tela_encaixar = Adw.SwitchRow(title=t("Mostrar a imagem inteira (com faixas)"),
                                           subtitle=t("Sem isso, a imagem é cortada para preencher a tela 128×128."))
        self.tela_encaixar.connect("notify::active", lambda *_: self._carregar_previa_tela())
        self._tela_quadros, self._tela_animacao = [], 0
        self.tela_progresso = Gtk.ProgressBar(margin_top=12, show_text=True, visible=False)
        self.tela_botao = _botao(t("Enviar para a tela"), self._enviar_tela)
        grupo.add(self.tela_previa)
        grupo.add(self.tela_linha)
        grupo.add(self.tela_encaixar)
        grupo.add(self.tela_progresso)
        grupo.add(self.tela_botao)
        return pag

    def _escolher_imagem(self):
        filtro = Gtk.FileFilter(name=t("Imagens"))
        for tipo in ("image/gif", "image/png", "image/jpeg", "image/webp", "image/bmp"):
            filtro.add_mime_type(tipo)
        filtros = Gio.ListStore.new(Gtk.FileFilter)
        filtros.append(filtro)
        dialogo = Gtk.FileDialog(filters=filtros)

        def pronto(d, res):
            try:
                arquivo = d.open_finish(res)
            except GLib.Error:
                return
            self.tela_arquivo = arquivo.get_path()
            self.tela_linha.set_title(Path(self.tela_arquivo).name)
            self._carregar_previa_tela()

        dialogo.open(self, None, pronto)

    def _carregar_previa_tela(self):
        """Mostra os quadros já convertidos (128×128, RGB565), como vão aparecer no teclado."""
        if not self.tela_arquivo:
            return
        caminho, modo = self.tela_arquivo, ("encaixar" if self.tela_encaixar.get_active() else "cortar")

        def carregar():
            from .. import imagem
            quadros, tempos = imagem.carregar(caminho, modo)
            return [_textura_rgb565(q) for q in quadros], tempos

        def pronto(resultado, erro):
            if erro:
                self.avisar(t("Erro: {erro}", erro=erro))
                return
            self._tela_quadros = list(zip(*resultado))
            self._tela_animacao += 1
            self._tocar_quadro(self._tela_animacao, 0)

        threading.Thread(target=lambda: _em_thread(carregar, pronto), daemon=True).start()

    def _tocar_quadro(self, animacao, i):
        if animacao != self._tela_animacao or not self._tela_quadros:
            return False
        textura, ms = self._tela_quadros[i % len(self._tela_quadros)]
        self.tela_previa.set_paintable(textura)
        if len(self._tela_quadros) > 1:
            GLib.timeout_add(max(20, ms), self._tocar_quadro, animacao, i + 1)
        return False

    def _enviar_tela(self):
        if not self.tela_arquivo:
            return self.avisar(t("Nenhum arquivo escolhido"))
        caminho, modo = self.tela_arquivo, ("encaixar" if self.tela_encaixar.get_active() else "cortar")
        self.tela_botao.set_sensitive(False)
        self.tela_progresso.set_visible(True)
        self.tela_progresso.set_fraction(0)

        def progresso(i, n):
            GLib.idle_add(self.tela_progresso.set_fraction, i / n)

        def depois(_erro):
            self.tela_botao.set_sensitive(True)
            self.tela_progresso.set_visible(False)

        self.executar(lambda: S.enviar_tela(caminho, modo, progresso),
                      sucesso=lambda n: t("Enviado: {n} quadro(s)", n=n), depois=depois)

    # ajustes ----------------------------------------------------------------
    def _pagina_ajustes(self):
        pag = Adw.PreferencesPage()
        g1 = Adw.PreferencesGroup(title=t("Ajustes"))
        pag.add(g1)
        chaves = [c for c, _ in SONO_OPCOES]
        self.aj_sono = _combo(t("Tempo até dormir"), [t(r) for _, r in SONO_OPCOES],
                              chaves.index(self.estado.ajustes.sono))
        self.aj_resp = Adw.SpinRow.new_with_range(1, 5, 1)
        self.aj_resp.set_title(t("Tempo de resposta das teclas"))
        self.aj_resp.set_subtitle(t("Nível 1 é o mais rápido (~2-3 ms no cabo). Suba se alguma tecla repetir sozinha."))
        self.aj_resp.set_value(self.estado.ajustes.resposta)
        g1.add(self.aj_sono)
        g1.add(self.aj_resp)
        g1.add(_botao(t("Aplicar"), self._aplicar_ajustes))

        gv = Adw.PreferencesGroup(title=t("Versão do teclado"))
        pag.add(gv)
        chaves_v = list(VERSOES)
        self.aj_versao = _combo(t("Versão do teclado"), [t(v.nome) for v in VERSOES.values()],
                                chaves_v.index(self.prefs.versao))
        self.aj_versao.set_subtitle(t("Só muda o desenho do teclado no programa."))
        self.aj_versao.connect("notify::selected", lambda *_: self._trocar_versao())
        gv.add(self.aj_versao)

        g2 = Adw.PreferencesGroup(title=t("Relógio da tela"))
        pag.add(g2)
        linha = Adw.ActionRow(title=t("Acertar com a hora do computador"))
        b = Gtk.Button(label=t("Acertar agora"), valign=Gtk.Align.CENTER)
        b.connect("clicked", lambda *_: self.executar(S.acertar_relogio, t("Relógio acertado")))
        linha.add_suffix(b)
        g2.add(linha)

        g3 = Adw.PreferencesGroup(title=t("Padrão de fábrica do teclado"))
        pag.add(g3)
        linha = Adw.ActionRow(title=t("Padrão de fábrica do teclado"), subtitle=t("Apaga luz, cores, teclas remapeadas e ajustes."))
        b = Gtk.Button(label=t("Restaurar"), valign=Gtk.Align.CENTER, css_classes=["destructive-action"])
        b.connect("clicked", lambda *_: self._confirmar_restaurar())
        linha.add_suffix(b)
        g3.add(linha)
        return pag

    def _atualizar_botao_tema(self):
        claro = self.prefs.tema == "claro"
        self.botao_tema.set_icon_name("weather-clear-night-symbolic" if claro else "weather-clear-symbolic")
        self.botao_tema.set_tooltip_text(t("Tema escuro") if claro else t("Tema claro"))

    def _alternar_tema(self):
        self.prefs.tema = "claro" if self.prefs.tema == "escuro" else "escuro"
        if self.tema:
            self.tema.aplicar(self.prefs.tema)
        self.prefs.salvar()
        self._atualizar_botao_tema()
        for kb in self._teclados() + [self.luz_previa]:
            kb.tema = self.prefs.tema
            kb.queue_draw()

    def _teclados(self):
        return [self.kb_cores, self.kb_teclas]

    def _trocar_versao(self):
        self.prefs.versao = list(VERSOES)[self.aj_versao.get_selected()]
        self.prefs.salvar()
        for kb in self._teclados():
            kb.versao = VERSOES[self.prefs.versao]
            kb.queue_draw()

    def _aplicar_ajustes(self):
        sono = SONO_OPCOES[self.aj_sono.get_selected()][0]
        resp = int(self.aj_resp.get_value())
        self.executar(lambda: S.aplicar_ajustes(self.estado, sono=sono, resposta=resp))

    def _confirmar_restaurar(self):
        d = Adw.AlertDialog(heading=t("Restaurar o padrão de fábrica?"),
                            body=t("Apaga luz, cores, teclas remapeadas e ajustes."))
        d.add_response("cancelar", t("Cancelar"))
        d.add_response("restaurar", t("Restaurar"))
        d.set_response_appearance("restaurar", Adw.ResponseAppearance.DESTRUCTIVE)

        def resposta(_d, r):
            if r == "restaurar":
                self.executar(lambda: S.restaurar(self.estado), t("Teclado restaurado"), depois=self._apos_restaurar)

        d.connect("response", resposta)
        d.present(self)

    def _apos_restaurar(self, erro):
        if erro:
            return
        self.kb_cores.cores = {}
        self.kb_cores.queue_draw()
        self._atualizar_remaps()
        self.aj_sono.set_selected([c for c, _ in SONO_OPCOES].index("5"))
        self.aj_resp.set_value(2)

    # atalhos ----------------------------------------------------------------
    def _pagina_atalhos(self):
        pag = Adw.PreferencesPage(description=t("Atalhos de fábrica do teclado. Funcionam sem nenhum programa."))
        aviso = Adw.PreferencesGroup(description=t("Fonte: manual do AK820 Pro. Confira no seu teclado; alguns lotes mudam a fileira F."))
        pag.add(aviso)
        for titulo, itens in GERAIS:
            g = Adw.PreferencesGroup(title=t(titulo))
            for comb, func in itens:
                g.add(_linha_atalho(t(comb) if comb in i18n.TRADUCOES else comb, t(func)))
            pag.add(g)
        g = Adw.PreferencesGroup(title=t("Fileira F"))
        for comb, win, mac in FILEIRA_F:
            g.add(_linha_atalho(comb, t("Windows: {w} · Mac: {m}", w=t(win), m=t(mac))))
        pag.add(g)
        g = Adw.PreferencesGroup(title=t("Luzes indicadoras"))
        for luz, texto in LUZES:
            g.add(_linha_atalho(t(luz) if luz in i18n.TRADUCOES else luz, t(texto)))
        pag.add(g)
        return pag


def _em_thread(funcao, ao_terminar):
    try:
        resultado, erro = funcao(), None
    except (ValueError, RuntimeError, OSError) as e:
        resultado, erro = None, e
    GLib.idle_add(lambda: ao_terminar(resultado, erro) and False)


def _textura_rgb565(dados):
    rgb = bytearray(len(dados) // 2 * 3)
    for i in range(0, len(dados), 2):
        v = dados[i] | dados[i + 1] << 8
        j = i // 2 * 3
        rgb[j], rgb[j + 1], rgb[j + 2] = (v >> 11) << 3, ((v >> 5) & 63) << 2, (v & 31) << 3
    lado = P.TELA_LADO
    return Gdk.MemoryTexture.new(lado, lado, Gdk.MemoryFormat.R8G8B8, GLib.Bytes.new(bytes(rgb)), lado * 3)


def _linha_atalho(combinacao, funcao):
    linha = Adw.ActionRow(title=funcao)
    rot = Gtk.Label(label=combinacao, css_classes=["dim-label", "monospace"], valign=Gtk.Align.CENTER)
    linha.add_prefix(rot)
    rot.set_size_request(200, -1)
    rot.set_xalign(0)
    return linha


def _caixa_pagina(dica):
    caixa = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_top=18, margin_bottom=18,
                    margin_start=18, margin_end=18)
    caixa.append(Gtk.Label(label=dica, css_classes=["dim-label"], margin_bottom=12))
    return caixa


def _rolavel(filho):
    clamp = Adw.Clamp(maximum_size=1100, child=filho)
    return Gtk.ScrolledWindow(child=clamp, vexpand=True)


def _nome_tecla(nome):
    from .teclado import rotulo
    t_ = POR_NOME.get(nome)
    if t_ and rotulo(t_) and rotulo(t_).upper() != nome.upper():
        return f"{rotulo(t_)} ({nome})"
    return nome.upper() if len(nome) <= 3 else nome


def _nome_acao(acao):
    if acao in A.MULTIMIDIA:
        return t(acao)
    return " + ".join(_nome_tecla(p) for p in acao.split("+"))


def salvar_idioma(codigo):
    from ..preferencias import Preferencias
    prefs = Preferencias.carregar()
    prefs.idioma = codigo
    prefs.salvar()
