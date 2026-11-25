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


def test_previa_para_linkedin(cliente):
    html = cliente.get('/').get_data(as_text=True)
    assert 'property="og:title"' in html
    assert 'content="https://localhost/static/imagens/previa.png"' in html
    assert cliente.get('/static/imagens/previa.png').status_code == 200


# ---------- Selo de frescor ----------

@pytest.fixture
def relogio(monkeypatch):
    """Fixa a hora do servidor em 19/10/2026 18:25Z (METAR de exemplo é 191800Z)."""
    from datetime import datetime, timezone
    import frescor

    def acertar(dia, hora, minuto):
        momento = datetime(2026, 10, dia, hora, minuto, tzinfo=timezone.utc)
        monkeypatch.setattr(frescor, 'agora_utc', lambda: momento)

    acertar(19, 18, 25)
    return acertar


def test_selo_de_frescor_em_cada_secao(cliente, fontes_ok, relogio):
    html = cliente.post('/', data={"icao": "SBGL", "idioma": "pt"}).get_data(as_text=True)
    assert "Observado às 18:00Z (há 25 min)" in html
    assert "Emitido às 16:30Z (há 1 h 55 min)" in html
    assert "Consultado às 18:25Z" in html
    assert "selo-velho" not in html


def test_selo_avisa_metar_velho_e_taf_vencido(cliente, fontes_ok, relogio):
    relogio(21, 1, 0)
    html = cliente.post('/', data={"icao": "SBGL", "idioma": "en"}).get_data(as_text=True)
    assert "Over 1 h old" in html
    assert "Validity ended at 00:00Z." in html
    assert "selo-velho" in html


def test_selo_mostra_hora_da_falha(cliente, fontes_ok, relogio, monkeypatch):
    def notam_fora(icao):
        raise ErroFonte('conexao')

    monkeypatch.setattr(clientes, 'buscar_notams', notam_fora)
    html = cliente.post('/', data={"icao": "SBGL", "idioma": "pt"}).get_data(as_text=True)
    assert "Falhou às 18:25Z" in html
    # As outras seções continuam com o selo normal
    assert "Observado às 18:00Z" in html


def test_rodape_com_link_do_linkedin(cliente):
    html = cliente.get('/').get_data(as_text=True)
    assert "linkedin.com/in/" in html
    assert "Fale com o desenvolvedor" in html
    html = cliente.post('/', data={"icao": "", "idioma": "en"}).get_data(as_text=True)
    assert "Contact the developer" in html


def test_aerodromo_estrangeiro_nao_mostra_falha_no_notam(cliente, fontes_ok, relogio, monkeypatch):
    def fora(icao):
        raise ErroFonte('fora_do_brasil')

    monkeypatch.setattr(clientes, 'buscar_notams', fora)
    html = cliente.post('/', data={"icao": "KMIA", "idioma": "en"}).get_data(as_text=True)
    assert "only available for Brazilian aerodromes" in html
    assert "Failed at" not in html
