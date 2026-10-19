"""Monta o briefing completo de um aeródromo: METAR, TAF e NOTAM.

As três consultas rodam em paralelo (cada uma pode levar alguns segundos) e
cada seção falha sozinha: se o AISWEB cair, METAR e TAF continuam na tela.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import clientes
from clientes import ErroFonte
from formatacao import formatar_metar, formatar_notams, formatar_taf


def _secao(buscar, formatar, aeroporto, t):
    """Busca e formata uma seção. Devolve {'dados': ..., 'erro': None} ou o contrário."""
    try:
        bruto = buscar(aeroporto)
        return {"dados": formatar(bruto), "erro": None}
    except ErroFonte as e:
        return {"dados": None, "erro": t['erros'].get(e.codigo, t['erros']['indisponivel'])}
    except KeyError:
        # A fonte respondeu sem o texto bruto (raw_text)
        return {"dados": None, "erro": t['erros']['sem_dados_brutos']}


def montar_briefing(aeroporto, idioma, t):
    tarefas = {
        "metar": (clientes.buscar_metar, lambda d: formatar_metar(d, idioma, t)),
        "taf": (clientes.buscar_taf, lambda d: formatar_taf(d, idioma, t)),
        "notam": (clientes.buscar_notams, lambda d: formatar_notams(d, t)),
    }
    with ThreadPoolExecutor(max_workers=len(tarefas)) as executor:
        futuros = {
            nome: executor.submit(_secao, buscar, formatar, aeroporto, t)
            for nome, (buscar, formatar) in tarefas.items()
        }
        briefing = {nome: futuro.result() for nome, futuro in futuros.items()}

    briefing["aeroporto"] = aeroporto
    briefing["gerado_em"] = datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%MZ')
    return briefing
