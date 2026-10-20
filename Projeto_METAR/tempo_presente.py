"""Decodifica os códigos de tempo presente do METAR/TAF (ex.: -RA, VCSH, +TSRA).

Em vez de traduzir o texto em inglês que a API devolve ("Nearby showers"),
lemos o código ICAO e montamos a frase em português ou inglês. Assim
qualquer combinação válida sai traduzida, mesmo que nunca tenha aparecido antes.

Um código tem até quatro partes, nesta ordem:
    intensidade (- ou +)  ·  proximidade (VC)  ·  descritor (SH, TS...)  ·  fenômeno(s) (RA, FG...)
Exemplo: -SHRA = leve + pancadas + chuva -> "Pancadas de chuva leve".

Terminologia em português conforme a tabela de tempo presente do DECEA
("Como decodificar o METAR e o SPECI", Central de Ajuda do DECEA / ICA 105-16):
"-" = leve, sem sinal = moderada, "+" = forte, VC = nas vizinhanças.
"""

# Fenômenos: código -> (português, gênero), inglês
# Gênero/número: 'm', 'f', 'mp' (masc. plural), 'fp' (fem. plural), para concordar "fraco/fraca/fracos"
FENOMENOS = {
    # Precipitação
    'DZ': (('chuvisco', 'm'), 'drizzle'),
    'RA': (('chuva', 'f'), 'rain'),
    'SN': (('neve', 'f'), 'snow'),
    'SG': (('grãos de neve', 'mp'), 'snow grains'),
    'IC': (('cristais de gelo', 'mp'), 'ice crystals'),
    'PL': (('pelotas de gelo', 'fp'), 'ice pellets'),
    'GR': (('granizo', 'm'), 'hail'),
    'GS': (('granizo pequeno e/ou grãos de neve', 'm'), 'small hail and/or snow pellets'),
    'UP': (('precipitação desconhecida', 'f'), 'unknown precipitation'),
    # Obscurecimento
    'BR': (('névoa úmida', 'f'), 'mist'),
    'FG': (('nevoeiro', 'm'), 'fog'),
    'FU': (('fumaça', 'f'), 'smoke'),
    'VA': (('cinzas vulcânicas', 'fp'), 'volcanic ash'),
    'DU': (('poeira extensa', 'f'), 'widespread dust'),
    'SA': (('areia', 'f'), 'sand'),
    'HZ': (('névoa seca', 'f'), 'haze'),
    # Outros
    'PO': (('poeira/areia em redemoinhos', 'f'), 'dust/sand whirls'),
    'SQ': (('tempestade', 'f'), 'squall'),
    'FC': (('nuvem(ns) funil', 'f'), 'funnel cloud(s)'),
    'SS': (('tempestade de areia', 'f'), 'sandstorm'),
    'DS': (('tempestade de poeira', 'f'), 'duststorm'),
}

# Fenômenos que aceitam intensidade (sem sinal = moderada)
PRECIPITACAO = {'DZ', 'RA', 'SN', 'SG', 'PL', 'GR', 'GS'}
# Aceitam só "forte" (+SS, +DS); sem sinal não se diz "moderada"
SO_FORTE = {'SS', 'DS'}

GENERO = {'m': 0, 'f': 1, 'mp': 2, 'fp': 3}

# Descritores que viram adjetivo depois do fenômeno: código -> (m, f, mp, fp), inglês
ADJETIVOS = {
    'MI': (('baixo', 'baixa', 'baixos', 'baixas'), 'shallow'),
    'BC': (('em bancos',) * 4, 'patches of'),
    'PR': (('parcial', 'parcial', 'parciais', 'parciais'), 'partial'),
    'DR': (('flutuante', 'flutuante', 'flutuantes', 'flutuantes'), 'low drifting'),
    'BL': (('soprado', 'soprada', 'soprados', 'sopradas'), 'blowing'),
    'FZ': (('congelante', 'congelante', 'congelantes', 'congelantes'), 'freezing'),
}
DESCRITORES = set(ADJETIVOS) | {'SH', 'TS'}

INTENSIDADE_PT = {
    '-': ('leve', 'leve', 'leves', 'leves'),
    '+': ('forte', 'forte', 'fortes', 'fortes'),
    '': ('moderado', 'moderada', 'moderados', 'moderadas'),
}
INTENSIDADE_EN = {'-': 'light', '+': 'heavy', '': 'moderate'}

