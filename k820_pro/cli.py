"""Linha de comando do k820-pro."""
import argparse
import sys
from datetime import datetime

from . import acoes as A
from . import protocolo as P
from . import servico as S
from .atalhos import FILEIRA_F, GERAIS
from .i18n import TRADUCOES, t
from .dispositivo import ErroTeclado, achar_hidraw
from .estado import Estado
from .layout import TECLAS


def _cor(texto):
    t = texto.lstrip("#")
    if len(t) != 6:
        raise argparse.ArgumentTypeError(t("use 6 dígitos hexadecimais, como ff0000"))
    try:
        return tuple(int(t[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        raise argparse.ArgumentTypeError(t("cor inválida: {texto}", texto=texto)) from None


def _hora(texto):
    try:
        return datetime.strptime(texto, "%H:%M").time()
    except ValueError:
        raise argparse.ArgumentTypeError(t("use HH:MM, como 12:34")) from None


APELIDOS = {"light": "luz", "colors": "cores", "key": "tecla", "keys": "teclas", "actions": "acoes",
            "screen": "tela", "settings": "ajustes", "clock": "relogio", "reset": "restaurar",
            "shortcuts": "atalhos", "effects": "efeitos"}


def montar_parser():
    ap = argparse.ArgumentParser(prog="k820", description=t("Configura o teclado Ajazz AK820 Pro no Linux (pelo cabo USB)."))
    sub = ap.add_subparsers(dest="comando", required=True)

    luz = sub.add_parser("luz", aliases=["light"], help=t("muda o efeito de iluminação"))
    luz.add_argument("efeito", choices=list(P.EFEITOS))
    luz.add_argument("-c", "--cor", type=_cor, default=(255, 0, 0), help=t("cor em hexadecimal (padrão ff0000)"))
    luz.add_argument("-a", "--arco-iris", action="store_true", help=t("usa as cores do arco-íris em vez de uma cor só"))
    luz.add_argument("-b", "--brilho", type=int, default=P.BRILHO_MAX, help="0-5")
    luz.add_argument("-v", "--velocidade", type=int, default=3, help="0-5")
    luz.add_argument("-d", "--direcao", choices=list(P.DIRECOES), help=t("só para rolagem, onda, fluxo e inclinado"))

    cores = sub.add_parser("cores", aliases=["colors"], help=t("luz personalizada: uma cor por tecla (ex.: esc=ff0000 f1=00ff00)"))
    cores.add_argument("pares", nargs="*", metavar="tecla=rrggbb")
    cores.add_argument("--todas", type=_cor, help=t("pinta todas as teclas desta cor antes dos pares"))
    cores.add_argument("--limpar", action="store_true", help=t("apaga as cores guardadas antes de aplicar"))
    cores.add_argument("-b", "--brilho", type=int, default=P.BRILHO_MAX)

    tecla = sub.add_parser("tecla", aliases=["key"], help=t("remapeia uma tecla (ex.: k820 tecla capslock ctrl_esq)"))
    tecla.add_argument("tecla")
    tecla.add_argument("acao", help=t("tecla, atalho (ctrl_esq+c), multimídia (volume+) ou 'padrao'"))

    sub.add_parser("teclas", aliases=["keys"], help=t("lista as teclas e o remapeamento atual"))
    sub.add_parser("acoes", aliases=["actions"], help=t("lista as ações possíveis no remapeamento"))

    tela = sub.add_parser("tela", aliases=["screen"], help=t("manda uma imagem ou GIF para a tela (128x128, até 140 quadros)"))
    tela.add_argument("arquivo")
    tela.add_argument("--encaixar", action="store_true", help=t("mostra a imagem inteira com faixas pretas, em vez de cortar"))

    aj = sub.add_parser("ajustes", aliases=["settings"], help=t("tempo até dormir e tempo de resposta das teclas"))
    aj.add_argument("--sono", choices=list(P.SONO), help=t("minutos sem uso até dormir (nunca, 1, 5 ou 30)"))
    aj.add_argument("--resposta", type=int, choices=list(P.RESPOSTA_NIVEIS), help=t("nível 1 (mais rápido) a 5"))

    rel = sub.add_parser("relogio", aliases=["clock"], help=t("acerta o relógio da tela (padrão: hora do sistema)"))
    rel.add_argument("hora", nargs="?", type=_hora, help=t("HH:MM, para testar; sem isso usa a hora atual"))

    sub.add_parser("restaurar", aliases=["reset"], help=t("volta o teclado ao padrão de fábrica"))
    sub.add_parser("atalhos", aliases=["shortcuts"], help=t("lista os atalhos de fábrica do teclado (Fn + tecla)"))
    sub.add_parser("efeitos", aliases=["effects"], help=t("lista os efeitos de iluminação"))
    sub.add_parser("info", help=t("mostra onde o teclado foi encontrado e o estado guardado"))
    return ap


def main(argv=None):
    args = montar_parser().parse_args(argv)
    try:
        return _executar(args)
    except (ErroTeclado, ValueError, RuntimeError, OSError, argparse.ArgumentTypeError) as e:
        print(t("erro: {e}", e=e), file=sys.stderr)
        return 1


def _executar(args):
    c = APELIDOS.get(args.comando, args.comando)
    if c == "efeitos":
        for nome in P.EFEITOS:
            dirs = P.DIRECOES_POR_EFEITO.get(nome)
            extra = t("  (direção: {d})", d=", ".join(dirs)) if dirs else ""
            print(f"{nome:<16} {t(nome)}{extra}")
        return 0
    if c == "acoes":
        print(t("teclas:"), ", ".join(sorted(A.TECLAS_HID)))
        print(t("modificadores:"), ", ".join(A.MODIFICADORES), t("(combine com +, ex.: ctrl_esq+shift_esq+esc)"))
        print(t("multimídia:"), ", ".join(A.MULTIMIDIA))
        print(t("padrao: devolve a função de fábrica"))
        return 0
    if c == "atalhos":
        for grupo, itens in GERAIS:
            print(f"\n{t(grupo)}")
            for comb, func in itens:
                print(f"  {t(comb) if comb in TRADUCOES else comb:<28} {t(func)}")
        print(f"\n{t('Fileira F')} (Windows | Mac)")
        for comb, win, mac in FILEIRA_F:
            print(f"  {comb:<10} {t(win):<22} | {t(mac)}")
        return 0
    estado = Estado.carregar()
    if c == "teclas":
        for tec in TECLAS:
            extra = f"  -> {estado.teclas[tec.nome]}" if tec.nome in estado.teclas else ""
            print(f"{tec.nome}{extra}")
        return 0
    if c == "info":
        print(t("AK820 Pro encontrado em {c} (interface 3)", c=achar_hidraw()))
        print(t("teclas remapeadas: {m}", m=estado.teclas or t("nenhuma")))
        print(t("ajustes: sono {s}, resposta nível {r}", s=estado.ajustes.sono, r=estado.ajustes.resposta))
        return 0

    if c == "luz":
        direcao = args.direcao or P.DIRECOES_POR_EFEITO.get(args.efeito, ("esquerda",))[0]
        S.aplicar_luz(P.Iluminacao(args.efeito, args.cor, args.arco_iris, args.brilho, args.velocidade, direcao))
        print(t("ok, iluminação: {e}", e=t(args.efeito)))

    elif c == "cores":
        cores = {} if args.limpar else dict(estado.cores)
        if args.todas:
            cores = {t.nome: "%02x%02x%02x" % args.todas for t in TECLAS}
        for par in args.pares:
            nome, _, cor = par.partition("=")
            cores[nome] = cor
        S.aplicar_cores(estado, cores, args.brilho)
        print(t("ok, luz personalizada com {n} tecla(s) colorida(s)", n=len(estado.cores)))

    elif c == "tecla":
        S.remapear(estado, args.tecla, args.acao.lower())
        print(f"ok, {args.tecla} -> {args.acao}")

    elif c == "tela":
        def progresso(i, n):
            print("\r" + t("enviando {i}/{n} blocos", i=i, n=n), end="", file=sys.stderr, flush=True)

        n = S.enviar_tela(args.arquivo, "encaixar" if args.encaixar else "cortar", progresso)
        print("\n" + t("Enviado: {n} quadro(s)", n=n))

    elif c == "ajustes":
        if args.sono is None and args.resposta is None:
            raise ValueError("diga --sono e/ou --resposta")
        S.aplicar_ajustes(estado, **{k: v for k, v in (("sono", args.sono), ("resposta", args.resposta)) if v is not None})
        print(t("ajustes: sono {s}, resposta nível {r}", s=estado.ajustes.sono, r=estado.ajustes.resposta))

    elif c == "relogio":
        agora = datetime.now()
        momento = agora.replace(hour=args.hora.hour, minute=args.hora.minute, second=0) if args.hora else agora
        S.acertar_relogio(momento)
        print(t("Relógio acertado") + f": {momento:%Y-%m-%d %H:%M:%S}")

    elif c == "restaurar":
        S.restaurar(estado)
        print(t("Teclado restaurado"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
