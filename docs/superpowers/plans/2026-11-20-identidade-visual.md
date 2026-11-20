# Identidade visual (K820 Pro Studio) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dar ao app o nome K820 Pro Studio, o tema preto e branco do `dazz-mouse` (escuro e claro, com botão para trocar), a escolha da versão do teclado e um ícone próprio.

**Architecture:** Preferências da interface (tema, versão, idioma) num JSON próprio. As versões do teclado são dados puros (`gui/versoes.py`) que o widget `Teclado` usa para pintar teclas sem cor. O tema é uma folha CSS por modo, trocada em tempo real por `gui/tema.py`.

**Tech Stack:** Python 3.10+, GTK 4 / libadwaita 1.5+ (PyGObject), pytest.

**Spec:** `docs/superpowers/specs/2026-11-20-identidade-visual-design.md`

## Global Constraints

- Nome exibido: **K820 Pro Studio**. ID do app continua `io.github.k820pro.Configurador`.
- Tema escuro: fundo #0E0E10, cabeçalho #141417, cartões #1B1B1F, borda #2B2B30, destaque #FFFFFF com texto #0E0E10.
- Tema claro: fundo #FAFAFA, cabeçalho #F0F0F2, cartões #FFFFFF, borda #DCDCE0, destaque #0E0E10 com texto #FFFFFF.
- Escuro é o padrão. Vermelho só para erro e ação destrutiva.
- Todo texto novo passa por `t()` com tradução en e zh (o `tests/test_i18n.py` cobra).
- Preferências em `~/.config/k820-pro/` (respeitando `XDG_CONFIG_HOME`).

## Review Focus

- `preferencias.json` corrompido ou com valor desconhecido: o app abre com os padrões, sem quebrar (teste na Task 1).
- Arquivo antigo `~/.config/k820-pro/idioma` (da versão já publicada): o idioma escolhido continua valendo (teste na Task 1).
- Texto da tecla legível em todas as versões: contraste entre o fundo da tecla e o texto, inclusive no branco (teste na Task 2).
- Trocar o tema com a janela aberta não deixa duas folhas CSS carregadas ao mesmo tempo (teste na Task 3).
- Tecla com cor de luz por cima continua mostrando a cor da luz, não a da versão (teste na Task 2).

---

### Task 1: Preferências da interface

**Files:**
- Create: `k820_pro/preferencias.py`
- Modify: `k820_pro/gui/app.py` (trocar `_idioma_salvo` por `Preferencias.carregar()`), `k820_pro/gui/janela.py` (`salvar_idioma` passa a usar `Preferencias`)
- Test: `tests/test_preferencias.py`

**Interfaces:**
- Produces: `@dataclass Preferencias(tema: str = "escuro", versao: str = "neutro", idioma: str | None = None)`, `Preferencias.carregar(caminho=None) -> Preferencias`, `Preferencias.salvar(caminho=None) -> None`, `TEMAS = ("escuro", "claro")`, `caminho_padrao() -> Path` (= `.../k820-pro/preferencias.json`).

- [ ] **Step 1: Testes**

```python
def test_ida_e_volta(tmp_path): p = Preferencias("claro", "cinza-amarelo", "zh"); p.salvar(tmp_path/"p.json"); assert Preferencias.carregar(tmp_path/"p.json") == p
def test_padroes_sem_arquivo(tmp_path): assert Preferencias.carregar(tmp_path/"x.json") == Preferencias()
def test_valores_estranhos_viram_padrao(tmp_path):  # '{"tema": "roxo", "versao": 3, "idioma": "xx"}' e "lixo" -> Preferencias()
def test_migra_arquivo_idioma_antigo(tmp_path):  # existe tmp_path/"idioma" com "en\n" e não existe preferencias.json -> idioma == "en"
```

- [ ] **Step 2:** `pytest tests/test_preferencias.py` falha (módulo não existe).
- [ ] **Step 3:** Implementar. Valores fora de `TEMAS`, de `versoes.VERSOES` (Task 2; até lá aceite só "neutro") ou de `i18n.IDIOMAS` voltam ao padrão campo a campo. Escrita atômica (`.tmp` + `replace`), como `estado.py`.
- [ ] **Step 4:** `pytest -q` passa (inclusive os testes antigos).
- [ ] **Step 5:** Commit `feat: preferências da interface (tema, versão, idioma)`.

### Task 2: Versões do teclado no desenho

**Files:**
- Create: `k820_pro/gui/versoes.py`
- Modify: `k820_pro/gui/teclado.py` (atributos `versao` e `tema`; fundo da tecla sem cor vem da versão), `k820_pro/gui/janela.py` (linha "Versão do teclado" na aba Ajustes, que atualiza os dois teclados e salva a preferência), `k820_pro/i18n.py`, `k820_pro/preferencias.py` (validar contra `VERSOES`)
- Test: `tests/test_versoes.py`

