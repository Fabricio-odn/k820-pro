# Capturas

Registros do que o software oficial (`DeviceDriver.exe` 1.0.0.5) mandou ao teclado, feitos com `scripts/captura/capturar.sh`. Cada linha: `<tempo unix> if<interface> <SETF|GETF|OUT|IN> <tamanho> <bytes em hex>`. Nos `SETF`, `GETF` e `OUT` o primeiro byte é o report ID 0 que o Wine põe na frente.

- `sessao1-…`: troca de efeitos de luz, Caps Lock → Ctrl e de volta, envio de um GIF de 20 quadros para a tela, tempo até dormir, restauração de fábrica.
- `sessao2-…`: Caps Lock → A, Aumentar volume, Ctrl e padrão; luz por tecla (Esc vermelho, F1 verde, F2 azul); todas as opções de sono e de tempo de resposta; restauração de fábrica.

Nada do que foi digitado entra no registro (a interface 0 nunca é gravada). Os pixels do GIF da sessão 1 foram trocados por um gradiente gerado, porque a imagem original não é nossa; o cabeçalho (número de quadros e tempos), o enquadramento em blocos e o preenchimento são os originais.
