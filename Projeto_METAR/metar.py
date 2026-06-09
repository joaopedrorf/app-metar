import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv('API_KEY')
API_URL = "https://api.checkwx.com/metar/{aeroporto}/decoded"

# Dicionário abrangente de mapeamento Inglês -> Português para fenômenos do METAR
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

@app.route('/', methods=['GET', 'POST'])
def index():
    # Detecta o idioma selecionado (padrão 'pt')
    idioma = request.form.get('idioma', 'pt') if request.method == 'POST' else 'pt'

    if request.method != 'POST':
        return render_template('index.html', info=None, erro=None, idioma=idioma)

    aeroporto = request.form.get('icao', '').strip().upper()

    if not aeroporto or len(aeroporto) != 4:
        erro_txt = "Por favor, insira um código ICAO válido com 4 letras." if idioma == 'pt' else "Please enter a valid 4-letter ICAO code."
        return render_template('index.html', erro=erro_txt, info=None, idioma=idioma)

    url = API_URL.format(aeroporto=aeroporto)
    cabecalho = {"X-API-Key": API_KEY}

    try:
        resposta = requests.get(url, headers=cabecalho, timeout=10)
        
        if resposta.status_code == 401:
            erro_txt = "Chave de API inválida ou não autorizada." if idioma == 'pt' else "Invalid or unauthorized API Key."
            return render_template('index.html', erro=erro_txt, info=None, idioma=idioma)
        if resposta.status_code != 200:
            erro_txt = "Serviço meteorológico indisponível." if idioma == 'pt' else "Weather service unavailable."
            return render_template('index.html', erro=erro_txt, info=None, idioma=idioma)
            
        dados_completos = resposta.json()
    except (requests.exceptions.RequestException, ValueError):
        erro_txt = "Falha na conexão com o servidor." if idioma == 'pt' else "Server connection failed."
        return render_template('index.html', erro=erro_txt, info=None, idioma=idioma)

    if dados_completos.get('results', 0) == 0 or not dados_completos.get('data'):
        erro_txt = f"Aeródromo {aeroporto} não encontrado." if idioma == 'pt' else f"Aerodrome {aeroporto} not found."
        return render_template('index.html', erro=erro_txt, info=None, idioma=idioma)
    
    dados = dados_completos['data'][0]
    metar_bruto = dados.get('raw_text')
    
    if not metar_bruto:
        erro_txt = f"Dados brutos indisponíveis." if idioma == 'pt' else "Raw data unavailable."
        return render_template('index.html', erro=erro_txt, info=None, idioma=idioma)
    
    # Tratamento de Visibilidade e Teto com rótulos internacionais alternáveis
    visibilidade_val = dados.get('visibility', {}).get('meters')
    if visibilidade_val is not None:
        visibilidade_txt = f"{visibilidade_val} m"
    else:
        visibilidade_txt = "Não informada / Ampla" if idioma == 'pt' else "Not reported / Wide"
    
    teto_val = dados.get('ceiling', {}).get('feet')
    if teto_val is not None:
        teto_txt = f"{teto_val} ft"
    else:
        teto_txt = "Céu Claro (Sem Teto)" if idioma == 'pt' else "Clear Sky (No Ceiling)"
    
    vento_dir = dados.get('wind', {}).get('degrees', 0)
    vento_vel = dados.get('wind', {}).get('speed_kts', 0)
    vento_txt = f"{vento_dir}° com {vento_vel} kt" if idioma == 'pt' else f"{vento_dir}° at {vento_vel} kt"
    
    qnh_val = dados.get('barometer', {}).get('hpa', "---")

    # Extração e Tradução do Tempo Presente
    condicoes_lista = dados.get('conditions', [])
    if condicoes_lista:
        termos = []
        for c in condicoes_lista:
            texto_en = c.get('text', '').lower().strip()
            if texto_en:
                if idioma == 'pt':
                    texto_formatado = TRADUCAO_FENOMENOS.get(texto_en, texto_en.capitalize())
                else:
                    texto_formatado = texto_en
                termos.append(texto_formatado.capitalize())
        tempo_presente_txt = ", ".join(termos)
    else:
        tempo_presente_txt = "Sem fenômenos significativos" if idioma == 'pt' else "No significant phenomena"

    # Monta o objeto que alimenta os cartões do HTML
    informacoes_metar = {
        "bruto": metar_bruto,
        "visibilidade": visibilidade_txt,
        "teto": teto_txt,
        "vento": vento_txt,
        "qnh": f"{qnh_val} hPa" if qnh_val != "---" else "---",
        "tempo_presente": tempo_presente_txt
    }

    return render_template('index.html', info=informacoes_metar, erro=None, idioma=idioma)

if __name__ == '__main__':
    app.run(debug=True)