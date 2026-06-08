import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv('API_KEY')
API_URL = "https://api.checkwx.com/metar/{aeroporto}/decoded"

MINIMOS_OPERACIONAIS = {
    "2": {"visibilidade": 1500, "teto": 600},
    "default": {"visibilidade": 5000, "teto": 1500}
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method != 'POST':
        return render_template('index.html', metar=None, erro=None)

    aeroporto = request.form.get('icao', '').strip().upper()
    tipo_anv = request.form.get('tipo_anv')

    if not aeroporto or len(aeroporto) != 4:
        return render_template('index.html', erro="Por favor, insira um código ICAO válido com 4 letras.", metar=None)

    minimos = MINIMOS_OPERACIONAIS.get(tipo_anv, MINIMOS_OPERACIONAIS["default"])
    min_visibilidade = minimos["visibilidade"]
    min_teto = minimos["teto"]

    url = API_URL.format(aeroporto=aeroporto)
    cabecalho = {"X-API-Key": API_KEY}

    try:
        resposta = requests.get(url, headers=cabecalho, timeout=10)
        
        if resposta.status_code == 401:
            return render_template('index.html', erro="Chave de API inválida ou não autorizada.", metar=None)
        if resposta.status_code != 200:
            return render_template('index.html', erro="Serviço meteorológico indisponível no momento.", metar=None)
            
        dados_completos = resposta.json()
    except (requests.exceptions.RequestException, ValueError):
        return render_template('index.html', erro="Falha na conexão com o servidor de meteorologia.", metar=None)

    if dados_completos.get('results', 0) == 0 or not dados_completos.get('data'):
        return render_template('index.html', erro=f"Aeródromo {aeroporto} não encontrado ou sem METAR disponível.", metar=None)
    
    dados = dados_completos['data'][0]
    metar_bruto = dados.get('raw_text')
    
    if not metar_bruto:
        return render_template('index.html', erro=f"Dados brutos do aeródromo {aeroporto} indisponíveis.", metar=None)
    
    visibilidade = dados.get('visibility', {}).get('meters', 9999) if dados.get('visibility') else 9999
    teto = dados.get('ceiling', {}).get('feet', 9999) if dados.get('ceiling') else 9999

    if visibilidade >= min_visibilidade and teto >= min_teto:
        resultado = "OPERANDO POR INSTRUMENTOS (IFR) / OPERANDO VISUAL (VFR)"
    else:
        resultado = "OPERANDO POR INSTRUMENTOS (IFR)"

    return render_template(
        'index.html', 
        metar=metar_bruto, 
        visibilidade=visibilidade, 
        teto=teto, 
        resultado=resultado,
        erro=None
    )

if __name__ == '__main__':
    app.run(debug=False)