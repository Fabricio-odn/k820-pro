"""Atalhos de fábrica do AK820 Pro (feitos pelo firmware, sem software).

Fonte: o manual do AK820 Pro com tela, reproduzido pela revenda mirdomov.by
("conteúdo fornecido pelo fabricante AJAZZ"). Não foi possível abrir o PDF oficial,
então confira no seu teclado; alguns modelos trocam a ordem do F1 ao F12.
"""

GERAIS = [
    ("Iluminação", [
        ("Fn + \\", "Troca entre os 20 efeitos de luz"),
        ("Fn + ↑ / Fn + ↓", "Aumenta / diminui o brilho"),
        ("Fn + + / Fn + -", "Acelera / desacelera o efeito"),
        ("Fn + →", "Muda a direção do efeito"),
        ("Fn + ←", "Troca a cor da luz"),
        ("Fn + X", "Liga / desliga a luz"),
        ("Fn + 1 / 2 / 3", "Escolhe um dos três grupos de luz do usuário"),
        ("Fn + ~", "Grava a luz atual no grupo escolhido (segure para apagar a gravação)"),
    ]),
    ("Conexão", [
        ("Fn + Q / W / E", "Bluetooth 1, 2 ou 3 (toque troca; segure 3 s para parear)"),
        ("Fn + R", "2.4 GHz (segure 3 s para parear com o dongle)"),
        ("Cabo USB", "Modo com fio: automático ao ligar o cabo"),
    ]),
    ("Tela e botão giratório", [
        ("Girar o botão", "Volume - / volume +"),
        ("Apertar o botão", "Mudo / tira o mudo"),
        ("Fn + apertar o botão", "Menu de ajustes da tela (gira para navegar, aperta para confirmar); "
                                 "é por ele que se troca entre Windows e Mac, em System"),
        ("Fn + Home", "Animação da tela / volta à tela principal"),
        ("Fn + Del", "Liga / desliga a tela"),
    ]),
    ("Sistema", [
        ("Fn + Win", "Trava a tecla Windows (luz W acesa)"),
        ("Fn + PgUp", "Print Screen"),
        ("Fn + PgDn", "Break"),
        ("Fn + Espaço (segure 3 a 5 s)", "Volta ao padrão de fábrica"),
    ]),
]

# (tecla, no modo Windows, no modo Mac)
FILEIRA_F = [
    ("Fn + F1", "Player de mídia", "Diminui o brilho da tela"),
    ("Fn + F2", "Volume -", "Aumenta o brilho da tela"),
    ("Fn + F3", "Volume +", "Mission Control"),
    ("Fn + F4", "Mudo", "Launchpad"),
    ("Fn + F5", "Parar", "Diminui a luz do teclado"),
    ("Fn + F6", "Faixa anterior", "Aumenta a luz do teclado (o manual repete \"diminui\", provável erro)"),
    ("Fn + F7", "Tocar / pausar", "Faixa anterior"),
    ("Fn + F8", "Próxima faixa", "Tocar / pausar"),
    ("Fn + F9", "E-mail", "Próxima faixa"),
    ("Fn + F10", "Navegador", "Mudo"),
    ("Fn + F11", "Meu computador", "Volume -"),
    ("Fn + F12", "Calculadora", "Volume +"),
]

LUZES = [
    ("C", "Caps Lock ligado"),
    ("W", "Tecla Windows travada"),
    ("Carga", "Vermelho piscando: bateria fraca; vermelho fixo: carregando; verde: carregada"),
]
