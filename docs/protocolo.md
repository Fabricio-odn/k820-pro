# Protocolo do Ajazz AK820 Pro (0c45:800a)

Decifrado em 20/11/2026 a partir do software oficial (`DeviceDriver.exe` 1.0.0.5, o mesmo para os PIDs `8009` e `800A`), rodando no Wine com os pacotes registrados por `scripts/captura/hidlog.c` (LD_PRELOAD). As capturas estão em `captures/` e os testes em `tests/test_capturas.py` conferem byte a byte que o `k820_pro` reproduz o que o software oficial manda.

## Interfaces USB (pelo cabo)

| Interface | Usage page | Uso |
|---|---|---|
| 0 | teclado | teclas (nunca mexer) |
| 1 | consumer | teclas multimídia |
| 2 | 0xff68 | dados da tela: output report de 4096 bytes, input de 64 |
| 3 | 0xff13 | configuração: feature report de 64 bytes |

O descritor não declara report IDs, mas o primeiro byte de cada feature report funciona como um. No hidraw, um pacote que começa com 0x00 precisa de um 0x00 extra na frente (o kernel trata o primeiro byte como report ID e o descarta).

O dongle 2.4G (`0c45:fdfd`) e o driver web (ajazz.driveall.cn, protocolo `AA`/`55` com comando 0x10) não foram estudados / não funcionam com esta unidade.

## Transações (interface 3)

Pacote de controle: `04 cmd b2 00 00 00 00 00 b8 00...` (64 bytes). Depois de cada um o software faz um GET_FEATURE; a resposta ecoa o pacote com o byte 3 = 01.

| Operação | Sequência |
|---|---|
| Iluminação | `18`, `13 b8=01`, dados, `02`, `f0` |
| Teclas (camada normal) | `18`, `11 b8=09`, 9 pacotes (tabela), `02`, `f0` |
| Teclas (camada Fn) | `18`, `27 b8=09`, 9 pacotes, `02`, `f0` (só vista zerada) |
| Luz por tecla | iluminação com efeito `0x80`, depois `18`, `23 b8=09`, 9 pacotes, `02`, `f0` |
| Configurações | `18`, `17 b2=01 b8=01`, dados, `02` |
| Relógio | `18`, `28 b8=01`, dados, `02` |
| Tela | `18`, `72 b2=02 b8=nº de blocos`, blocos na interface 2, `02` |
| Restauração de fábrica | `19`, `15 b8=08`, 8 pacotes zerados, `02`, e regrava teclas, Fn, iluminação e configurações padrão |

`f5 b8=09` é uma consulta que o software repete o tempo todo enquanto está aberto; a resposta traz `00`, `01` ou `ff` no byte 3. Não é necessária.

### Iluminação (dados)

`[efeito, R, G, B, 0, 0, 0, 0, arco-íris, brilho 0-5, velocidade 0-5, direção, 0, 0, AA, 55, 0...]`. Efeitos 0x00 a 0x13 e 0x80 (personalizado, cores da tabela `23`). Padrão de fábrica: `0b` (onda), arco-íris, brilho 5, velocidade 3.

### Tabelas de 144 entradas (`11`, `27`, `23`)

576 bytes = 144 entradas de 4 bytes, mandados em 9 pacotes; os dois últimos bytes são `AA 55`. A posição de cada tecla é o `key_index`/`light_index` do layout (`k820_pro/layout.py`; Caps Lock = 55).

- **Teclas** (`11`): entrada zerada = função de fábrica. `[02, modificadores, código HID, 0]` para tecla ou atalho (Ctrl esquerdo sozinho = `02 01 00 00`); `[03, uso consumer LE, 0]` para multimídia (Aumentar volume = `03 e9 00 00`).
- **Luz por tecla** (`23`): `[índice, R, G, B]`; o índice vai preenchido em toda posição que tem tecla, mesmo sem cor.

### Configurações (dados)

`[0, b1, 0, 0, 0, b5, sono, 0, resposta, 0..., AA, 55]`. Sono: 0 = nunca, 1 = 1 min, 2 = 5 min, 3 = 30 min. Resposta: nível 1 a 5. Padrão: b1 = 1, b5 = 0, sono = 2, resposta = 2. O significado de b1 e b5 é desconhecido (b5 virou 1 numa das capturas); são repassados como observados.

### Relógio (dados)

`[0, 01, 5a, ano-2000, mês, dia, hora, minuto, segundo, 0, dia da semana (domingo = 0), 0..., AA, 55]`.

### Tela

Dados = cabeçalho de 256 bytes (`[nº de quadros, tempo de cada quadro em unidades de 2 ms...]`, completado com `ff`) + quadros de 128×128 em RGB565 little-endian, completados com `ff` até um múltiplo de 4096. Cada bloco vai como output report de 4096 bytes na interface 2, e o teclado responde `01 5a 02` em um input report antes do próximo. Até 140 quadros (`gif_maxframes` do software).
