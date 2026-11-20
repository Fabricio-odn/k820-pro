"""Página Tela: imagem ou GIF para a telinha, com a prévia já em 128×128."""
import threading
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gio, GLib, Gtk  # noqa: E402

from ... import protocolo as P  # noqa: E402
from ... import servico as S  # noqa: E402
from ...i18n import t  # noqa: E402
from ..componentes import Colunas, cabecalho_pagina, cartao, secao, segmentado  # noqa: E402


def textura_rgb565(dados):
    rgb = bytearray(len(dados) // 2 * 3)
    for i in range(0, len(dados), 2):
        v = dados[i] | dados[i + 1] << 8
        j = i // 2 * 3
        rgb[j], rgb[j + 1], rgb[j + 2] = (v >> 11) << 3, ((v >> 5) & 63) << 2, (v & 31) << 3
    lado = P.TELA_LADO
    return Gdk.MemoryTexture.new(lado, lado, Gdk.MemoryFormat.R8G8B8, GLib.Bytes.new(bytes(rgb)), lado * 3)


class PaginaTela(Gtk.Box):
    def __init__(self, janela):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.janela = janela
        self.arquivo = None
        self._quadros, self._animacao = [], 0
        self.append(cabecalho_pagina(t("Tela"), t("Até 140 quadros. Leva uns 20 segundos.")))

        self.previa = Gtk.Picture(content_fit=Gtk.ContentFit.CONTAIN, width_request=256, height_request=256,
                                  halign=Gtk.Align.CENTER, can_shrink=True)
        moldura = Gtk.Box(halign=Gtk.Align.CENTER)
        moldura.add_css_class("moldura-tela")
        moldura.append(self.previa)
        self.legenda = Gtk.Label(label=t("Nenhum arquivo escolhido"))
        self.legenda.add_css_class("secundario")
        self.legenda.add_css_class("caption")
        caixa = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        caixa.append(moldura)
        caixa.append(self.legenda)
        esquerda = cartao(caixa)

        direita = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=22)
        escolher = Gtk.Button(label=t("Escolher arquivo…"))
        escolher.connect("clicked", lambda *_: self._escolher())
        direita.append(secao(t("Imagem ou GIF"), escolher))
        self.modo = segmentado([("cortar", t("Preencher")), ("encaixar", t("Imagem inteira"))],
                               lambda _m: self._carregar_previa())
        self.modo.set_active_name("cortar")
        direita.append(secao(t("Enquadramento"), self.modo,
                             t("Sem isso, a imagem é cortada para preencher a tela 128×128.")))
        self.progresso = Gtk.ProgressBar(show_text=True, visible=False)
        direita.append(self.progresso)
        self.enviar = Gtk.Button(label=t("Enviar para a tela"), sensitive=False, halign=Gtk.Align.START)
        self.enviar.add_css_class("suggested-action")
        self.enviar.add_css_class("pill")
        self.enviar.connect("clicked", lambda *_: self._enviar())
        direita.append(self.enviar)
        self.colunas = Colunas(esquerda, direita, 340)
        self.append(self.colunas)

    def teclados(self):
        return []

    def definir_empilhado(self, empilhado):
        self.colunas.definir_empilhado(empilhado)

    def ao_sair(self):
        pass

    def _escolher(self):
        filtro = Gtk.FileFilter(name=t("Imagens"))
        for tipo in ("image/gif", "image/png", "image/jpeg", "image/webp", "image/bmp"):
            filtro.add_mime_type(tipo)
        filtros = Gio.ListStore.new(Gtk.FileFilter)
        filtros.append(filtro)

        def pronto(d, res):
            try:
                arquivo = d.open_finish(res)
            except GLib.Error:
                return
            self.arquivo = arquivo.get_path()
            self._carregar_previa()

        Gtk.FileDialog(filters=filtros).open(self.get_root(), None, pronto)

    def _carregar_previa(self):
        if not self.arquivo:
            return
        caminho, modo = self.arquivo, self.modo.get_active_name()

        def carregar():
            from ... import imagem
            quadros, tempos = imagem.carregar(caminho, modo)
            return [textura_rgb565(q) for q in quadros], tempos

        def pronto(resultado, erro):
            if erro:
                self.janela.avisar(t("Erro: {erro}", erro=erro))
                self.enviar.set_sensitive(False)
                return
            self._quadros = list(zip(*resultado))
            self._animacao += 1
            self.legenda.set_label(t("{arquivo} · {n} quadro(s)", arquivo=Path(caminho).name, n=len(self._quadros)))
            self.enviar.set_sensitive(True)
            self._tocar(self._animacao, 0)

        threading.Thread(target=lambda: _em_thread(carregar, pronto), daemon=True).start()

    def _tocar(self, animacao, i):
        if animacao != self._animacao or not self._quadros:
            return False
        textura, ms = self._quadros[i % len(self._quadros)]
        self.previa.set_paintable(textura)
        if len(self._quadros) > 1:
            GLib.timeout_add(max(20, ms), self._tocar, animacao, i + 1)
        return False

    def _enviar(self):
        caminho, modo = self.arquivo, self.modo.get_active_name()
        self.enviar.set_sensitive(False)
        self.progresso.set_visible(True)
        self.progresso.set_fraction(0)

        def progresso(i, n):
            GLib.idle_add(self.progresso.set_fraction, i / n)

        def depois(_erro):
            self.enviar.set_sensitive(True)
            self.progresso.set_visible(False)

        self.janela.executar(lambda: S.enviar_tela(caminho, modo, progresso),
                             sucesso=lambda n: t("Enviado: {n} quadro(s)", n=n), depois=depois)


def _em_thread(funcao, ao_terminar):
    try:
        resultado, erro = funcao(), None
    except (ValueError, RuntimeError, OSError) as e:
        resultado, erro = None, e
    GLib.idle_add(lambda: ao_terminar(resultado, erro) and False)
