# Segurança

## O que o programa acessa

- `/dev/hidraw*` das interfaces 2 e 3 do teclado `0c45:800a` e da interface 3 do dongle `0c45:fdfd`, achadas pelo `HID_ID` e pelo número da interface. As interfaces por onde passam as teclas digitadas (0 no teclado; 0, 1 e 2 no dongle) nunca são abertas nem liberadas pela regra udev.
- `~/.config/k820-pro/` (`estado.json` e `idioma`), validados ao carregar: qualquer conteúdo fora do formato gera erro, nunca é executado.
- As imagens que você escolher para a tela, com limite de 64 MB, 40 megapixels e 5000 quadros lidos.

Não há acesso à rede, nem comandos de shell, nem `sudo`. A regra udev (`udev/69-ajazz-ak820.rules`) usa `TAG+="uaccess"`, que dá acesso só ao usuário da sessão local, em vez de `MODE="0666"`, que liberaria para qualquer processo.

### Atenção: o teclado é confundido com uma câmera

O banco de dados do `libgphoto2` (instalado por padrão no Fedora e no Ubuntu) cadastra `0c45:800a` como a câmera "Vivitar Vivicam 3350B". Por causa disso, a regra `70-uaccess.rules` do systemd libera para o usuário logado o dispositivo USB inteiro e o hidraw da interface 0, por onde passa tudo o que é digitado: qualquer programa rodando com o seu usuário consegue ler o teclado, mesmo no Wayland. Isso acontece **com ou sem este projeto**. A regra udev do projeto roda antes do `70-uaccess.rules` e apaga a marca de câmera (`ID_GPHOTO2`) do teclado, deixando liberadas só as interfaces de configuração. Tirar a tag depois não resolve: o logind refaz as permissões a partir das tags que o dispositivo já teve. Para conferir, depois de instalar a regra e reconectar o cabo: `getfacl /dev/hidrawN` da interface 0 não deve listar o seu usuário.

`scripts/captura/` é ferramenta de desenvolvimento: injeta uma biblioteca (`LD_PRELOAD`) no software oficial rodando no Wine para registrar os pacotes. Não é usada pelo programa.

## Riscos conhecidos

- Os comandos são gravados na memória do teclado. Mandar só o que o software oficial manda é a regra do projeto; um comando errado em teoria poderia deixar a configuração estranha, e o `restaurar` (ou Fn + Espaço por 3 a 5 s) volta ao padrão.
- O firmware não é atualizado nem tocado por este projeto.

## Como relatar

Abra uma issue no GitHub. Se for algo sensível, use "Report a vulnerability" na aba Security do repositório.
