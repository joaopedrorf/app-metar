import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv('API_KEY')
API_URL = "https://api.checkwx.com/metar/{aeroporto}/decoded"

MINIMOS_OPERACIONAIS = {
    "2": {"visibilidade": 3000, "teto": 1000},
    "default": {"visibilidade": 5000, "teto": 1500}
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method != 'POST':
        return render_template('index.html')

    aeroporto = request.form.get('icao', '').strip().upper()
    tipo_anv = request.form.get('tipo_anv')

    if not aeroporto:
        return render_template('index.html', erro="Por favor, insira o código ICAO do aeródromo.")

    minimos = MINIMOS_OPERACIONAIS.get(tipo_anv, MINIMOS_OPERACIONAIS["default"])
    min_visibilidade = minimos["visibilidade"]
    min_teto = minimos["teto"]

    url = API_URL.format(aeroporto=aeroporto)
    cabecalho = {"X-API-Key": API_KEY}

    try:
        resposta = requests.get(url, headers=cabecalho, timeout=10)
        
        if resposta.status_code == 401:
            return render_template('index.html', erro="Acesso negado. Verifique as credenciais da API Key.")
        if resposta.status_code != 200:
            return render_template('index.html', erro="O serviço meteorológico externo está instável no momento.")
            
        dados_completos = resposta.json()
    except (requests.exceptions.RequestException, ValueError):
        return render_template('index.html', erro="Falha na conexão com o servidor de meteorologia.")

    if dados_completos.get('results', 0) == 0:
        return render_template('index.html', erro=f"Aeródromo {aeroporto} não encontrado ou sem METAR disponível.")
    
    dados = dados_completos['data'][0]
    metar_bruto = dados.get('raw_text', 'METAR indisponível no momento.')
    
    visibilidade = (dados.get('visibility') or {}).get('meters', 9999) 
    teto = (dados.get('ceiling') or {}).get('feet', 9999) 

    if visibilidade >= min_visibilidade and teto >= min_teto:
        status_vfr = "PERMITIDA (Condições VMC acima dos mínimos)"
        status_ifr = "DISPONÍVEL (Conforme cartas e auxílios do aeródromo)"
    else:
        status_vfr = "SUSPENSA (Condições IMC / Abaixo dos mínimos para voo visual)"
        status_ifr = "DISPONÍVEL (Operações restritas a procedimentos de voo por instrumentos)"

    return render_template(
        'index.html', 
        metar=metar_bruto, 
        visibilidade=visibilidade, 
        teto=teto, 
        status_vfr=status_vfr,
        status_ifr=status_ifr
    )

if __name__ == '__main__':
    app.run(debug=True)