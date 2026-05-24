from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env secreto
load_dotenv()

# Inicializando o servidor Flask
app = Flask(__name__)

# Puxa a chave do "cofre" em vez de deixar exposta
minha_chave = os.getenv('API_KEY')

# Rota principal do site
@app.route('/', methods=['GET', 'POST'])
def index():
    # Se o usuário clicou no botão "Processar" (Enviou o formulário)
    if request.method == 'POST':
        # Pegando os dados que foram digitados lá na página HTML
        aeroporto = request.form.get('icao').upper()
        tipo_anv = request.form.get('tipo_anv')

        # Regra de Mínimos Automáticos
        if tipo_anv == "2":
            min_visibilidade = 3000
            min_teto = 1000
        else:
            min_visibilidade = 5000
            min_teto = 1500

        # Buscando na internet
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

        # A Regra de Negócio
        if visibilidade >= min_visibilidade and teto >= min_teto:
            resultado_final = f"OPERAÇÃO POR INSTRUMENTOS (IFR) / OPERAÇÃO VISUAL (VFR)"
        else:
            resultado_final = f"OPERAÇÃO POR INSTRUMENTOS (IFR) / FECHADO VISUAL (VFR)"

        # Devolvendo a resposta formatada para a tela HTML
        return render_template('index.html', 
                               metar=metar_bruto, 
                               visibilidade=visibilidade, 
                               teto=teto, 
                               resultado=resultado_final)

    # Se ele só acessou a página, exibe o formulário vazio
    return render_template('index.html')

# Ligando o motor do servidor
if __name__ == '__main__':
    app.run(debug=True)