"""Idiomas: português (original), inglês e chinês simplificado.

Os textos ficam escritos em português no código, dentro de t("..."); este módulo
devolve a tradução do idioma ativo. O idioma vem de K820_IDIOMA, ou de
LC_ALL/LC_MESSAGES/LANG, ou da escolha salva pela interface. Um teste confere que
todo t("...") do projeto tem tradução nos três idiomas.
"""
import os

IDIOMAS = {"pt": "Português", "en": "English", "zh": "中文"}

_ativo = None


def detectar():
    for var in ("K820_IDIOMA", "LC_ALL", "LC_MESSAGES", "LANG"):
        v = os.environ.get(var, "").lower()
        if v:
            for codigo in IDIOMAS:
                if v.startswith(codigo):
                    return codigo
            if var != "K820_IDIOMA":
                return "en"  # outro idioma do sistema: inglês é o mais provável de ser entendido
    return "en"


def definir(codigo):
    global _ativo
    if codigo not in IDIOMAS:
        raise ValueError(f"idioma desconhecido: {codigo}")
    _ativo = codigo


def ativo():
    global _ativo
    if _ativo is None:
        _ativo = detectar()
    return _ativo


def t(texto, **campos):
    idioma = ativo()
    # em português o texto já é o original, a não ser que seja uma chave interna
    # (efeito, ação multimídia) com rótulo próprio em "pt"
    traduzido = TRADUCOES.get(texto, {}).get(idioma, texto)
    return traduzido.format(**campos) if campos else traduzido


