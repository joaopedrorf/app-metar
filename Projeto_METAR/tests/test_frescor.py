from datetime import datetime, timezone

from exemplos import METAR_SBGL, TAF_SBGL
from frescor import idade_texto, resolver_data, selo_falha, selo_metar, selo_notam, selo_taf
from textos import TEXTOS

PT = TEXTOS['pt']
EN = TEXTOS['en']


def utc(dia, hora, minuto=0, mes=10, ano=2026):
    return datetime(ano, mes, dia, hora, minuto, tzinfo=timezone.utc)


# ---------- datas a partir de dia/hora/minuto ----------

def test_resolver_data_mesmo_mes():
    assert resolver_data(19, 18, 0, utc(19, 18, 25)) == utc(19, 18)


def test_resolver_data_virada_de_mes():
    # METAR do dia 31, lido logo depois da meia-noite do dia 1º
    assert resolver_data(31, 23, 0, utc(1, 0, 10, mes=11)) == utc(31, 23, mes=10)


def test_resolver_data_virada_de_ano():
    assert resolver_data(31, 23, 0, utc(1, 0, 10, mes=1, ano=2027)) == utc(31, 23, mes=12, ano=2026)


def test_resolver_data_hora_24_vira_meia_noite_do_dia_seguinte():
    assert resolver_data(20, 24, 0, utc(20, 10)) == utc(21, 0)


# ---------- idade ----------

def test_idade_texto():
    agora = utc(19, 18, 25)
    assert idade_texto(utc(19, 18, 25), agora, PT) == "agora mesmo"
    assert idade_texto(utc(19, 18), agora, PT) == "há 25 min"
    assert idade_texto(utc(19, 17), agora, PT) == "há 1 h 25 min"
    assert idade_texto(utc(19, 15, 25), agora, PT) == "há 3 h"
    assert idade_texto(utc(19, 18), agora, EN) == "25 min ago"


def test_idade_nunca_negativa():
    # Relógio do servidor um pouco atrasado em relação à estação
    assert idade_texto(utc(19, 18, 5), utc(19, 18), PT) == "agora mesmo"


# ---------- METAR ----------

def test_metar_recente():
    selo = selo_metar(METAR_SBGL, utc(19, 18, 25), PT)
    assert selo['estado'] == 'ok'
    assert selo['texto'] == "Observado às 18:00Z (há 25 min)"
    assert selo['aviso'] is None


def test_metar_com_mais_de_1_hora():
    selo = selo_metar(METAR_SBGL, utc(19, 19, 30), PT)
    assert selo['estado'] == 'velho'
    assert selo['texto'] == "Observado às 18:00Z (há 1 h 30 min)"
    assert "Mais de 1 h" in selo['aviso']


def test_metar_exatamente_1_hora_ainda_ok():
    assert selo_metar(METAR_SBGL, utc(19, 19), PT)['estado'] == 'ok'


def test_metar_em_ingles():
    selo = selo_metar(METAR_SBGL, utc(19, 20), EN)
    assert selo['texto'] == "Observed at 18:00Z (2 h ago)"
    assert "Over 1 h old" in selo['aviso']


def test_metar_sem_hora_nao_quebra():
    assert selo_metar({'raw_text': 'METAR SBGL'}, utc(19, 18), PT) is None


# ---------- TAF (emitido 191630Z, validade 1918/2024) ----------

def test_taf_dentro_da_validade():
    selo = selo_taf(TAF_SBGL, utc(19, 19, 30), PT)
    assert selo['estado'] == 'ok'
    assert selo['texto'] == "Emitido às 16:30Z (há 3 h)"
    assert selo['aviso'] is None


def test_taf_vencido():
    selo = selo_taf(TAF_SBGL, utc(21, 1), PT)
    assert selo['estado'] == 'velho'
    assert selo['aviso'] == "Validade terminou às 00:00Z."


def test_taf_vencido_em_ingles():
    assert selo_taf(TAF_SBGL, utc(21, 1), EN)['aviso'] == "Validity ended at 00:00Z."


# ---------- NOTAM e falha ----------

def test_notam_mostra_hora_da_consulta():
    assert selo_notam([], utc(19, 18, 25), PT)['texto'] == "Consultado às 18:25Z"
    assert selo_notam([], utc(19, 18, 25), EN)['texto'] == "Fetched at 18:25Z"


def test_falha():
    selo = selo_falha(utc(19, 18, 25), PT)
    assert selo == {"estado": "falha", "texto": "Falhou às 18:25Z", "aviso": None}
