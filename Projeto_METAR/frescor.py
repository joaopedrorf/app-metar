"""Selo de frescor: mostra, em cada seção, de quando é o dado e há quanto tempo.

O isolamento de falhas já impede que uma fonte derrube as outras. Este módulo
cuida da outra metade: deixar visível se o dado é recente, velho ou se a
consulta falhou, sem o usuário precisar ler a hora dentro do código bruto.

O app só mostra a idade do dado. Ele não decide se o aeródromo está aberto ou
fechado: essa decisão continua sendo humana.

Funções puras: recebem o dado bruto e a hora "agora" (UTC) e devolvem um
dicionário {'estado': 'ok' | 'velho' | 'falha', 'texto': ..., 'aviso': ...}.
"""
import re
from datetime import datetime, timedelta, timezone

# METAR é horário: passou de 1 h, provavelmente o próximo ainda não chegou
LIMITE_METAR = timedelta(hours=1)

DIA_HORA_MIN = re.compile(r'\b(\d{2})(\d{2})(\d{2})Z\b')


def agora_utc():
    return datetime.now(timezone.utc)


def _mes(ano, mes, desloca):
    """Soma `desloca` meses a (ano, mes). Ex.: (2026, 1, -1) -> (2025, 12)"""
    indice = ano * 12 + (mes - 1) + desloca
    return indice // 12, indice % 12 + 1


def resolver_data(dia, hora, minuto, referencia):
    """Os códigos só trazem dia/hora/minuto (ex.: 191800Z). Descobre o mês e o ano.

    Testa o mês anterior, o atual e o seguinte da `referencia` e fica com a
    data mais próxima dela. Assim, um METAR do dia 31 lido no dia 1º cai no
    mês anterior. Hora 24 (comum no fim da validade do TAF) vira 00 do dia
    seguinte. Devolve None se o dia não existir em nenhum dos três meses.
    """
    candidatas = []
    for desloca in (-1, 0, 1):
        ano, mes = _mes(referencia.year, referencia.month, desloca)
        try:
            data = datetime(ano, mes, dia, 0, minuto, tzinfo=timezone.utc)
        except ValueError:
            continue
        candidatas.append(data + timedelta(hours=hora))
    if not candidatas:
        return None
    return min(candidatas, key=lambda d: abs(d - referencia))


def idade_texto(desde, agora, t):
    """Diferença entre duas horas em texto curto: 'há 25 min', 'há 1 h 10 min'."""
    minutos = max(0, int((agora - desde).total_seconds() // 60))
    if minutos < 1:
        return t['frescor_agora']
    horas, resto = divmod(minutos, 60)
    if horas == 0:
        tempo = f"{resto} min"
    elif resto == 0:
        tempo = f"{horas} h"
    else:
        tempo = f"{horas} h {resto} min"
    return t['frescor_ha'].format(tempo=tempo)


def _hora(data):
    return data.strftime('%H:%MZ')


def selo_metar(dados, agora, t):
    """Hora da observação lida do próprio METAR (grupo 191800Z)."""
    grupo = DIA_HORA_MIN.search((dados or {}).get('raw_text') or '')
    if not grupo:
        return None
    observado = resolver_data(int(grupo[1]), int(grupo[2]), int(grupo[3]), agora)
    if observado is None:
        return None

    selo = {
        "estado": "ok",
        "texto": t['frescor_observado'].format(hora=_hora(observado), idade=idade_texto(observado, agora, t)),
        "aviso": None,
    }
    if agora - observado > LIMITE_METAR:
        selo["estado"] = "velho"
        selo["aviso"] = t['frescor_metar_velho']
    return selo


def selo_taf(dados, agora, t):
    """Hora de emissão do TAF e aviso se a validade já terminou."""
    bruto = ((dados or {}).get('raw_text') or '').replace('=', ' ')
    emitido_grupo = DIA_HORA_MIN.search(bruto)
    validade = re.search(r'\b\d{4}/(\d{2})(\d{2})\b', bruto)
    if not emitido_grupo:
        return None
    emitido = resolver_data(int(emitido_grupo[1]), int(emitido_grupo[2]), int(emitido_grupo[3]), agora)
    if emitido is None:
        return None

    selo = {
        "estado": "ok",
        "texto": t['frescor_emitido'].format(hora=_hora(emitido), idade=idade_texto(emitido, agora, t)),
        "aviso": None,
    }
    if validade:
        # O fim da validade vem depois da emissão (até ~30 h), por isso a referência é a emissão
        fim = resolver_data(int(validade[1]), int(validade[2]), 0, emitido)
        if fim is not None and agora >= fim:
            selo["estado"] = "velho"
            selo["aviso"] = t['frescor_taf_vencido'].format(hora=_hora(fim))
    return selo


def selo_notam(notams, agora, t):
    """O AISWEB devolve os NOTAM em vigor no momento: o que importa é a hora da consulta."""
    return {"estado": "ok", "texto": t['frescor_consultado'].format(hora=_hora(agora)), "aviso": None}


def selo_falha(agora, t):
    return {"estado": "falha", "texto": t['frescor_falhou'].format(hora=_hora(agora)), "aviso": None}
