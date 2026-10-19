"""Acesso às fontes externas: CheckWX (METAR e TAF) e AISWEB/DECEA (NOTAM).

Cada função devolve os dados brutos da fonte ou levanta ErroFonte com um
código curto. Quem chama decide como mostrar o erro, em qual idioma.
"""
import os
import xml.etree.ElementTree as ET

import requests

CHECKWX_URL = "https://api.checkwx.com/{tipo}/{aeroporto}/decoded"
AISWEB_URL = os.getenv('AISWEB_URL', "https://api.decea.mil.br/aisweb/")

TIMEOUT = 10

# Prefixos ICAO usados por aeródromos brasileiros (os demais "S..." são de
# outros países da América do Sul, que o AISWEB não cobre).
PREFIXOS_BRASIL = ('SB', 'SD', 'SI', 'SJ', 'SN', 'SS', 'SW')


class ErroFonte(Exception):
    """Falha ao buscar dados de uma fonte. `codigo` vira mensagem em textos.py."""

    def __init__(self, codigo):
        super().__init__(codigo)
        self.codigo = codigo


def _buscar_checkwx(tipo, aeroporto):
    cabecalho = {"X-API-Key": os.getenv('API_KEY')}
    url = CHECKWX_URL.format(tipo=tipo, aeroporto=aeroporto)
    try:
        resposta = requests.get(url, headers=cabecalho, timeout=TIMEOUT)
    except requests.exceptions.RequestException:
        raise ErroFonte('conexao')

    if resposta.status_code == 401:
        raise ErroFonte('chave_invalida')
    if resposta.status_code != 200:
        raise ErroFonte('indisponivel')

    try:
        dados = resposta.json()
    except ValueError:
        raise ErroFonte('indisponivel')

    if dados.get('results', 0) == 0 or not dados.get('data'):
        raise ErroFonte('nao_encontrado')
    return dados['data'][0]


def buscar_metar(aeroporto):
    return _buscar_checkwx('metar', aeroporto)


def buscar_taf(aeroporto):
    return _buscar_checkwx('taf', aeroporto)


def buscar_notams(aeroporto):
    """Lista de NOTAM em vigor (cada um é um dicionário com os campos do AISWEB).

    O AISWEB só cobre aeródromos brasileiros e exige cadastro gratuito
    (apiKey e apiPass) no próprio site do DECEA.
    """
    if not aeroporto.startswith(PREFIXOS_BRASIL):
        raise ErroFonte('fora_do_brasil')
    chave = os.getenv('AISWEB_API_KEY')
    senha = os.getenv('AISWEB_API_PASS')
    if not chave or not senha:
        raise ErroFonte('sem_chave_notam')

    parametros = {
        "apiKey": chave,
        "apiPass": senha,
        "area": "notam",
        "icaocode": aeroporto,
    }
    try:
        resposta = requests.get(AISWEB_URL, params=parametros, timeout=TIMEOUT)
    except requests.exceptions.RequestException:
        raise ErroFonte('conexao')

    if resposta.status_code != 200:
        raise ErroFonte('indisponivel')
    return ler_xml_notams(resposta.content)


def ler_xml_notams(conteudo):
    """Converte o XML do AISWEB em lista de dicionários.

    Formato esperado: <aisweb><notam total="N"><item><n>...</n><e>...</e></item>...
    Cada filho de <item> vira uma chave do dicionário.
    """
    try:
        raiz = ET.fromstring(conteudo)
    except ET.ParseError:
        raise ErroFonte('indisponivel')

    notams = []
    for item in raiz.iter('item'):
        notams.append({filho.tag: (filho.text or '').strip() for filho in item})
    return notams
