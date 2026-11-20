"""Teclas físicas do AK820 Pro ANSI (81 teclas), tiradas de layouts/rgb-keyboard.xml do
software oficial 1.0.0.5 (índices, códigos e a geometria do desenho).

`indice` é a posição da tecla nas tabelas de 144 entradas de 4 bytes (remapeamento e
luz por tecla; no layout, key_index e light_index são iguais). `codigo` é o código HID
que a tecla manda de fábrica.
"""
from typing import NamedTuple


class Tecla(NamedTuple):
    nome: str
    codigo: int
    indice: int
    linha: int
    coluna: int
    x: int = 0       # posição e tamanho no desenho do software oficial (pixels)
    y: int = 0
    largura: int = 28
    altura: int = 28


TECLAS = [
    Tecla('esc', 0x29, 1, 0, 0, 95, 22, 28, 28),
    Tecla('f1', 0x3a, 2, 0, 1, 141, 22, 28, 28),
    Tecla('f2', 0x3b, 3, 0, 2, 179, 22, 28, 28),
    Tecla('f3', 0x3c, 4, 0, 3, 217, 22, 28, 28),
    Tecla('f4', 0x3d, 5, 0, 5, 255, 22, 28, 28),
    Tecla('f5', 0x3e, 6, 0, 6, 302, 22, 28, 28),
    Tecla('f6', 0x3f, 7, 0, 7, 339, 22, 28, 28),
    Tecla('f7', 0x40, 8, 0, 8, 377, 22, 28, 28),
    Tecla('f8', 0x41, 9, 0, 9, 415, 22, 28, 28),
    Tecla('f9', 0x42, 10, 0, 10, 462, 22, 28, 28),
    Tecla('f10', 0x43, 11, 0, 11, 500, 22, 28, 28),
    Tecla('f11', 0x44, 12, 0, 12, 538, 22, 28, 28),
    Tecla('f12', 0x45, 13, 0, 13, 576, 22, 28, 28),
    Tecla('delete', 0x4c, 119, 0, 14, 623, 22, 28, 28),
    Tecla('grave', 0x35, 19, 1, 0, 95, 69, 28, 28),
    Tecla('1', 0x1e, 20, 1, 1, 132, 69, 28, 28),
    Tecla('2', 0x1f, 21, 1, 2, 170, 69, 28, 28),
    Tecla('3', 0x20, 22, 1, 3, 208, 69, 28, 28),
    Tecla('4', 0x21, 23, 1, 4, 246, 69, 28, 28),
    Tecla('5', 0x22, 24, 1, 5, 283, 69, 28, 28),
    Tecla('6', 0x23, 25, 1, 6, 321, 69, 28, 28),
    Tecla('7', 0x24, 26, 1, 7, 359, 69, 28, 28),
    Tecla('8', 0x25, 27, 1, 8, 397, 69, 28, 28),
    Tecla('9', 0x26, 28, 1, 9, 434, 69, 28, 28),
    Tecla('0', 0x27, 29, 1, 10, 472, 69, 28, 28),
    Tecla('menos', 0x2d, 30, 1, 11, 510, 69, 28, 28),
    Tecla('igual', 0x2e, 31, 1, 12, 547, 69, 28, 28),
    Tecla('backspace', 0x2a, 103, 1, 14, 585, 69, 66, 28),
    Tecla('home', 0x4a, 117, 1, 15, 677, 69, 28, 28),
    Tecla('tab', 0x2b, 37, 2, 0, 95, 108, 46, 28),
    Tecla('q', 0x14, 38, 2, 1, 151, 108, 28, 28),
    Tecla('w', 0x1a, 39, 2, 2, 189, 108, 28, 28),
    Tecla('e', 0x08, 40, 2, 3, 227, 108, 28, 28),
    Tecla('r', 0x15, 41, 2, 4, 265, 108, 28, 28),
    Tecla('t', 0x17, 42, 2, 5, 302, 108, 28, 28),
    Tecla('y', 0x1c, 43, 2, 6, 340, 108, 28, 28),
    Tecla('u', 0x18, 44, 2, 7, 378, 108, 28, 28),
    Tecla('i', 0x0c, 45, 2, 8, 416, 108, 28, 28),
    Tecla('o', 0x12, 46, 2, 9, 453, 108, 28, 28),
    Tecla('p', 0x13, 47, 2, 10, 491, 108, 28, 28),
    Tecla('colchete_esq', 0x2f, 48, 2, 11, 529, 108, 28, 28),
    Tecla('colchete_dir', 0x30, 49, 2, 12, 566, 108, 28, 28),
    Tecla('barra_invertida', 0x31, 67, 2, 14, 604, 108, 47, 28),
    Tecla('pgup', 0x4b, 118, 2, 15, 677, 108, 28, 28),
    Tecla('capslock', 0x39, 55, 3, 0, 95, 145, 55, 28),
    Tecla('a', 0x04, 56, 3, 2, 160, 145, 28, 28),
    Tecla('s', 0x16, 57, 3, 3, 198, 145, 28, 28),
    Tecla('d', 0x07, 58, 3, 4, 236, 145, 28, 28),
    Tecla('f', 0x09, 59, 3, 5, 274, 145, 28, 28),
    Tecla('g', 0x0a, 60, 3, 6, 312, 145, 28, 28),
    Tecla('h', 0x0b, 61, 3, 7, 350, 145, 28, 28),
    Tecla('j', 0x0d, 62, 3, 8, 387, 145, 28, 28),
    Tecla('k', 0x0e, 63, 3, 9, 425, 145, 28, 28),
    Tecla('l', 0x0f, 64, 3, 10, 462, 145, 28, 28),
    Tecla('ponto_virgula', 0x33, 65, 3, 11, 500, 145, 28, 28),
    Tecla('aspas', 0x34, 66, 3, 12, 538, 145, 28, 28),
    Tecla('enter', 0x28, 85, 3, 14, 576, 145, 75, 28),
    Tecla('pgdn', 0x4e, 121, 3, 15, 677, 145, 28, 28),
    Tecla('shift_esq', 0xe1, 73, 4, 0, 95, 183, 75, 28),
    Tecla('z', 0x1d, 74, 4, 2, 179, 183, 28, 28),
    Tecla('x', 0x1b, 75, 4, 3, 217, 183, 28, 28),
    Tecla('c', 0x06, 76, 4, 4, 255, 183, 28, 28),
    Tecla('v', 0x19, 77, 4, 5, 292, 183, 28, 28),
    Tecla('b', 0x05, 78, 4, 6, 330, 183, 28, 28),
    Tecla('n', 0x11, 79, 4, 7, 368, 183, 28, 28),
    Tecla('m', 0x10, 80, 4, 8, 406, 183, 28, 28),
    Tecla('virgula', 0x36, 81, 4, 9, 443, 183, 28, 28),
    Tecla('ponto', 0x37, 82, 4, 10, 481, 183, 28, 28),
    Tecla('barra', 0x38, 83, 4, 11, 519, 183, 28, 28),
    Tecla('shift_dir', 0xe5, 84, 4, 14, 557, 183, 55, 28),
    Tecla('cima', 0x52, 101, 4, 16, 631, 192, 28, 28),
    Tecla('ctrl_esq', 0xe0, 91, 5, 0, 95, 221, 37, 28),
    Tecla('win', 0xe3, 92, 5, 1, 142, 221, 37, 28),
    Tecla('alt_esq', 0xe2, 93, 5, 3, 189, 221, 37, 28),
    Tecla('espaco', 0x2c, 94, 5, 6, 236, 221, 225, 28),
    Tecla('alt_dir', 0xe6, 95, 5, 10, 472, 221, 28, 28),
    Tecla('fn', 0xaf, 96, 5, 12, 510, 221, 28, 28),
    Tecla('ctrl_dir', 0xe4, 98, 5, 14, 548, 221, 28, 28),
    Tecla('esquerda', 0x50, 99, 5, 15, 594, 230, 28, 28),
    Tecla('baixo', 0x51, 100, 5, 16, 631, 230, 28, 28),
    Tecla('direita', 0x4f, 102, 5, 17, 669, 230, 28, 28),
]

POR_NOME = {t.nome: t for t in TECLAS}
