from formatacao import formatar_metar, formatar_nuvens
from grupos_metar import ler_grupos
from textos import TEXTOS

PT = TEXTOS['pt']
EN = TEXTOS['en']


def test_le_grupos_extras():
    g = ler_grupos("METAR SBGL 201200Z 31015G27KT 280V350 4000 1500SW -RA BKN010 18/16 Q1012 RETSRA WS RWY10 RMK TESTE")
    assert g['variacao_vento'] == (280, 350)
    assert g['visibilidade_minima'] == (1500, 'SW')
    assert g['tempo_recente'] == ['TSRA']
    assert g['cortante'] == ['10']
    assert g['cavok'] is False


def test_ignora_o_que_vem_depois_de_rmk_e_tendencia():
    g = ler_grupos("METAR SBGL 201200Z 18005KT 9999 FEW030 25/18 Q1015 TEMPO 3000 RERA WS ALL RWY")
    assert g['tempo_recente'] == []
    assert g['cortante'] == []


def test_metar_mostra_grupos_extras():
    dados = {
        "raw_text": "METAR SBGL 201200Z 31015G27KT 280V350 4000 1500SW -RA BKN010 18/16 Q1012 RETSRA WS ALL RWY",
        "wind": {"degrees": 310, "speed_kts": 15, "gust_kts": 27},
        "visibility": {"meters": "4000"},
        "temperature": {"celsius": 18},
        "dewpoint": {"celsius": 16},
        "barometer": {"hpa": 1012},
        "conditions": [{"code": "-RA"}],
    }
    info = formatar_metar(dados, 'pt', PT)
    assert info['vento'] == "310° com 15 kt, rajadas de 27 kt, variando entre 280° e 350°"
    assert info['visibilidade'] == "4000 m (mínima 1500 m a SW)"
    assert info['temperatura'] == "18 °C / 16 °C"
    assert info['tempo_recente'] == "Trovoada com chuva moderada"
    assert info['cortante'] == "Em todas as pistas"


def test_temperatura_negativa_e_ausente():
    dados = {"raw_text": "METAR XXXX", "temperature": {"celsius": -2}, "dewpoint": {"celsius": -5}}
    assert formatar_metar(dados, 'en', EN)['temperatura'] == "-2 °C / -5 °C"
    assert formatar_metar({"raw_text": "METAR XXXX"}, 'en', EN)['temperatura'] == "—"


def test_nuvens_especiais():
    assert formatar_nuvens([{"code": "NSC"}], PT) == "Nenhuma nuvem significativa (NSC)"
    assert formatar_nuvens([{"code": "VV", "feet": 200}], PT) == "Céu obscurecido, visibilidade vertical 200 ft (VV)"
    assert formatar_nuvens([{"code": "BKN", "feet": 1000.0}], EN) == "BKN 1000 ft"


def test_ceu_obscurecido_vira_teto():
    dados = {"raw_text": "METAR SBGL 200600Z 00000KT 0200 FG VV002 15/15 Q1016", "conditions": [{"code": "FG"}]}
    info = formatar_metar(dados, 'pt', PT)
    assert info['teto'] == "Céu obscurecido, visibilidade vertical 200 ft (VV)"
    assert info['tempo_presente'] == "Nevoeiro"


def test_nuvens_do_metar_mantem_cb():
    dados = {"raw_text": "METAR SBGL 201200Z 31015KT 9999 BKN010 FEW030CB SCT040TCU 18/16 Q1012", "ceiling": {"feet": 1000}}
    assert formatar_metar(dados, 'pt', PT)['nuvens'] == "BKN 1000 ft, FEW 3000 ft CB, SCT 4000 ft TCU"


def test_rvr_e_tendencia():
    dados = {
        "raw_text": "METAR SBGL 201200Z 18005KT 0600 R10/0800V1200U R28L/M0050 FG VV002 12/12 Q1015 "
                    "TEMPO FM1300 TL1400 3000 BR BKN010 RMK TESTE",
        "wind": {"degrees": 180, "speed_kts": 5},
    }
    info = formatar_metar(dados, 'pt', PT)
    assert info['rvr'] == ["Pista 10: entre 800 m e 1200 m, aumentando", "Pista 28L: menos de 50 m"]
    assert info['tendencia'] == [{
        "rotulo": "TEMPO FM1300 TL1400",
        "texto": "a partir das 13:00Z, até 14:00Z: 3000 m, Névoa úmida, BKN 1000 ft",
    }]
    assert formatar_metar(dados, 'en', EN)['rvr'][1] == "Runway 28L: less than 50 m"


def test_tendencia_nosig_e_sem_tendencia():
    nosig = formatar_metar({"raw_text": "METAR SBGL 201200Z 18005KT CAVOK 25/12 Q1015 NOSIG"}, 'pt', PT)
    assert nosig['tendencia'] == [{"rotulo": "NOSIG", "texto": "Sem mudança significativa prevista (NOSIG)"}]
    assert nosig['rvr'] == []
    sem = formatar_metar({"raw_text": "METAR SBGL 201200Z 18005KT CAVOK 25/12 Q1015"}, 'pt', PT)
    assert sem['tendencia'] == []