**Interfaces:**
- Consumes: `Preferencias` (Task 1).
- Produces: `@dataclass(frozen=True) Versao(nome: str, corpo, alfa, modificadora, destaque, texto_alfa, texto_mod, texto_destaque: tuple[int,int,int], teclas_destaque: frozenset[str])`, `VERSOES: dict[str, Versao]` com as chaves `"neutro", "cinza-amarelo", "branco-roxo", "preto", "branco"` nessa ordem, `MODIFICADORAS: frozenset[str]`, `cor_da_tecla(versao: Versao, nome: str) -> tuple[fundo, texto]`.

Valores (aproximações das fotos oficiais; o nome vai por `t()`):

| chave | nome | corpo | alfa | modificadora | destaque | textos (alfa / mod / destaque) | destaque em |
|---|---|---|---|---|---|---|---|
| neutro | Neutro | sem corpo | #28282E | #28282E | #28282E | #EBEBEB ×3 | — |
| cinza-amarelo | Cinza e amarelo | #2E2F33 | #C9CACC | #5A5C62 | #F2C230 | #26272B / #F0F0F0 / #26272B | esc, enter |
| branco-roxo | Branco e roxo | #EEEEF2 | #FFFFFF | #C9B8EC | #8E6CCF | #3B2E5A / #3B2E5A / #FFFFFF | esc, enter |
| preto | Preto | #141416 | #2A2A2E | #1E1E21 | #2A2A2E | #E6E6E6 ×3 | — |
| branco | Branco | #E9E9EC | #FFFFFF | #E0E0E4 | #FFFFFF | #2B2B2E ×3 | — |

`MODIFICADORAS`: esc, grave, tab, capslock, shift_esq, shift_dir, ctrl_esq, ctrl_dir, win, alt_esq, alt_dir, fn, enter, backspace, delete, home, pgup, pgdn, cima, baixo, esquerda, direita. Destaque tem prioridade sobre modificadora. Com versão que tem corpo, o widget desenha um retângulo arredondado na cor do corpo atrás das teclas (margem de 10 px na escala do desenho).

- [ ] **Step 1: Testes**

```python
def test_cinco_versoes_na_ordem(): assert list(VERSOES) == ["neutro", "cinza-amarelo", "branco-roxo", "preto", "branco"]
def test_tipos_de_tecla(): v = VERSOES["cinza-amarelo"]; assert cor_da_tecla(v, "esc")[0] == (0xF2,0xC2,0x30); assert cor_da_tecla(v, "a")[0] == (0xC9,0xCA,0xCC); assert cor_da_tecla(v, "tab")[0] == (0x5A,0x5C,0x62)
def test_contraste_legivel():  # para toda versão e toda tecla do layout, razão de contraste WCAG entre fundo e texto >= 3.0
def test_toda_versao_traduzida(): assert all({"en","zh"} <= set(i18n.TRADUCOES[v.nome]) for v in VERSOES.values())
def test_cor_de_luz_tem_prioridade():  # Teclado(...) só é testável com GTK: teste a função pura usada pelo widget,
                                       # fundo_da_tecla(versao, nome, cores) -> cores[nome] se existir, senão cor_da_tecla(...)[0]
```

(Adicione `fundo_da_tecla(versao, nome, cores: dict) -> tuple` em `versoes.py`.)

- [ ] **Step 2:** `pytest tests/test_versoes.py` falha.
- [ ] **Step 3:** Implementar `versoes.py`; o `_desenhar` do `Teclado` usa `fundo_da_tecla` e o texto de `cor_da_tecla` (quando a tecla tem cor de luz, mantém a regra atual de texto claro/escuro pela luminância). Linha `Adw.ComboRow` "Versão do teclado" no grupo Ajustes, inicializada pela preferência.
- [ ] **Step 4:** `pytest -q` passa; renderize a aba Teclas com `cinza-amarelo` e confira o PNG.
- [ ] **Step 5:** Commit `feat: escolha da versão do teclado no desenho`.

### Task 3: Tema preto e branco, escuro e claro

**Files:**
- Create: `k820_pro/gui/estilo.css`, `k820_pro/gui/estilo-claro.css`, `k820_pro/gui/tema.py`
- Modify: `k820_pro/gui/app.py` (aplica o tema salvo antes de abrir a janela), `k820_pro/gui/janela.py` (botão no cabeçalho), `k820_pro/gui/teclado.py` (contorno e seleção por tema), `pyproject.toml` (package-data `*.css`), `k820_pro/i18n.py`
- Test: `tests/test_tema.py`