ESPECIAIS = {
    'NSW': {'pt': "Sem tempo significativo", 'en': "No significant weather"},
    # +FC é como o METAR indica tornado ou tromba d'água
    '+FC': {'pt': "Tornado ou tromba d'água", 'en': "Tornado or waterspout"},
}


def _separar(codigo):
    """'-VCSHRA' -> ('-', True, 'SH', ['RA']). Devolve None se o código não for válido."""
    c = codigo.strip().upper()
    intensidade = ''
    if c[:1] in ('-', '+'):
        intensidade, c = c[0], c[1:]
    vizinhanca = c.startswith('VC')
    if vizinhanca:
        c = c[2:]
    descritor = None
    if c[:2] in DESCRITORES:
        descritor, c = c[:2], c[2:]

    if len(c) % 2:
        return None
    fenomenos = [c[i:i + 2] for i in range(0, len(c), 2)]
    if any(f not in FENOMENOS for f in fenomenos):
        return None
    if not fenomenos and not descritor:
        return None
    return intensidade, vizinhanca, descritor, fenomenos


def _leva_intensidade(fenomeno, intensidade, vizinhanca, descritor):
    """Fraca/moderada/forte só faz sentido para precipitação. Sem sinal = moderada,
    exceto em neve/areia soprada (BL, DR) e afins, onde a ausência de sinal não indica intensidade."""
    if vizinhanca:
        return False
    if fenomeno in SO_FORTE:
        return intensidade == '+'
    if fenomeno not in PRECIPITACAO:
        return False
    return bool(intensidade) or descritor not in ('MI', 'BC', 'PR', 'DR', 'BL')


def _texto_pt(intensidade, vizinhanca, descritor, fenomenos):
    partes = []
    for i, codigo in enumerate(fenomenos):
        nome, genero = FENOMENOS[codigo][0]
        g = GENERO[genero]
        if codigo == 'DU' and descritor in ('BL', 'DR'):
            nome = 'poeira'  # BLDU = poeira soprada (não "poeira extensa soprada")
        if descritor in ADJETIVOS and i == 0:
            nome += ' ' + ADJETIVOS[descritor][0][g]
        # A intensidade vale para a precipitação (sem sinal = moderada)
        if i == 0 and _leva_intensidade(codigo, intensidade, vizinhanca, descritor):
            nome += ' ' + INTENSIDADE_PT[intensidade][g]
        partes.append(nome)
    fenomeno = ' e '.join(partes)

    if descritor == 'SH':
        texto = f"pancadas de {fenomeno}" if fenomeno else "pancadas"
    elif descritor == 'TS':
        texto = f"trovoada com {fenomeno}" if fenomeno else "trovoada"
    else:
        texto = fenomeno

    if vizinhanca:
        texto += " nas vizinhanças"
    return texto


def _texto_en(intensidade, vizinhanca, descritor, fenomenos):
    partes = [FENOMENOS[c][1] for c in fenomenos]
    if fenomenos and fenomenos[0] == 'DU' and descritor in ('BL', 'DR'):
        partes[0] = 'dust'
    if partes and descritor in ADJETIVOS:
        partes[0] = f"{ADJETIVOS[descritor][1]} {partes[0]}"
    if partes and _leva_intensidade(fenomenos[0], intensidade, vizinhanca, descritor):
        partes[0] = f"{INTENSIDADE_EN[intensidade]} {partes[0]}"
    fenomeno = ' and '.join(partes)

    if descritor == 'SH':
        texto = f"{fenomeno} showers" if fenomeno else "showers"
    elif descritor == 'TS':
        texto = f"thunderstorm with {fenomeno}" if fenomeno else "thunderstorm"
    else:
        texto = fenomeno

    if vizinhanca:
        texto += " in the vicinity"
    return texto


def decodificar(codigo, idioma):
    """Código de tempo presente -> frase no idioma pedido, ou None se não reconhecer."""
    if not codigo:
        return None
    especial = ESPECIAIS.get(codigo.strip().upper())
    if especial:
        return especial[idioma]

    partes = _separar(codigo)
    if partes is None:
        return None
    texto = _texto_pt(*partes) if idioma == 'pt' else _texto_en(*partes)
    return texto[0].upper() + texto[1:]
