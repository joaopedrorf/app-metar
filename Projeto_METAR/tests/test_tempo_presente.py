import pytest

from formatacao import formatar_metar, formatar_vento, formatar_visibilidade
from tempo_presente import FENOMENOS, decodificar
from textos import TEXTOS

PT = TEXTOS['pt']
EN = TEXTOS['en']


@pytest.mark.parametrize("codigo, pt, en", [
    # O caso que apareceu em inglês no site
    ("VCSH", "Pancadas na vizinhança", "Showers in the vicinity"),
    # Intensidade (sem sinal = moderada)
    ("-RA", "Chuva fraca", "Light rain"),
    ("RA", "Chuva moderada", "Moderate rain"),
    ("+RA", "Chuva forte", "Heavy rain"),
    ("-DZ", "Chuvisco fraco", "Light drizzle"),
    ("-RADZ", "Chuva fraca e chuvisco", "Light rain and drizzle"),
    # Pancadas e trovoadas
    ("SHRA", "Pancadas de chuva moderada", "Moderate rain showers"),
    ("-SHRA", "Pancadas de chuva fraca", "Light rain showers"),
    ("+TSRA", "Trovoada com chuva forte", "Thunderstorm with heavy rain"),
    ("TS", "Trovoada", "Thunderstorm"),
    ("VCTS", "Trovoada na vizinhança", "Thunderstorm in the vicinity"),
    ("TSGR", "Trovoada com granizo moderado", "Thunderstorm with moderate hail"),
    # Obscurecimento e descritores
    ("BR", "Névoa úmida", "Mist"),
    ("HZ", "Névoa seca", "Haze"),
    ("FG", "Nevoeiro", "Fog"),
    ("FU", "Fumaça", "Smoke"),
    ("MIFG", "Nevoeiro baixo", "Shallow fog"),
    ("BCFG", "Nevoeiro em bancos", "Patches of fog"),
    ("PRFG", "Nevoeiro parcial", "Partial fog"),
    ("FZFG", "Nevoeiro congelante", "Freezing fog"),
    ("VCFG", "Nevoeiro na vizinhança", "Fog in the vicinity"),
    ("-FZDZ", "Chuvisco congelante fraco", "Light freezing drizzle"),
    ("BLSN", "Neve soprada", "Blowing snow"),
    ("DRSA", "Areia flutuante", "Low drifting sand"),
    # Outros
    ("SQ", "Tempestade (rajada)", "Squall"),
    ("+FC", "Nuvem funil (tornado ou tromba d'água)", "Funnel cloud (tornado or waterspout)"),
    ("NSW", "Sem tempo significativo", "No significant weather"),
])
def test_codigos(codigo, pt, en):
    assert decodificar(codigo, 'pt') == pt
    assert decodificar(codigo, 'en') == en


def test_nenhum_fenomeno_fica_sem_traducao():
    # Todo fenômeno da tabela, sozinho ou na vizinhança, tem frase nos dois idiomas
    for codigo in FENOMENOS:
        for prefixo in ('', '-', '+', 'VC'):
            assert decodificar(prefixo + codigo, 'pt')
            assert decodificar(prefixo + codigo, 'en')


@pytest.mark.parametrize("codigo", ["", "XX", "RAX", "VC"])
def test_codigo_invalido_devolve_none(codigo):
    assert decodificar(codigo, 'pt') is None


def test_metar_com_vcsh_fica_em_portugues():
    dados = {
        "raw_text": "METAR SBXX 201200Z 00000KT 9999 VCSH BKN045 25/18 Q1020",
        "visibility": {"meters": "9999.0"},
        "ceiling": {"feet": 4500},
        "wind": {"speed_kts": 0},
        "barometer": {"hpa": 1020.0},
        "conditions": [{"code": "VCSH", "text": "Nearby showers"}],
    }
    info = formatar_metar(dados, 'pt', PT)
    assert info['tempo_presente'] == "Pancadas na vizinhança"
    assert info['visibilidade'] == "10 km ou mais"
    assert info['vento'] == "Calmo"
    assert info['qnh'] == "1020 hPa"


def test_sem_codigo_usa_texto_da_api():
    dados = {"raw_text": "METAR ...", "conditions": [{"text": "Mist"}]}
    assert formatar_metar(dados, 'pt', PT)['tempo_presente'] == "Névoa úmida"


def test_visibilidade_e_vento():
    assert formatar_visibilidade({"meters": "4000.0"}, PT) == "4000 m"
    assert formatar_visibilidade({"meters": 9999}, EN) == "10 km or more"
    assert formatar_vento({"degrees": 90, "speed_kts": 0}, EN) == "Calm"
