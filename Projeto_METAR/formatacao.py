"""Transforma os dados brutos das fontes no que os cartões da tela mostram.

Funções puras: recebem dicionários e devolvem dicionários, sem acessar rede.
Por isso dá para testar cada uma com dados de exemplo (ver tests/).
"""
import re
from datetime import datetime

from tempo_presente import decodificar

# Reserva: tradução pelo texto em inglês, usada só quando a API não manda o código
TRADUCAO_FENOMENOS = {
    # Intensidade e Proximidade
    "light": "leve",
    "heavy": "forte",
    "vicinity": "nas proximidades",

    # Descritores
    "shallow": "raso",
    "patches": "em bancos",
    "partial": "parcial",
    "low drifting": "baixa altura (soprada)",
    "blowing": "alta altura (soprada)",
    "showers": "pancadas",
    "thunderstorm": "trovoada",
    "thunderstorms": "trovoadas",
    "freezing": "congelante",

    # Precipitação
    "light rain": "chuva leve",
    "rain": "chuva",
    "heavy rain": "chuva forte",
    "light drizzle": "chuvisco leve",
    "drizzle": "chuvisco",
    "heavy drizzle": "chuvisco forte",
    "light snow": "neve leve",
    "snow": "neve",
    "heavy snow": "neve forte",
    "snow grains": "grãos de neve",
    "ice crystals": "cristais de gelo",
    "ice pellets": "pelotas de gelo",
    "hail": "granizo",
    "small hail": "granizo pequeno",
    "light rain showers": "pancadas de chuva leve",
    "rain showers": "pancadas de chuva",
    "heavy rain showers": "pancadas de chuva forte",
    "snow showers": "pancadas de neve",
    "hail showers": "pancadas de granizo",

    # Obscurecimento (Visibilidade reduzida)
    "mist": "névoa úmida",
    "fog": "nevoeiro",
    "smoke": "fumaça",
    "volcanic ash": "cinzas vulcânicas",
    "widespread dust": "poeira generalizada",
    "sand": "areia",
    "haze": "névoa seca",

    # Outros Fenômenos
    "well-developed dust/sand whirls": "redemoinhos de poeira/areia",
    "squall": "tempestade",
    "squalls": "tempestades",
    "funnel cloud": "nuvem funil (tornado/tromba d'água)",
    "sandstorm": "tempestade de areia",
    "duststorm": "tempestade de poeira"
}


def traduzir_condicoes(condicoes, idioma, t):
    """Lista de fenômenos da API -> texto único no idioma escolhido.

    Usa o código ICAO (ex.: VCSH) para montar a frase. O texto em inglês da
    API só é usado se o código vier vazio ou for desconhecido.
    """
    termos = []
    for c in condicoes or []:
        texto = decodificar(c.get('code', ''), idioma)
        if texto is None:
            texto_en = c.get('text', '').lower().strip()
            if not texto_en:
                continue
            texto = TRADUCAO_FENOMENOS.get(texto_en, texto_en) if idioma == 'pt' else texto_en
            texto = texto.capitalize()
        termos.append(texto)
    return ", ".join(termos) if termos else t['sem_fenomenos']


def _numero(valor):
    """'9999.0', 9999.0 ou '9999' -> 9999 (int). Devolve None se não for número."""
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    return int(numero) if numero == int(numero) else numero


def formatar_vento(vento, t):
    vento = vento or {}
    velocidade = _numero(vento.get('speed_kts')) or 0
    direcao = _numero(vento.get('degrees'))
    if velocidade == 0:
        return t['vento_calmo']
    if direcao is None:
        texto = f"{t['vento_variavel']}, {velocidade} kt"
    else:
        texto = t['vento_fmt'].format(dir=direcao, vel=velocidade)
    if vento.get('gust_kts'):
        texto += t['rajada_fmt'].format(raj=vento['gust_kts'])
    return texto


