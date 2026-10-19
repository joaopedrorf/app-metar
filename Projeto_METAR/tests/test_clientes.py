import pytest
import requests

import clientes
from clientes import ErroFonte
from exemplos import NOTAM_XML


class RespostaFalsa:
    def __init__(self, status_code, json_data=None, content=b""):
        self.status_code = status_code
        self._json = json_data
        self.content = content

    def json(self):
        if self._json is None:
            raise ValueError("sem json")
        return self._json


def test_le_xml_do_aisweb():
    notams = clientes.ler_xml_notams(NOTAM_XML)
    assert len(notams) == 2
    assert notams[0]['n'] == "C1234/26"
    assert notams[1]['c'] == "PERM"


def test_xml_quebrado_vira_erro():
    with pytest.raises(ErroFonte) as e:
        clientes.ler_xml_notams(b"<aisweb><notam>")
    assert e.value.codigo == 'indisponivel'


def test_notam_so_para_aerodromos_brasileiros(monkeypatch):
    monkeypatch.setenv('AISWEB_API_KEY', 'x')
    monkeypatch.setenv('AISWEB_API_PASS', 'y')
    with pytest.raises(ErroFonte) as e:
        clientes.buscar_notams('SAEZ')  # Buenos Aires: começa com S, mas não é Brasil
    assert e.value.codigo == 'fora_do_brasil'


def test_notam_sem_chave(monkeypatch):
    monkeypatch.delenv('AISWEB_API_KEY', raising=False)
    with pytest.raises(ErroFonte) as e:
        clientes.buscar_notams('SBGL')
    assert e.value.codigo == 'sem_chave_notam'


def test_notam_envia_chaves_e_icao(monkeypatch):
    monkeypatch.setenv('AISWEB_API_KEY', 'minha-chave')
    monkeypatch.setenv('AISWEB_API_PASS', 'minha-senha')
    chamadas = []

    def get_falso(url, params=None, timeout=None):
        chamadas.append(params)
        return RespostaFalsa(200, content=NOTAM_XML)

    monkeypatch.setattr(clientes.requests, 'get', get_falso)
    assert len(clientes.buscar_notams('SBGL')) == 2
    assert chamadas[0] == {"apiKey": "minha-chave", "apiPass": "minha-senha", "area": "notam", "icaocode": "SBGL"}


@pytest.mark.parametrize("resposta, codigo", [
    (RespostaFalsa(401), 'chave_invalida'),
    (RespostaFalsa(500), 'indisponivel'),
    (RespostaFalsa(200, {"results": 0, "data": []}), 'nao_encontrado'),
])
def test_erros_do_checkwx(monkeypatch, resposta, codigo):
    monkeypatch.setattr(clientes.requests, 'get', lambda *a, **k: resposta)
    with pytest.raises(ErroFonte) as e:
        clientes.buscar_taf('SBGL')
    assert e.value.codigo == codigo


def test_queda_de_conexao(monkeypatch):
    def get_falso(*a, **k):
        raise requests.exceptions.ConnectionError()

    monkeypatch.setattr(clientes.requests, 'get', get_falso)
    with pytest.raises(ErroFonte) as e:
        clientes.buscar_metar('SBGL')
    assert e.value.codigo == 'conexao'
