# Segurança

## O que o programa acessa

- `/dev/hidraw*` das interfaces 2 e 3 do teclado `0c45:800a`, achadas pelo `HID_ID` e pelo número da interface. A interface 0 (as teclas digitadas) nunca é aberta.
- `~/.config/k820-pro/` (`estado.json` e `idioma`), validados ao carregar: qualquer conteúdo fora do formato gera erro, nunca é executado.
- As imagens que você escolher para a tela, com limite de 64 MB, 40 megapixels e 5000 quadros lidos.

Não há acesso à rede, nem comandos de shell, nem `sudo`. A regra udev (`udev/71-ajazz-ak820.rules`) usa `TAG+="uaccess"`, que dá acesso só ao usuário da sessão local, em vez de `MODE="0666"`, que liberaria para qualquer processo.

`scripts/captura/` é ferramenta de desenvolvimento: injeta uma biblioteca (`LD_PRELOAD`) no software oficial rodando no Wine para registrar os pacotes. Não é usada pelo programa.

## Riscos conhecidos

- Os comandos são gravados na memória do teclado. Mandar só o que o software oficial manda é a regra do projeto; um comando errado em teoria poderia deixar a configuração estranha, e o `restaurar` (ou Fn + Espaço por 3 a 5 s) volta ao padrão.
- O firmware não é atualizado nem tocado por este projeto.

## Como relatar

Abra uma issue no GitHub. Se for algo sensível, use "Report a vulnerability" na aba Security do repositório.
