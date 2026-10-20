"""Lê do METAR bruto os grupos que a API não decodifica.

A CheckWX devolve vento, visibilidade, nuvens etc. já separados, mas não traz
alguns grupos previstos no METAR (ICA 105-16 / Anexo 3 da ICAO). Esses são
lidos aqui direto do texto:
    CAVOK, variação do vento (280V350), visibilidade mínima (1500SW),
    visibilidade vertical (VV002), camadas de nuvens com CB/TCU (FEW030CB),
    tempo recente (RERA) e cortante do vento (WS RWY17).
"""
import re

# Depois destes grupos vem RMK ou a tendência, que não fazem parte da observação
FIM_DA_OBSERVACAO = {'RMK', 'NOSIG', 'BECMG', 'TEMPO'}


def _grupos(bruto):
    grupos = []
    for g in (bruto or '').replace('=', ' ').split():
        if g in FIM_DA_OBSERVACAO:
            break
        grupos.append(g)
    return grupos


def ler_grupos(bruto):
    """Devolve um dicionário com o que encontrou (chaves ausentes = grupo não reportado)."""
    grupos = _grupos(bruto)
    resultado = {'cavok': 'CAVOK' in grupos, 'tempo_recente': [], 'cortante': [], 'nuvens': []}

    for i, g in enumerate(grupos):
        variacao = re.fullmatch(r'(\d{3})V(\d{3})', g)
        if variacao:
            resultado['variacao_vento'] = (int(variacao[1]), int(variacao[2]))
            continue

        minima = re.fullmatch(r'(\d{4})(N|NE|E|SE|S|SW|W|NW)', g)
        if minima:
            resultado['visibilidade_minima'] = (int(minima[1]), minima[2])
            continue

        nuvem = re.fullmatch(r'(FEW|SCT|BKN|OVC)(\d{3}|///)(CB|TCU|///)?', g)
        if nuvem:
            altura = int(nuvem[2]) * 100 if nuvem[2] != '///' else None
            tipo = nuvem[3] if nuvem[3] in ('CB', 'TCU') else None
            resultado['nuvens'].append({'code': nuvem[1], 'feet': altura, 'type': tipo})
            continue
        if g in ('NSC', 'NCD', 'SKC', 'CLR'):
            resultado['nuvens'].append({'code': g})
            continue

        vv = re.fullmatch(r'VV(\d{3}|///)', g)
        if vv:
            resultado['visibilidade_vertical'] = int(vv[1]) * 100 if vv[1] != '///' else None
            continue

        if g.startswith('RE') and len(g) > 2:
            resultado['tempo_recente'].append(g[2:])
            continue

        if g == 'WS':
            seguinte = grupos[i + 1] if i + 1 < len(grupos) else ''
            if seguinte == 'ALL':
                resultado['cortante'].append('ALL')
            else:
                pista = re.fullmatch(r'(?:RWY|R)(\d{2}[LCR]?)', seguinte)
                if pista:
                    resultado['cortante'].append(pista[1])
    return resultado
