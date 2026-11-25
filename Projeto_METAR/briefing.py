"""Monta o briefing completo de um aeródromo: METAR, TAF e NOTAM.

As três consultas rodam em paralelo (cada uma pode levar alguns segundos) e
cada seção falha sozinha: se o AISWEB cair, METAR e TAF continuam na tela.
Cada seção também leva um selo de frescor (ver frescor.py).
"""
from concurrent.futures import ThreadPoolExecutor

import clientes
import frescor
from clientes import ErroFonte
from formatacao import formatar_metar, formatar_notams, formatar_taf

# Erros que não são queda da fonte, só falta de cobertura
SEM_COBERTURA = {'fora_do_brasil'}


def _secao(buscar, formatar, selo, aeroporto, t):
    """Busca e formata uma seção. Devolve {'dados', 'erro', 'selo'}.

    O selo diz de quando é o dado (ou a hora em que a fonte falhou). A hora é
    marcada assim que a fonte responde, então cada seção tem a sua.
    """
    try:
        bruto = buscar(aeroporto)
    except ErroFonte as e:
        erro = t['erros'].get(e.codigo, t['erros']['indisponivel'])
        # Fora da cobertura (ex.: NOTAM de aeródromo estrangeiro) não é falha: sem selo
        selo_erro = None if e.codigo in SEM_COBERTURA else frescor.selo_falha(frescor.agora_utc(), t)
        return {"dados": None, "erro": erro, "selo": selo_erro}
    agora = frescor.agora_utc()
    try:
        dados = formatar(bruto)
    except KeyError:
        # A fonte respondeu sem o texto bruto (raw_text)
        return {"dados": None, "erro": t['erros']['sem_dados_brutos'], "selo": frescor.selo_falha(agora, t)}
    return {"dados": dados, "erro": None, "selo": selo(bruto, agora, t)}


def montar_briefing(aeroporto, idioma, t):
    tarefas = {
        "metar": (clientes.buscar_metar, lambda d: formatar_metar(d, idioma, t), frescor.selo_metar),
        "taf": (clientes.buscar_taf, lambda d: formatar_taf(d, idioma, t), frescor.selo_taf),
        "notam": (clientes.buscar_notams, lambda d: formatar_notams(d, t), frescor.selo_notam),
    }
    with ThreadPoolExecutor(max_workers=len(tarefas)) as executor:
        futuros = {
            nome: executor.submit(_secao, buscar, formatar, selo, aeroporto, t)
            for nome, (buscar, formatar, selo) in tarefas.items()
        }
        briefing = {nome: futuro.result() for nome, futuro in futuros.items()}

    briefing["aeroporto"] = aeroporto
    briefing["gerado_em"] = frescor.agora_utc().strftime('%d/%m/%Y %H:%MZ')
    return briefing