# português -> {en, zh}
TRADUCOES = {
    # janela e abas
    "Iluminação": {"en": "Lighting", "zh": "灯光"},
    "Cores por tecla": {"en": "Per-key colors", "zh": "单键颜色"},
    "Teclas": {"en": "Keys", "zh": "按键"},
    "Tela": {"en": "Screen", "zh": "屏幕"},
    "Ajustes": {"en": "Settings", "zh": "设置"},
    "Atalhos": {"en": "Shortcuts", "zh": "快捷键"},
    "Idioma": {"en": "Language", "zh": "语言"},
    "Teclado conectado pelo cabo": {"en": "Keyboard connected by cable", "zh": "键盘已通过数据线连接"},
    "Teclado não encontrado. Ligue o AK820 Pro pelo cabo USB.": {
        "en": "Keyboard not found. Connect the AK820 Pro with the USB cable.",
        "zh": "未找到键盘。请用 USB 数据线连接 AK820 Pro。"},
    "Aplicar": {"en": "Apply", "zh": "应用"},
    "Aplicado": {"en": "Applied", "zh": "已应用"},
    "Erro: {erro}": {"en": "Error: {erro}", "zh": "错误：{erro}"},
    "Enviando…": {"en": "Sending…", "zh": "发送中…"},
    "Reinicie o programa para trocar o idioma.": {
        "en": "Restart the program to change the language.", "zh": "重新启动程序以切换语言。"},
    # iluminação
    "Efeito": {"en": "Effect", "zh": "效果"},
    "Cor": {"en": "Color", "zh": "颜色"},
    "Arco-íris": {"en": "Rainbow", "zh": "彩虹"},
    "Brilho": {"en": "Brightness", "zh": "亮度"},
    "Velocidade": {"en": "Speed", "zh": "速度"},
    "Direção": {"en": "Direction", "zh": "方向"},
    "Só para rolagem, onda, fluxo e inclinado": {
        "en": "Only for scrolling, wave, flow and tilt", "zh": "仅适用于滚动、波浪、流动和倾斜"},
    "desligado": {"pt": "Desligado", "en": "off", "zh": "关闭"},
    "estatico": {"pt": "Estático", "en": "static", "zh": "常亮"},
    "acende-ao-tocar": {"pt": "Acende ao tocar", "en": "light on press", "zh": "按下点亮"},
    "apaga-ao-tocar": {"pt": "Apaga ao tocar", "en": "dim on press", "zh": "按下熄灭"},
    "cintilante": {"pt": "Cintilante", "en": "glittering", "zh": "闪烁"},
    "chuva": {"pt": "Chuva", "en": "falling", "zh": "雨滴"},
    "colorido": {"pt": "Colorido", "en": "colorful", "zh": "缤纷"},
    "respiracao": {"pt": "Respiração", "en": "breathing", "zh": "呼吸"},
    "espectro": {"pt": "Espectro", "en": "spectrum", "zh": "光谱"},
    "do-centro": {"pt": "Do centro", "en": "outward", "zh": "向外扩散"},
    "rolagem": {"pt": "Rolagem", "en": "scrolling", "zh": "滚动"},
    "onda": {"pt": "Onda", "en": "wave", "zh": "波浪"},
    "giro": {"pt": "Giro", "en": "rotating", "zh": "旋转"},
    "explosao": {"pt": "Explosão", "en": "explode", "zh": "爆炸"},
    "lancamento": {"pt": "Lançamento", "en": "launch", "zh": "发射"},
    "ondulacao": {"pt": "Ondulação", "en": "ripples", "zh": "涟漪"},
    "fluxo": {"pt": "Fluxo", "en": "flowing", "zh": "流动"},
    "pulsar": {"pt": "Pulsar", "en": "pulsating", "zh": "脉冲"},
    "inclinado": {"pt": "Inclinado", "en": "tilt", "zh": "倾斜"},
    "vaivem": {"pt": "Vaivém", "en": "shuttle", "zh": "穿梭"},
    "esquerda": {"pt": "Esquerda", "en": "left", "zh": "左"},
    "direita": {"pt": "Direita", "en": "right", "zh": "右"},
    "cima": {"pt": "Cima", "en": "up", "zh": "上"},
    "baixo": {"pt": "Baixo", "en": "down", "zh": "下"},
    # cores por tecla
    "Clique nas teclas para selecionar; depois escolha a cor e pinte.": {
        "en": "Click keys to select them, then pick a color and paint.", "zh": "点击按键进行选择，然后选择颜色并涂色。"},
    "Pintar selecionadas": {"en": "Paint selected", "zh": "涂选中按键"},
    "Pintar todas": {"en": "Paint all", "zh": "全部涂色"},
    "Apagar selecionadas": {"en": "Clear selected", "zh": "清除选中"},
    "Limpar seleção": {"en": "Clear selection", "zh": "取消选择"},
    # teclas
    "Clique numa tecla e escolha o que ela deve fazer.": {
        "en": "Click a key and choose what it should do.", "zh": "点击一个按键，然后选择它的功能。"},
    "Tecla selecionada": {"en": "Selected key", "zh": "已选按键"},
    "nenhuma": {"en": "none", "zh": "无"},
    "Tipo": {"en": "Type", "zh": "类型"},
    "Padrão de fábrica": {"en": "Factory default", "zh": "出厂默认"},
    "Tecla ou atalho": {"en": "Key or shortcut", "zh": "按键或组合键"},
    "Multimídia": {"en": "Multimedia", "zh": "多媒体"},
    "Ação": {"en": "Action", "zh": "功能"},
    "Modificadores": {"en": "Modifiers", "zh": "修饰键"},
    "Remapear": {"en": "Remap", "zh": "重新映射"},
    "Teclas remapeadas": {"en": "Remapped keys", "zh": "已映射的按键"},
    "Nenhuma tecla remapeada": {"en": "No remapped keys", "zh": "没有已映射的按键"},
    "Voltar ao padrão": {"en": "Reset to default", "zh": "恢复默认"},
    "A tecla Fn não pode ser remapeada": {"en": "The Fn key cannot be remapped", "zh": "Fn 键不能重新映射"},
    "volume+": {"pt": "Aumentar volume", "en": "volume up", "zh": "音量+"},
    "volume-": {"pt": "Diminuir volume", "en": "volume down", "zh": "音量-"},
    "mudo": {"pt": "Mudo", "en": "mute", "zh": "静音"},
    "play-pause": {"pt": "Tocar / pausar", "en": "play/pause", "zh": "播放/暂停"},
    "proxima": {"pt": "Próxima faixa", "en": "next track", "zh": "下一曲"},
    "anterior": {"pt": "Faixa anterior", "en": "previous track", "zh": "上一曲"},
    "parar": {"pt": "Parar", "en": "stop", "zh": "停止"},
    "brilho+": {"pt": "Brilho da tela +", "en": "screen brightness up", "zh": "屏幕亮度+"},
    "brilho-": {"pt": "Brilho da tela -", "en": "screen brightness down", "zh": "屏幕亮度-"},
    "email": {"pt": "E-mail", "en": "e-mail", "zh": "邮件"},
    "calculadora": {"pt": "Calculadora", "en": "calculator", "zh": "计算器"},
    "meu-computador": {"pt": "Meu computador", "en": "my computer", "zh": "我的电脑"},
    "navegador": {"pt": "Navegador", "en": "browser", "zh": "浏览器"},
    "web-pesquisar": {"pt": "Pesquisar (web)", "en": "web search", "zh": "网页搜索"},
    "web-inicio": {"pt": "Página inicial (web)", "en": "web home", "zh": "网页主页"},
    "web-voltar": {"pt": "Voltar (web)", "en": "web back", "zh": "网页后退"},
    "web-avancar": {"pt": "Avançar (web)", "en": "web forward", "zh": "网页前进"},
    "web-parar": {"pt": "Parar (web)", "en": "web stop", "zh": "网页停止"},
    "web-atualizar": {"pt": "Atualizar (web)", "en": "web refresh", "zh": "网页刷新"},
    "web-favoritos": {"pt": "Favoritos (web)", "en": "web favorites", "zh": "网页收藏夹"},
    # tela
    "Imagem ou GIF": {"en": "Image or GIF", "zh": "图片或 GIF"},
    "Escolher arquivo…": {"en": "Choose file…", "zh": "选择文件…"},
    "Nenhum arquivo escolhido": {"en": "No file chosen", "zh": "未选择文件"},
    "Mostrar a imagem inteira (com faixas)": {
        "en": "Show the whole image (with bars)", "zh": "显示完整图片（带边框）"},
    "Sem isso, a imagem é cortada para preencher a tela 128×128.": {
        "en": "Otherwise the image is cropped to fill the 128×128 screen.", "zh": "否则图片会被裁剪以填满 128×128 屏幕。"},
    "Enviar para a tela": {"en": "Send to screen", "zh": "发送到屏幕"},
    "Imagens": {"en": "Images", "zh": "图片"},
    "Enviado: {n} quadro(s)": {"en": "Sent: {n} frame(s)", "zh": "已发送：{n} 帧"},
    "Até 140 quadros. Leva uns 20 segundos.": {
        "en": "Up to 140 frames. Takes about 20 seconds.", "zh": "最多 140 帧，大约需要 20 秒。"},
    # ajustes
    "Tempo até dormir": {"en": "Sleep time", "zh": "休眠时间"},
    "Nunca": {"en": "Never", "zh": "从不"},
    "1 minuto": {"en": "1 minute", "zh": "1 分钟"},
    "5 minutos": {"en": "5 minutes", "zh": "5 分钟"},
    "30 minutos": {"en": "30 minutes", "zh": "30 分钟"},
    "Tempo de resposta das teclas": {"en": "Key response time", "zh": "按键响应时间"},
    "Nível 1 é o mais rápido (~2-3 ms no cabo). Suba se alguma tecla repetir sozinha.": {
        "en": "Level 1 is the fastest (~2-3 ms wired). Raise it if a key chatters.",
        "zh": "1 级最快（有线约 2-3 毫秒）。如果按键连击，请调高。"},
    "Relógio da tela": {"en": "Screen clock", "zh": "屏幕时钟"},
    "Acertar com a hora do computador": {"en": "Sync with the computer clock", "zh": "与电脑时间同步"},
    "Acertar agora": {"en": "Sync now", "zh": "立即同步"},
    "Relógio acertado": {"en": "Clock synced", "zh": "时钟已同步"},
    "Padrão de fábrica do teclado": {"en": "Keyboard factory reset", "zh": "键盘恢复出厂设置"},
    "Apaga luz, cores, teclas remapeadas e ajustes.": {
        "en": "Erases lighting, colors, remapped keys and settings.", "zh": "清除灯光、颜色、按键映射和设置。"},
    "Restaurar": {"en": "Reset", "zh": "恢复"},
    "Restaurar o padrão de fábrica?": {"en": "Reset to factory defaults?", "zh": "恢复出厂设置？"},
    "Cancelar": {"en": "Cancel", "zh": "取消"},
    "Teclado restaurado": {"en": "Keyboard reset", "zh": "键盘已恢复"},
    # atalhos
    "Atalhos de fábrica do teclado. Funcionam sem nenhum programa.": {
        "en": "The keyboard's built-in shortcuts. They work without any software.",
        "zh": "键盘内置快捷键，无需任何软件即可使用。"},
    "Fonte: manual do AK820 Pro. Confira no seu teclado; alguns lotes mudam a fileira F.": {
        "en": "Source: AK820 Pro manual. Check on your keyboard; some batches change the F row.",
        "zh": "来源：AK820 Pro 说明书。请在您的键盘上确认，部分批次的 F 行可能不同。"},
    "Fileira F": {"en": "F row", "zh": "F 行"},
    "Windows: {w} · Mac: {m}": {"en": "Windows: {w} · Mac: {m}", "zh": "Windows：{w} · Mac：{m}"},
    "Luzes indicadoras": {"en": "Indicator lights", "zh": "指示灯"},
    "Conexão": {"en": "Connection", "zh": "连接"},
    "Tela e botão giratório": {"en": "Screen and knob", "zh": "屏幕和旋钮"},
    "Sistema": {"en": "System", "zh": "系统"},
    "Troca entre os 20 efeitos de luz": {"en": "Cycle through the 20 lighting effects", "zh": "切换 20 种灯效"},
    "Aumenta / diminui o brilho": {"en": "Brightness up / down", "zh": "亮度增加 / 降低"},
    "Acelera / desacelera o efeito": {"en": "Effect faster / slower", "zh": "灯效加速 / 减速"},
    "Muda a direção do efeito": {"en": "Change effect direction", "zh": "改变灯效方向"},
    "Troca a cor da luz": {"en": "Change light color", "zh": "切换灯光颜色"},
    "Liga / desliga a luz": {"en": "Backlight on / off", "zh": "背光开 / 关"},
    "Escolhe um dos três grupos de luz do usuário": {
        "en": "Pick one of the three user lighting groups", "zh": "选择三个自定义灯光组之一"},
    "Grava a luz atual no grupo escolhido (segure para apagar a gravação)": {
        "en": "Save current lighting to the chosen group (hold to clear it)", "zh": "将当前灯光保存到所选组（长按清除）"},
    "Bluetooth 1, 2 ou 3 (toque troca; segure 3 s para parear)": {
        "en": "Bluetooth 1, 2 or 3 (tap to switch; hold 3 s to pair)", "zh": "蓝牙 1、2 或 3（短按切换；长按 3 秒配对）"},
    "2.4 GHz (segure 3 s para parear com o dongle)": {
        "en": "2.4 GHz (hold 3 s to pair with the dongle)", "zh": "2.4 GHz（长按 3 秒与接收器配对）"},
    "Cabo USB": {"en": "USB cable", "zh": "USB 数据线"},
    "Modo com fio: automático ao ligar o cabo": {"en": "Wired mode: automatic when the cable is plugged in", "zh": "有线模式：插入数据线后自动切换"},
    "Girar o botão": {"en": "Turn the knob", "zh": "旋转旋钮"},
    "Volume - / volume +": {"en": "Volume down / up", "zh": "音量 - / +"},
    "Apertar o botão": {"en": "Press the knob", "zh": "按下旋钮"},
    "Mudo / tira o mudo": {"en": "Mute / unmute", "zh": "静音 / 取消静音"},
    "Fn + apertar o botão": {"en": "Fn + press the knob", "zh": "Fn + 按下旋钮"},
    "Menu de ajustes da tela (gira para navegar, aperta para confirmar); é por ele que se troca entre Windows e Mac, em System": {
        "en": "Screen settings menu (turn to navigate, press to confirm); switch between Windows and Mac under System",
        "zh": "屏幕设置菜单（旋转浏览，按下确认）；在 System 中切换 Windows 和 Mac"},
    "Animação da tela / volta à tela principal": {"en": "Screen animation / back to main screen", "zh": "屏幕动画 / 返回主界面"},
    "Liga / desliga a tela": {"en": "Screen on / off", "zh": "屏幕开 / 关"},
    "Trava a tecla Windows (luz W acesa)": {"en": "Lock the Windows key (W light on)", "zh": "锁定 Windows 键（W 灯亮）"},
    "Volta ao padrão de fábrica": {"en": "Factory reset", "zh": "恢复出厂设置"},
    "Fn + Espaço (segure 3 a 5 s)": {"en": "Fn + Space (hold 3-5 s)", "zh": "Fn + 空格（长按 3-5 秒）"},
    "Player de mídia": {"en": "Media player", "zh": "媒体播放器"},
    "Diminui o brilho da tela": {"en": "Display brightness down", "zh": "显示器亮度降低"},
    "Aumenta o brilho da tela": {"en": "Display brightness up", "zh": "显示器亮度增加"},
    "Volume -": {"en": "Volume down", "zh": "音量 -"},
    "Volume +": {"en": "Volume up", "zh": "音量 +"},
    "Mudo": {"en": "Mute", "zh": "静音"},
    "Parar": {"en": "Stop", "zh": "停止"},
    "Diminui a luz do teclado": {"en": "Keyboard backlight down", "zh": "键盘背光降低"},
    "Aumenta a luz do teclado (o manual repete \"diminui\", provável erro)": {
        "en": "Keyboard backlight up (the manual says \"down\" twice, likely a typo)",
        "zh": "键盘背光增加（说明书重复写了“降低”，可能有误）"},
    "Faixa anterior": {"en": "Previous track", "zh": "上一曲"},
    "Tocar / pausar": {"en": "Play / pause", "zh": "播放 / 暂停"},
    "Próxima faixa": {"en": "Next track", "zh": "下一曲"},
    "E-mail": {"en": "E-mail", "zh": "邮件"},
    "Navegador": {"en": "Browser", "zh": "浏览器"},
    "Meu computador": {"en": "My computer", "zh": "我的电脑"},
    "Calculadora": {"en": "Calculator", "zh": "计算器"},
    "Mission Control": {"en": "Mission Control", "zh": "调度中心"},
    "Launchpad": {"en": "Launchpad", "zh": "启动台"},
    "Print Screen": {"en": "Print Screen", "zh": "截屏"},
    "Break": {"en": "Break", "zh": "Break"},
    "Caps Lock ligado": {"en": "Caps Lock on", "zh": "大写锁定开启"},
    "Tecla Windows travada": {"en": "Windows key locked", "zh": "Windows 键已锁定"},
    "Carga": {"en": "Charge", "zh": "充电"},
    "Vermelho piscando: bateria fraca; vermelho fixo: carregando; verde: carregada": {
        "en": "Blinking red: low battery; solid red: charging; green: charged",
        "zh": "红灯闪烁：电量低；红灯常亮：充电中；绿灯：已充满"},
    # linha de comando e mensagens do dispositivo
    '  (direção: {d})': {"en": '  (direction: {d})', "zh": '  （方向：{d}）'},
    '(combine com +, ex.: ctrl_esq+shift_esq+esc)': {"en": '(combine with +, e.g. ctrl_esq+shift_esq+esc)', "zh": '（用 + 组合，例如 ctrl_esq+shift_esq+esc）'},
    'AK820 Pro encontrado em {c} (interface 3)': {"en": 'AK820 Pro found at {c} (interface 3)', "zh": '已在 {c} 找到 AK820 Pro（接口 3）'},
    'Configura o teclado Ajazz AK820 Pro no Linux (pelo cabo USB).': {"en": 'Configures the Ajazz AK820 Pro keyboard on Linux (over the USB cable).', "zh": '在 Linux 上配置 Ajazz AK820 Pro 键盘（通过 USB 数据线）。'},
    'HH:MM, para testar; sem isso usa a hora atual': {"en": 'HH:MM, for testing; without it the current time is used', "zh": 'HH:MM，用于测试；不填则使用当前时间'},
    'acerta o relógio da tela (padrão: hora do sistema)': {"en": 'sets the screen clock (default: system time)', "zh": '设置屏幕时钟（默认：系统时间）'},
    'ajustes: sono {s}, resposta nível {r}': {"en": 'settings: sleep {s}, response level {r}', "zh": '设置：休眠 {s}，响应等级 {r}'},
    'apaga as cores guardadas antes de aplicar': {"en": 'clears the saved colors before applying', "zh": '应用前清除已保存的颜色'},
    'cor em hexadecimal (padrão ff0000)': {"en": 'hex color (default ff0000)', "zh": '十六进制颜色（默认 ff0000）'},
    'cor inválida: {texto}': {"en": 'invalid color: {texto}', "zh": '无效颜色：{texto}'},
    'enviando {i}/{n} blocos': {"en": 'sending {i}/{n} blocks', "zh": '正在发送 {i}/{n} 块'},
    'erro: {e}': {"en": 'error: {e}', "zh": '错误：{e}'},
    'lista as ações possíveis no remapeamento': {"en": 'lists the possible remap actions', "zh": '列出可用的映射功能'},
    'lista as teclas e o remapeamento atual': {"en": 'lists the keys and the current remapping', "zh": '列出按键及当前映射'},
    'lista os atalhos de fábrica do teclado (Fn + tecla)': {"en": "lists the keyboard's built-in shortcuts (Fn + key)", "zh": '列出键盘内置快捷键（Fn + 按键）'},
    'lista os efeitos de iluminação': {"en": 'lists the lighting effects', "zh": '列出灯光效果'},
    'luz personalizada: uma cor por tecla (ex.: esc=ff0000 f1=00ff00)': {"en": 'custom lighting: one color per key (e.g. esc=ff0000 f1=00ff00)', "zh": '自定义灯光：每个按键一种颜色（例如 esc=ff0000 f1=00ff00）'},
    'manda uma imagem ou GIF para a tela (128x128, até 140 quadros)': {"en": 'sends an image or GIF to the screen (128x128, up to 140 frames)', "zh": '将图片或 GIF 发送到屏幕（128x128，最多 140 帧）'},
    'minutos sem uso até dormir (nunca, 1, 5 ou 30)': {"en": 'idle minutes before sleeping (nunca=never, 1, 5 or 30)', "zh": '闲置多少分钟后休眠（nunca=从不、1、5 或 30）'},
    'modificadores:': {"en": 'modifiers:', "zh": '修饰键：'},
    'mostra a imagem inteira com faixas pretas, em vez de cortar': {"en": 'shows the whole image with black bars instead of cropping', "zh": '显示完整图片并加黑边，而不是裁剪'},
    'mostra onde o teclado foi encontrado e o estado guardado': {"en": 'shows where the keyboard was found and the saved state', "zh": '显示键盘位置和已保存的状态'},
    'muda o efeito de iluminação': {"en": 'changes the lighting effect', "zh": '更改灯光效果'},
    'multimídia:': {"en": 'multimedia:', "zh": '多媒体：'},
    'nível 1 (mais rápido) a 5': {"en": 'level 1 (fastest) to 5', "zh": '1 级（最快）到 5 级'},
    'ok, iluminação: {e}': {"en": 'ok, lighting: {e}', "zh": '完成，灯光：{e}'},
    'ok, luz personalizada com {n} tecla(s) colorida(s)': {"en": 'ok, custom lighting with {n} colored key(s)', "zh": '完成，自定义灯光，已着色 {n} 个按键'},
    'padrao: devolve a função de fábrica': {"en": 'padrao: restores the factory function', "zh": 'padrao：恢复出厂功能'},
    'pinta todas as teclas desta cor antes dos pares': {"en": 'paints every key this color before the pairs', "zh": '先将所有按键涂成此颜色'},
    'remapeia uma tecla (ex.: k820 tecla capslock ctrl_esq)': {"en": 'remaps a key (e.g. k820 key capslock ctrl_esq)', "zh": '重新映射按键（例如 k820 key capslock ctrl_esq）'},
    'só para rolagem, onda, fluxo e inclinado': {"en": 'only for rolagem, onda, fluxo and inclinado', "zh": '仅适用于 rolagem、onda、fluxo 和 inclinado'},
    "tecla, atalho (ctrl_esq+c), multimídia (volume+) ou 'padrao'": {"en": "key, shortcut (ctrl_esq+c), multimedia (volume+) or 'padrao'", "zh": "按键、组合键（ctrl_esq+c）、多媒体（volume+）或 'padrao'"},
    'teclas remapeadas: {m}': {"en": 'remapped keys: {m}', "zh": '已映射的按键：{m}'},
    'teclas:': {"en": 'keys:', "zh": '按键：'},
    'tempo até dormir e tempo de resposta das teclas': {"en": 'sleep time and key response time', "zh": '休眠时间和按键响应时间'},
    'usa as cores do arco-íris em vez de uma cor só': {"en": 'uses rainbow colors instead of a single color', "zh": '使用彩虹色而不是单色'},
    'use 6 dígitos hexadecimais, como ff0000': {"en": 'use 6 hex digits, like ff0000', "zh": '请使用 6 位十六进制数，例如 ff0000'},
    'use HH:MM, como 12:34': {"en": 'use HH:MM, like 12:34', "zh": '请使用 HH:MM，例如 12:34'},
    'volta o teclado ao padrão de fábrica': {"en": 'resets the keyboard to factory defaults', "zh": '将键盘恢复出厂设置'},
    'o teclado não confirmou o bloco {n} da imagem': {"en": 'the keyboard did not acknowledge image block {n}', "zh": '键盘未确认图片第 {n} 块'},
    'sem permissão em {c}. Instale a regra udev: sudo bash scripts/instalar-udev.sh': {"en": 'no permission on {c}. Install the udev rule: sudo bash scripts/instalar-udev.sh', "zh": '没有 {c} 的权限。请安装 udev 规则：sudo bash scripts/instalar-udev.sh'},
    "Prévia": {"en": "Preview", "zh": "预览"},
    "Simulação aproximada; o teclado só muda ao aplicar.": {
        "en": "Approximate simulation; the keyboard only changes when you apply.", "zh": "近似模拟；只有点击应用后键盘才会改变。"},
    # versões do teclado e temas
    "Versão do teclado": {"en": "Keyboard version", "zh": "键盘版本"},
    "Só muda o desenho do teclado no programa.": {
        "en": "Only changes how the keyboard is drawn in the app.", "zh": "仅改变程序中键盘的显示样式。"},
    "Neutro": {"en": "Neutral", "zh": "中性"},
    "Cinza e amarelo": {"en": "Grey and yellow", "zh": "灰黄"},
    "Branco e roxo": {"en": "White and purple", "zh": "白紫"},
    "Preto": {"en": "Black", "zh": "黑色"},
    "Branco": {"en": "White", "zh": "白色"},
    "Tema claro": {"en": "Light theme", "zh": "浅色主题"},
    "Tema escuro": {"en": "Dark theme", "zh": "深色主题"},
    "Cores": {"en": "Colors", "zh": "颜色"},
    "Não consegui salvar a preferência: {erro}": {
        "en": "Could not save the preference: {erro}", "zh": "无法保存偏好设置：{erro}"},
    # redesenho (barra lateral e páginas)
    'Ficam gravados no teclado e valem também sem fio.': {"en": 'Saved on the keyboard; they also apply when wireless.', "zh": '保存在键盘中，无线模式下同样有效。'},
    'Outra cor': {"en": 'Other color', "zh": '其他颜色'},
    '{s} selecionada(s) · {c} colorida(s)': {"en": '{s} selected · {c} colored', "zh": '已选 {s} 个 · 已着色 {c} 个'},
    'Conectado pelo cabo': {"en": 'Connected by cable', "zh": '已通过数据线连接'},
    'Desconectado: ligue o cabo USB': {"en": 'Disconnected: plug in the USB cable', "zh": '未连接：请插入 USB 数据线'},
    'Firmware {v}': {"en": 'Firmware {v}', "zh": '固件 {v}'},
    'Restaurar padrão': {"en": 'Restore defaults', "zh": '恢复默认'},
    'Seções': {"en": 'Sections', "zh": '分区'},
    'Os 20 efeitos do teclado. A prévia acompanha o que você escolhe e o teclado muda junto.': {"en": "The keyboard's 20 effects. The preview follows your choices and the keyboard changes along.", "zh": '键盘的 20 种灯效。预览会跟随您的选择，键盘也会同步改变。'},
    'Prévia: {efeito}, {cor}': {"en": 'Preview: {efeito}, {cor}', "zh": '预览：{efeito}，{cor}'},
    'arco-íris': {"en": 'rainbow', "zh": '彩虹'},
    'Enquadramento': {"en": 'Framing', "zh": '取景'},
    'Imagem inteira': {"en": 'Whole image', "zh": '完整图片'},
    'Preencher': {"en": 'Fill', "zh": '填满'},
    '{arquivo} · {n} quadro(s)': {"en": '{arquivo} · {n} frame(s)', "zh": '{arquivo} · {n} 帧'},
    'Vermelho': {"en": 'Red', "zh": '红色'},
    'Laranja': {"en": 'Orange', "zh": '橙色'},
    'Amarelo': {"en": 'Yellow', "zh": '黄色'},
    'Verde': {"en": 'Green', "zh": '绿色'},
    'Ciano': {"en": 'Cyan', "zh": '青色'},
    'Azul': {"en": 'Blue', "zh": '蓝色'},
    'Roxo': {"en": 'Purple', "zh": '紫色'},
    # dongle 2.4 GHz
    'O teclado não respondeu pelo dongle. Ele está ligado no 2.4 GHz e acordado? Aperte uma tecla e tente de novo.': {"en": 'The keyboard did not answer through the dongle. Is it on 2.4 GHz and awake? Press a key and try again.', "zh": '键盘没有通过接收器响应。它是否处于 2.4 GHz 模式并已唤醒？按任意键后重试。'},
    'A tela só pode ser trocada pelo cabo USB.': {"en": 'The screen can only be changed over the USB cable.', "zh": '屏幕只能通过 USB 数据线更改。'},
    'A restauração de fábrica só funciona pelo cabo USB (ou segure Fn + Espaço por 3 a 5 s).': {"en": 'Factory reset only works over the USB cable (or hold Fn + Space for 3 to 5 s).', "zh": '恢复出厂设置只能通过 USB 数据线进行（或长按 Fn + 空格 3 到 5 秒）。'},
    "Conectado pelo dongle 2.4 GHz": {"en": "Connected through the 2.4 GHz dongle", "zh": "已通过 2.4 GHz 接收器连接"},
    "Desconectado: ligue o cabo USB ou o dongle": {"en": "Disconnected: plug in the USB cable or the dongle", "zh": "未连接：请插入 USB 数据线或接收器"},
    "Teclado não encontrado. Ligue o AK820 Pro pelo cabo USB ou pelo dongle 2.4 GHz.": {
        "en": "Keyboard not found. Connect the AK820 Pro with the USB cable or the 2.4 GHz dongle.",
        "zh": "未找到键盘。请用 USB 数据线或 2.4 GHz 接收器连接 AK820 Pro。"},
}
