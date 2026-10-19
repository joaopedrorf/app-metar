import pytest

import clientes
from clientes import ErroFonte
from exemplos import METAR_SBGL, NOTAM_XML, TAF_SBGL
from metar import app


@pytest.fixture
def cliente():
    app.config['TESTING'] = True
    return app.test_client()


@pytest.fixture
def fontes_ok(monkeypatch):
    monkeypatch.setattr(clientes, 'buscar_metar', lambda icao: METAR_SBGL)
    monkeypatch.setattr(clientes, 'buscar_taf', lambda icao: TAF_SBGL)
    monkeypatch.setattr(clientes, 'buscar_notams', lambda icao: clientes.ler_xml_notams(NOTAM_XML))


def test_pagina_inicial(cliente):
    html = cliente.get('/').get_data(as_text=True)
    assert "Briefing Meteorológico" in html


def test_icao_invalido(cliente):
    html = cliente.post('/', data={"icao": "SB1", "idioma": "pt"}).get_data(as_text=True)
    assert "ICAO válido com 4 letras" in html


def test_trocar_idioma_sem_icao_nao_mostra_erro(cliente):
    html = cliente.post('/', data={"icao": "", "idioma": "en"}).get_data(as_text=True)
    assert "Weather Briefing" in html
    assert "Attention" not in html


def test_briefing_completo(cliente, fontes_ok):
    html = cliente.post('/', data={"icao": "sbgl", "idioma": "pt"}).get_data(as_text=True)
    assert "METAR SBGL 191800Z" in html
    assert "TAF SBGL 191630Z" in html
    assert "C1234/26" in html
    assert "RWY 10/28 CLSD" in html
    assert "Permanente" in html
    # O ICAO continua no campo, para trocar de idioma sem digitar de novo
    assert 'value="SBGL"' in html


def test_falha_no_notam_nao_derruba_o_resto(cliente, fontes_ok, monkeypatch):
    def notam_fora(icao):
        raise ErroFonte('conexao')

    monkeypatch.setattr(clientes, 'buscar_notams', notam_fora)
    html = cliente.post('/', data={"icao": "SBGL", "idioma": "pt"}).get_data(as_text=True)
    assert "METAR SBGL 191800Z" in html
    assert "TAF SBGL 191630Z" in html
    assert "Falha na conexão com o servidor." in html


def test_aerodromo_sem_taf(cliente, fontes_ok, monkeypatch):
    def sem_taf(icao):
        raise ErroFonte('nao_encontrado')

    monkeypatch.setattr(clientes, 'buscar_taf', sem_taf)
    html = cliente.post('/', data={"icao": "SBGL", "idioma": "en"}).get_data(as_text=True)
    assert "METAR SBGL 191800Z" in html
    assert "No data found for this aerodrome." in html