def formatar_visibilidade(visibilidade, t):
    metros = _numero((visibilidade or {}).get('meters'))
    if metros is None:
        return t['vis_ampla']
    # No METAR, 9999 significa "10 km ou mais"
    if metros >= 9999:
        return t['vis_10km']
    return f"{metros} m"


def hora_utc(iso):
    """'2026-10-19T12:00:00Z' -> '19/10 12:00Z'. Se não reconhecer, devolve o original."""
    if not iso:
        return ''
    try:
        data = datetime.fromisoformat(str(iso).replace('Z', '+00:00'))
    except ValueError:
        return str(iso)
    return data.strftime('%d/%m %H:%MZ')


def formatar_metar(dados, idioma, t):
    teto = (dados.get('ceiling') or {}).get('feet')
    qnh = _numero((dados.get('barometer') or {}).get('hpa'))
    return {
        "bruto": dados['raw_text'],
        "visibilidade": formatar_visibilidade(dados.get('visibility'), t),
        "teto": f"{_numero(teto)} ft" if teto is not None else t['sem_teto'],
        "vento": formatar_vento(dados.get('wind'), t),
        "qnh": f"{qnh} hPa" if qnh is not None else "---",
        "tempo_presente": traduzir_condicoes(dados.get('conditions'), idioma, t),
    }


def formatar_nuvens(nuvens, t):
    """[{'code': 'BKN', 'feet': 2000}, {'code': 'FEW', 'feet': 3000, 'type': 'CB'}] -> 'BKN 2000 ft, FEW 3000 ft CB'"""
    camadas = []
    for n in nuvens or []:
        codigo = n.get('code', '')
        altura = n.get('feet') or n.get('base_feet_agl')
        camada = f"{codigo} {altura} ft" if altura else codigo
        if n.get('type'):
            camada += f" {n['type']}"
        camadas.append(camada.strip())
    return ", ".join(c for c in camadas if c) or t['nao_informado']


def formatar_taf(dados, idioma, t):
    periodos = []
    for previsao in dados.get('forecast', []):
        indicador = ((previsao.get('change') or {}).get('indicator') or {}).get('code')
        probabilidade = (previsao.get('change') or {}).get('probability')
        if indicador and probabilidade:
            mudanca = f"PROB{probabilidade} {indicador}" if indicador != 'PROB' else f"PROB{probabilidade}"
        else:
            mudanca = indicador or t['base']

        horario = previsao.get('timestamp') or {}
        periodos.append({
            "mudanca": mudanca,
            "inicio": hora_utc(horario.get('from')),
            "fim": hora_utc(horario.get('to')),
            "vento": formatar_vento(previsao.get('wind'), t) if previsao.get('wind') else t['nao_informado'],
            "visibilidade": formatar_visibilidade(previsao.get('visibility'), t) if previsao.get('visibility') else t['nao_informado'],
            "nuvens": formatar_nuvens(previsao.get('clouds'), t),
            "tempo": traduzir_condicoes(previsao.get('conditions'), idioma, t) if previsao.get('conditions') else t['nao_informado'],
        })
    return {"bruto": dados['raw_text'], "periodos": periodos}


def data_notam(valor, t):
    """Datas do AISWEB vêm como AAMMDDHHMM ('2610191200'), 'PERM' ou com sufixo 'EST'."""
    valor = (valor or '').strip()
    if not valor:
        return t['nao_informado']
    if valor.upper() == 'PERM':
        return t['permanente']

    estimado = valor.upper().endswith('EST')
    numeros = re.sub(r'\D', '', valor)
    if len(numeros) != 10:
        return valor
    texto = f"{numeros[4:6]}/{numeros[2:4]}/20{numeros[0:2]} {numeros[6:8]}:{numeros[8:10]}Z"
    return f"{texto} {t['estimado']}" if estimado else texto


def formatar_notams(notams, t):
    return [
        {
            "numero": n.get('n') or n.get('id') or '',
            "inicio": data_notam(n.get('b'), t),
            "fim": data_notam(n.get('c'), t),
            "horario": n.get('d', ''),
            "texto": n.get('e', ''),
        }
        for n in notams
    ]
