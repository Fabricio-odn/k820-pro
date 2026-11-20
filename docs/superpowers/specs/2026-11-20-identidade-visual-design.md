# Identidade visual do K820 Pro Studio

## Intenção

O app está público e outras pessoas vão usar. Ele precisa de nome, ícone e visual próprios, com a mesma linguagem do `dazz-mouse` (o outro configurador do Fabrício), e sem parecer feito só para a versão cinza e amarela do teclado.

## Decisões do Fabrício

- **Nome:** K820 Pro Studio. ID do app continua `io.github.k820pro.Configurador`.
- **Visual:** igual ao `dazz-mouse`, escuro, preto e branco, sem cor de destaque. A seleção é branca com texto preto. As únicas cores na tela são as de conteúdo.
- **Versão do teclado:** a pessoa escolhe qual tem, e o app desenha o teclado com aquelas cores.
- **Tema claro e escuro:** um botão no cabeçalho alterna entre os dois; o escuro é o padrão. Os dois seguem a mesma regra de preto e branco.

## Abordagens consideradas

- **A. Como o teclado (cinza + amarelo de destaque):** identidade forte, mas o amarelo não combina com quem tem outra versão. Descartada.
- **B. Preto e branco como o `dazz-mouse`:** neutro para todas as versões, mesma família visual dos dois apps. **Escolhida.**
- **C. Destaque do sistema (padrão GNOME):** genérico, sem identidade. Descartada.

## Design

- **Tema escuro** (`k820_pro/gui/estilo.css`): as mesmas variáveis do `dazz-mouse` (fundo #0E0E10, cabeçalho #141417, cartões #1B1B1F, borda #2B2B30, destaque #FFFFFF com texto #0E0E10), carregado acima da prioridade de usuário. O aviso da faixa e o botão de restaurar continuam vermelhos (erro/destrutivo).
- **Tema claro** (`estilo-claro.css`): o espelho em preto e branco (fundo #FAFAFA, cabeçalho #F0F0F2, cartões #FFFFFF, borda #DCDCE0, destaque #0E0E10 com texto #FFFFFF). O botão no cabeçalho troca o esquema da libadwaita e a folha de estilo na hora, sem reiniciar, e a escolha fica salva em `~/.config/k820-pro/`. O desenho do teclado tem contorno e fundo da área ajustados a cada tema; as cores do teclado, da luz e do GIF não mudam.
- **Versões do teclado:** cinza e amarelo, branco e roxo, preto, branco, e "neutro" (o padrão atual). Cada versão define a cor do corpo, das teclas comuns, das teclas de destaque (Esc, Enter, setas etc., conforme a versão) e do texto. A escolha fica em Ajustes, é salva em `~/.config/k820-pro/` e muda o desenho nas abas Cores por tecla e Teclas. A prévia de luz continua mostrando as cores da luz.
- **Ícone:** no estilo do `dazz-mouse`: um AK820 visto de cima em cinza-escuro, com a borda frontal mostrando o LED arco-íris (a profundidade que o guia do GNOME pede) e a telinha acesa no canto. Mais uma versão simbólica, monocromática, para tamanhos pequenos.
- **Nome nos textos:** título da janela, atalho do menu, README e descrição do repositório passam a dizer "K820 Pro Studio". O README ganha a nota de projeto independente, sem relação com a Ajazz.

## Fora do escopo

- Detectar a versão sozinho: o USB não informa a cor, então a escolha é manual.

## Deixado para quem implementar

- As cores exatas de cada versão (tiradas das fotos oficiais da Ajazz).
- Quais teclas são "de destaque" em cada versão.
