from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

minha_chave = os.getenv('API_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        aeroporto = request.form.get('icao').upper()
        tipo_anv = request.form.get('tipo_anv')

        if tipo_anv == "2":
            min_visibilidade = 3000
            min_teto = 1000
        else:
            min_visibilidade = 5000
            min_teto = 1500

        url = f"https://api.checkwx.com/metar/{aeroporto}/decoded"
        cabecalho = {"X-API-Key": minha_chave}
        resposta = requests.get(url, headers=cabecalho)

        if resposta.status_code != 200:
            return render_template('index.html', erro="Servidor negou o acesso. Verifique a API Key.")

        dados_completos = resposta.json()

        if dados_completos.get('results', 0) == 0:
            return render_template('index.html', erro=f"Aeródromo {aeroporto} não encontrado ou sem METAR.")
        
        dados = dados_completos['data'][0]
        metar_bruto = dados['raw_text']
        visibilidade = dados.get('visibility', {}).get('meters', 9999) 
        teto = dados.get('ceiling', {}).get('feet', 9999) 

        if visibilidade >= min_visibilidade and teto >= min_teto:
            resultado_final = f"OPERAÇÃO POR INSTRUMENTOS (IFR) / OPERAÇÃO VISUAL (VFR)"
        else:
            resultado_final = f"OPERAÇÃO POR INSTRUMENTOS (IFR) / FECHADO VISUAL (VFR)"
        return render_template('index.html', 
                               metar=metar_bruto, 
                               visibilidade=visibilidade, 
                               teto=teto, 
                               resultado=resultado_final)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
        return render_template('index.html', 
                               metar=metar_bruto, 
                               visibilidade=visibilidade, 
                               teto=teto, 
                               resultado=resultado_final)

if __name__ == '__main__':
    app.run(debug=True)