"""Lê o TAF bruto e separa cada período com o grupo de mudança como está no TAF.

Exemplo:
    TAF SBGL 191630Z 1918/2024 16010KT 9999 BKN020 TX31/2018Z TN22/2009Z
        TEMPO 1921/2001 4000 RA BKN010
        BECMG 2006/2008 VRB03KT CAVOK
vira:
    emitido 191630Z, validade 1918/2024, TX 31 °C às 2018Z, TN 22 °C às 2009Z
    períodos: [base 1918/2024], [TEMPO 1921/2001], [BECMG 2006/2008]

Assim a tela mostra "BECMG 2006/2008" igual ao TAF (ICA 105-16 / Anexo 3 da ICAO),
e dá para ver CAVOK e CB de cada período, que a API nem sempre decodifica.
"""
import re

VALIDADE = re.compile(r'\d{4}/\d{4}')


def _temperatura(valor):
    """'M02' -> -2, '31' -> 31"""
    return -int(valor[1:]) if valor.startswith('M') else int(valor)


def ler_taf(bruto):
    grupos = (bruto or '').replace('=', ' ').split()
    resultado = {'amd': False, 'cor': False, 'emitido': None, 'validade': None,
                 'tx': [], 'tn': [], 'periodos': []}

    # Cabeçalho: TAF [AMD|COR] SBGL 191630Z 1918/2024
    i = 0
    while i < len(grupos) and resultado['validade'] is None:
        g = grupos[i]
        if g == 'AMD':
            resultado['amd'] = True
        elif g == 'COR':
            resultado['cor'] = True
        elif re.fullmatch(r'\d{6}Z', g):
            resultado['emitido'] = g
        elif VALIDADE.fullmatch(g):
            resultado['validade'] = g
        i += 1

    atual = {'tipo': None, 'validade': resultado['validade'], 'grupos': []}
    resultado['periodos'].append(atual)

    while i < len(grupos):
        g = grupos[i]
        seguinte = grupos[i + 1] if i + 1 < len(grupos) else ''

        temp = re.fullmatch(r'(TX|TN)(M?\d{2})/(\d{4})Z', g)
        if temp:
            resultado[temp[1].lower()].append((_temperatura(temp[2]), temp[3]))
        elif re.fullmatch(r'FM\d{6}', g):
            atual = {'tipo': 'FM', 'validade': g[2:], 'grupos': []}
            resultado['periodos'].append(atual)
        elif g in ('PROB30', 'PROB40'):
            atual = {'tipo': g, 'validade': None, 'grupos': []}
            resultado['periodos'].append(atual)
            if VALIDADE.fullmatch(seguinte):
                atual['validade'] = seguinte
                i += 1
        elif g in ('BECMG', 'TEMPO'):
            # "PROB30 TEMPO 2003/2006" é um período só
            if atual['tipo'] in ('PROB30', 'PROB40') and atual['validade'] is None:
                atual['tipo'] += ' ' + g
            else:
                atual = {'tipo': g, 'validade': None, 'grupos': []}
                resultado['periodos'].append(atual)
            if VALIDADE.fullmatch(seguinte):
                atual['validade'] = seguinte
                i += 1
        else:
            atual['grupos'].append(g)
        i += 1

    for p in resultado['periodos']:
        if p['tipo'] == 'FM':
            p['rotulo'] = f"FM{p['validade']}"
        elif p['tipo']:
            p['rotulo'] = f"{p['tipo']} {p['validade'] or ''}".strip()
        else:
            p['rotulo'] = p['validade'] or ''
        p['cavok'] = 'CAVOK' in p['grupos']
    return resultado
