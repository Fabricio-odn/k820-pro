from k820_pro.preferencias import Preferencias


def test_ida_e_volta(tmp_path):
    p = Preferencias("claro", "neutro", "zh")
    p.salvar(tmp_path / "p.json")
    assert Preferencias.carregar(tmp_path / "p.json") == p


def test_padroes_sem_arquivo(tmp_path):
    assert Preferencias.carregar(tmp_path / "x.json") == Preferencias()
    assert Preferencias() == Preferencias("escuro", "neutro", None)


def test_valores_estranhos_viram_padrao(tmp_path):
    arq = tmp_path / "p.json"
    for conteudo in ('{"tema": "roxo", "versao": 3, "idioma": "xx"}', "lixo", "[]", '{"tema": null}'):
        arq.write_text(conteudo)
        assert Preferencias.carregar(arq) == Preferencias()
    arq.write_text('{"tema": "claro", "versao": "inexistente"}')
    assert Preferencias.carregar(arq) == Preferencias(tema="claro")


def test_migra_arquivo_idioma_antigo(tmp_path):
    (tmp_path / "idioma").write_text("en\n")
    assert Preferencias.carregar(tmp_path / "preferencias.json").idioma == "en"


def test_idioma_malformado_nao_trava(tmp_path):
    arq = tmp_path / "preferencias.json"
    for conteudo in ('{"idioma": ["en"]}', '{"idioma": {}}', '{"tema": ["claro"]}'):
        arq.write_text(conteudo)
        assert Preferencias.carregar(arq) == Preferencias()
    arq.unlink()
    (tmp_path / "idioma").write_bytes(b"\xff\xfe\x00")
    assert Preferencias.carregar(arq) == Preferencias()
