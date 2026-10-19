"""Textos da interface em português e inglês.

O template usa `t.chave` em vez de repetir {% if idioma == 'pt' %} em cada
rótulo. Para adicionar um idioma, basta criar mais um dicionário aqui.
"""

TEXTOS = {
    'pt': {
        'titulo': "Briefing Meteorológico",
        'rotulo_icao': "Código ICAO do Aeródromo:",
        'botao': "Gerar briefing",
        'atencao': "Atenção:",
        'gerado_em': "Gerado em",
        'aviso_oficial': "Uso informativo. Não substitui o briefing oficial do DECEA (AISWEB/REDEMET).",

        'metar_bruto': "METAR BRUTO:",
        'decodificado': "Dados Decodificados",
        'visibilidade': "Visibilidade Horizontal",
        'visibilidade_curta': "Visibilidade",
        'teto': "Teto (Camadas BKN/OVC)",
        'vento': "Vento",
        'qnh': "Pressão Atmosférica (QNH)",
        'tempo_presente': "Tempo Presente (Fenômenos)",

        'taf_bruto': "TAF BRUTO:",
        'periodos': "Períodos da Previsão",
        'periodo': "Período",
        'mudanca': "Mudança",
        'nuvens': "Nuvens",
        'tempo': "Tempo",
        'base': "Previsão base",

        'notam_vigentes': "NOTAM em vigor",
        'nenhum_notam': "Nenhum NOTAM em vigor para este aeródromo.",
        'inicio': "Início",
        'fim': "Fim",

        # Valores formatados
        'vis_ampla': "Não informada / Ampla",
        'sem_teto': "Céu Claro (Sem Teto)",
        'vento_fmt': "{dir}° com {vel} kt",
        'rajada_fmt': ", rajadas de {raj} kt",
        'vento_variavel': "Variável",
        'sem_fenomenos': "Sem fenômenos significativos",
        'nao_informado': "—",
        'permanente': "Permanente",
        'estimado': "(estimado)",

        # Erros
        'icao_invalido': "Por favor, insira um código ICAO válido com 4 letras.",
        'erros': {
            'chave_invalida': "Chave de API inválida ou não autorizada.",
            'indisponivel': "Serviço indisponível no momento.",
            'conexao': "Falha na conexão com o servidor.",
            'nao_encontrado': "Nenhum dado encontrado para este aeródromo.",
            'sem_dados_brutos': "Dados brutos indisponíveis.",
            'sem_chave_notam': "Consulta de NOTAM não configurada (chave do AISWEB ausente).",
            'fora_do_brasil': "NOTAM disponível apenas para aeródromos brasileiros (fonte: AISWEB/DECEA).",
        },
    },
    'en': {
        'titulo': "Weather Briefing",
        'rotulo_icao': "Aerodrome ICAO Code:",
        'botao': "Get briefing",
        'atencao': "Attention:",
        'gerado_em': "Generated at",
        'aviso_oficial': "For information only. Not a substitute for an official briefing.",

        'metar_bruto': "RAW METAR:",
        'decodificado': "Decoded Data",
        'visibilidade': "Horizontal Visibility",
        'visibilidade_curta': "Visibility",
        'teto': "Ceiling (BKN/OVC Layers)",
        'vento': "Wind",
        'qnh': "Altimeter Setting (QNH)",
        'tempo_presente': "Present Weather (Phenomena)",

        'taf_bruto': "RAW TAF:",
        'periodos': "Forecast Periods",
        'periodo': "Period",
        'mudanca': "Change",
        'nuvens': "Clouds",
        'tempo': "Weather",
        'base': "Base forecast",

        'notam_vigentes': "NOTAMs in force",
        'nenhum_notam': "No NOTAMs in force for this aerodrome.",
        'inicio': "From",
        'fim': "To",

        'vis_ampla': "Not reported / Wide",
        'sem_teto': "Clear Sky (No Ceiling)",
        'vento_fmt': "{dir}° at {vel} kt",
        'rajada_fmt': ", gusting {raj} kt",
        'vento_variavel': "Variable",
        'sem_fenomenos': "No significant phenomena",
        'nao_informado': "—",
        'permanente': "Permanent",
        'estimado': "(estimated)",

        'icao_invalido': "Please enter a valid 4-letter ICAO code.",
        'erros': {
            'chave_invalida': "Invalid or unauthorized API Key.",
            'indisponivel': "Service currently unavailable.",
            'conexao': "Server connection failed.",
            'nao_encontrado': "No data found for this aerodrome.",
            'sem_dados_brutos': "Raw data unavailable.",
            'sem_chave_notam': "NOTAM lookup not configured (AISWEB key missing).",
            'fora_do_brasil': "NOTAMs are only available for Brazilian aerodromes (source: AISWEB/DECEA).",
        },
    },
}
