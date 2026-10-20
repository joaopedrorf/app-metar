from formatacao import formatar_taf
from grupos_taf import ler_taf
from textos import TEXTOS

PT = TEXTOS['pt']

TAF = ("TAF AMD SBGL 201000Z 2012/2112 18010KT 9999 SCT030 TX31/2018Z TN22/2109Z "
       "BECMG 2013/2015 22015G25KT "
       "PROB30 TEMPO 2018/2022 3000 TSRA BKN015 FEW030CB "
       "FM210300 VRB03KT CAVOK "
       "PROB40 2106/2109 0800 FG VV002=")


def test_separa_os_periodos_como_no_taf():
    taf = ler_taf(TAF)
    assert taf['amd'] is True
    assert taf['emitido'] == '201000Z'
    assert taf['validade'] == '2012/2112'
    assert [p['rotulo'] for p in taf['periodos']] == [
        "2012/2112", "BECMG 2013/2015", "PROB30 TEMPO 2018/2022", "FM210300", "PROB40 2106/2109",
    ]
    assert taf['tx'] == [(31, '2018')]
    assert taf['tn'] == [(22, '2109')]
    assert taf['periodos'][3]['cavok'] is True


def test_temperatura_negativa():
    taf = ler_taf("TAF SBXX 201000Z 2012/2112 00000KT 9999 FEW020 TXM02/2015Z TNM10/2106Z")
    assert taf['tx'] == [(-2, '2015')]
    assert taf['tn'] == [(-10, '2106')]


def test_formatar_taf_usa_rotulos_cavok_e_cb_do_texto():
    dados = {"raw_text": TAF, "forecast": [{} for _ in range(5)]}
    taf = formatar_taf(dados, 'pt', PT)
    assert [p['mudanca'] for p in taf['periodos']] == [
        "Previsão base 2012/2112", "BECMG 2013/2015", "PROB30 TEMPO 2018/2022", "FM210300", "PROB40 2106/2109",
    ]
    assert taf['periodos'][2]['nuvens'] == "BKN 1500 ft, FEW 3000 ft CB"
    assert taf['periodos'][3]['visibilidade'] == "10 km ou mais (CAVOK)"
    assert taf['periodos'][4]['nuvens'] == "—"  # VV fica no texto; a API decodifica o resto
    cab = taf['cabecalho']
    assert cab['linhas'] == [
        "TAF emendado (AMD)",
        "Emitido dia 20 às 10:00Z",
        "Validade 2012/2112: dia 20 às 12Z até dia 21 às 12Z",
    ]
    assert cab['temperaturas'] == ["Máxima 31 °C (dia 20 às 18Z)", "Mínima 22 °C (dia 21 às 09Z)"]


def test_se_os_periodos_nao_batem_usa_a_api():
    dados = {"raw_text": TAF, "forecast": [{"change": {"indicator": {"code": "TEMPO"}}}]}
    assert formatar_taf(dados, 'pt', PT)['periodos'][0]['mudanca'] == "TEMPO"