**Interfaces:**
- Consumes: `Preferencias` (Task 1).
- Produces: `class Tema` com `aplicar(nome: str) -> None` (troca `Adw.StyleManager` para `FORCE_DARK`/`FORCE_LIGHT`, remove o `Gtk.CssProvider` anterior e adiciona o novo com prioridade `STYLE_PROVIDER_PRIORITY_USER + 1`) e `atual: str`; `CORES_DESENHO: dict[str, dict]` com `contorno`, `selecao`, `marcada` por tema (escuro: #5A5A60 / #FFFFFF / #A1A1AA; claro: #B4B4BA / #0E0E10 / #6B6B73).

CSS: as variáveis de cor da libadwaita (`--window-bg-color`, `--headerbar-bg-color`, `--card-bg-color`, `--accent-bg-color`, `--accent-fg-color`, `--accent-color`, `--border-color` etc., como em `~/Projetos/Pessoais/dazz-mouse/dazz_mouse/gui/estilo.css`) com os valores das Global Constraints. Botão do cabeçalho: `Gtk.Button` com ícone `weather-clear-night-symbolic` no claro e `weather-clear-symbolic` no escuro, dica "Tema claro" / "Tema escuro", que aplica, salva a preferência e redesenha os teclados.

- [ ] **Step 1: Testes** (sem display, pulando se `Gtk.init_check()` falhar)

```python
def test_folhas_existem_e_tem_as_cores():  # estilo.css contém "#0E0E10" e "#FFFFFF" como accent; estilo-claro.css contém "#FAFAFA" e accent "#0E0E10"
def test_trocar_tema_mantem_um_provedor():  # Tema().aplicar("claro"); aplicar("escuro"); aplicar("claro") -> só um provedor nosso registrado (guarde a referência e confira que o anterior foi removido)
def test_tema_desconhecido(): with pytest.raises(ValueError): Tema().aplicar("roxo")
```

- [ ] **Step 2:** testes falham.
- [ ] **Step 3:** Implementar; adicionar `*.css` ao package-data.
- [ ] **Step 4:** `pytest -q` passa; renderize Iluminação e Teclas nos dois temas e confira os PNGs.
- [ ] **Step 5:** Commit `feat: tema preto e branco, escuro e claro`.

### Task 4: Nome e ícone

**Files:**
- Modify: `k820_pro/gui/icones/hicolor/scalable/apps/io.github.k820pro.Configurador.svg`
- Create: `k820_pro/gui/icones/hicolor/symbolic/apps/io.github.k820pro.Configurador-symbolic.svg`
- Modify: `k820_pro/gui/janela.py` (título "K820 Pro Studio"), `scripts/instalar-atalho.sh` (Name, e instalar o simbólico), `README.md`, `pyproject.toml` (description), `docs/imagens/*.png` (renderizar de novo)
- Test: `tests/test_icone.py`

Ícone 128×128 no estilo do ícone do `dazz-mouse`: teclado 75% visto de cima (retângulo arredondado inclinado levemente), face de cima em gradiente cinza-escuro (#5E5C64 → #241F31), borda frontal 6 px abaixo com o gradiente de LED arco-íris (#E01B24, #FF7800, #F6D32D, #33D17A, #3584E4, #9141AC), grade de teclas em #9A9996 e a telinha no canto superior direito acesa (#3584E4 → #33D17A) com o botão giratório ao lado. Simbólico 16×16 só com `#241f31`: contorno do teclado, três linhas de teclas e o quadradinho da tela.

README: título "K820 Pro Studio", subtítulo "configurador do Ajazz AK820 Pro para Linux", e no fim: "Projeto independente, sem relação com a Ajazz nem com quem fez o software oficial. Os nomes e as marcas pertencem aos donos." Descrição do repositório no GitHub atualizada com `gh repo edit --description`.

- [ ] **Step 1: Testes**

```python
def test_svgs_validos():  # os dois SVGs são XML válidos (xml.etree), viewBox "0 0 128 128" e "0 0 16 16"
def test_simbolico_monocromatico():  # todos os fill/stroke do simbólico são "#241f31" ou "none"
def test_nome_na_janela():  # o literal "K820 Pro Studio" aparece em janela.py e no .desktop gerado por instalar-atalho.sh
```

- [ ] **Step 2:** testes falham.
- [ ] **Step 3:** Desenhar os SVGs; trocar os textos; reinstalar o atalho; renderizar de novo as imagens do README (sem a aba Tela com GIF de terceiros).
- [ ] **Step 4:** `pytest -q` passa; ver o ícone renderizado em 128 e 32 px.
- [ ] **Step 5:** Commit `feat: nome K820 Pro Studio e ícone`, push.
