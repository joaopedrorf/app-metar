from exemplos import METAR_SBGL, TAF_SBGL
from formatacao import data_notam, formatar_metar, formatar_nuvens, formatar_taf, hora_utc
from textos import TEXTOS

PT = TEXTOS['pt']
EN = TEXTOS['en']


def test_metar_em_portugues():
    info = formatar_metar(METAR_SBGL, 'pt', PT)
    assert info['bruto'].startswith("METAR SBGL")
    assert info['visibilidade'] == "10 km ou mais"  # 9999 ou mais = 10 km ou mais
    assert info['teto'] == "1500 ft"
    assert info['vento'] == "160° com 12 kt, rajadas de 22 kt"
    assert info['qnh'] == "1014 hPa"
    assert info['tempo_presente'] == "Chuva leve"  # termo do DECEA para "-"


def test_metar_sem_teto_e_sem_fenomenos():
    dados = {"raw_text": "METAR SBGL 191800Z 00000KT 9999 FEW030 25/15 Q1015", "wind": {"degrees": 0, "speed_kts": 0}}
    info = formatar_metar(dados, 'en', EN)
    assert info['teto'] == "Clear Sky (No Ceiling)"
    assert info['tempo_presente'] == "No significant phenomena"
    assert info['qnh'] == "---"


def test_metar_cavok():
    dados = {"raw_text": "METAR SBGL 191800Z 00000KT CAVOK 25/15 Q1015", "wind": {"speed_kts": 0}}
    info = formatar_metar(dados, 'pt', PT)
    assert info['visibilidade'] == "10 km ou mais (CAVOK)"
    assert info['tempo_presente'] == "Nenhum tempo significativo (CAVOK)"
    assert "5000 ft" in info['teto']


def test_taf_lista_os_periodos():
    taf = formatar_taf(TAF_SBGL, 'pt', PT)
    assert [p['mudanca'] for p in taf['periodos']] == ["Previsão base 1918/2024", "TEMPO 1921/2001", "BECMG 2006/2008"]

    tempo = taf['periodos'][1]
    assert tempo['inicio'] == "19/10 21:00Z"
    assert tempo['visibilidade'] == "4000 m"
    assert tempo['nuvens'] == "BKN 1000 ft"
    assert tempo['tempo'] == "Chuva moderada"  # RA sem sinal = moderada
    assert tempo['vento'] == "—"  # TEMPO sem mudança de vento

    assert taf['periodos'][2]['vento'] == "Variável, 3 kt"


def test_taf_com_probabilidade():
    dados = {"raw_text": "TAF ...", "forecast": [
        {"change": {"indicator": {"code": "TEMPO"}, "probability": 30}},
    ]}
    assert formatar_taf(dados, 'pt', PT)['periodos'][0]['mudanca'] == "PROB30 TEMPO"


def test_nuvens_com_cb():
    assert formatar_nuvens([{"code": "FEW", "feet": 3000, "type": "CB"}], PT) == "FEW 3000 ft CB"
    assert formatar_nuvens([], PT) == "—"


def test_hora_utc_aceita_z_e_texto_invalido():
    assert hora_utc("2026-10-19T12:00:00Z") == "19/10 12:00Z"
    assert hora_utc("amanhã") == "amanhã"


def test_datas_de_notam():
    assert data_notam("2610150900", PT) == "15/10/2026 09:00Z"
    assert data_notam("2611152359 EST", PT) == "15/11/2026 23:59Z (estimado)"
    assert data_notam("PERM", EN) == "Permanent"
    assert data_notam("", PT) == "—"
