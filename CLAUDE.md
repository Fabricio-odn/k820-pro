# k820-pro

Ferramenta Linux própria para o teclado Ajazz AK820 Pro (`0c45:800a`, SONiX), no molde do `~/Projetos/Pessoais/dazz-mouse`. O protocolo veio do projeto github.com/gohv/EPOMAKER-Ajazz-AK820-Pro (MIT, PID 8009) e de testes no teclado.

## Regras

- Escreva tudo em português: código comentado, docs e mensagens de commit (Conventional Commits).
- Canal de configuração: feature report de 64 bytes na **interface 3** (hidraw). Ache o hidraw pelo `HID_ID` (`0003:00000C45:0000800A`) e pelo `bInterfaceNumber`, nunca por número fixo.
- Se o primeiro byte do pacote for 0x00, o kernel o remove (trata como report ID): `preparar_buffer` prefixa um 0x00 extra.
- **Só mande bytes observados** no software original ou no projeto de referência. Comandos novos (imagem da tela no 800a, remapeamento) só depois de capturar o tráfego do programa oficial no Windows, e com o mantenedor ciente antes.
- O driver web (ajazz.driveall.cn, protocolo AA/55 na interface 2) **não** funciona com esta unidade; o comando 0x10 fica sem resposta.
- O protocolo está em `docs/protocolo.md`; os testes de `tests/test_capturas.py` comparam com `captures/*.log`. Para descobrir algo novo, rode `scripts/captura/capturar.sh` (software oficial no Wine, com registro via LD_PRELOAD) e peça ao mantenedor para fazer a ação.
- A referência do gohv tinha erros (delimitador 55 AA, sono no byte errado, blocos de imagem de 4123 bytes); confie nas capturas.
- Pelo dongle 2.4G (`0c45:fdfd`) o protocolo não foi estudado.
- Capturas vão para `captures/` com nome que diga as ações feitas.
- Acessar `/dev/hidraw*` precisa da regra udev (`scripts/instalar-udev.sh`). Peça antes de usar `sudo`.
