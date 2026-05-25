import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

# Carrega as variáveis do arquivo .env secreto
load_dotenv()

# Inicializando o servidor Flask
app = Flask(__name__)

<<<<<<< HEAD
<<<<<<< HEAD
# Puxa a chave do "cofre" em vez de deixar exposta
=======
>>>>>>> parent of ffb60c5 (otimizando)
minha_chave = os.getenv('API_KEY')
=======
API_KEY = os.getenv('API_KEY')
API_URL = "https://api.checkwx.com/metar/{aeroporto}/decoded"

MINIMOS_OPERACIONAIS = {
    "2": {"visibilidade": 3000, "teto": 1000},
    "default": {"visibilidade": 5000, "teto": 1500}
}
>>>>>>> parent of a211472 (otimizando)

# Rota principal do site
@app.route('/', methods=['GET', 'POST'])
def index():
<<<<<<< HEAD
<<<<<<< HEAD
    # Se o usuário clicou no botão "Processar" (Enviou o formulário)
    if request.method == 'POST':
        # Pegando os dados que foram digitados lá na página HTML
        aeroporto = request.form.get('icao').upper()
        tipo_anv = request.form.get('tipo_anv')

        # Regra de Mínimos Automáticos
=======
    if request.method == 'POST':
        aeroporto = request.form.get('icao').upper()
        tipo_anv = request.form.get('tipo_anv')

>>>>>>> parent of ffb60c5 (otimizando)
        if tipo_anv == "2":
            min_visibilidade = 3000
            min_teto = 1000
        else:
            min_visibilidade = 5000
            min_teto = 1500

<<<<<<< HEAD
        # Buscando na internet
=======
>>>>>>> parent of ffb60c5 (otimizando)
        url = f"https://api.checkwx.com/metar/{aeroporto}/decoded"
        cabecalho = {"X-API-Key": minha_chave}
        resposta = requests.get(url, headers=cabecalho)
=======
    if request.method != 'POST':
        return render_template('index.html')

    aeroporto = request.form.get('icao', '').strip().upper()
    tipo_anv = request.form.get('tipo_anv')

    if not aeroporto:
        return render_template('index.html', erro="Por favor, insira o código ICAO do aeródromo.")
>>>>>>> parent of a211472 (otimizando)

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

<<<<<<< HEAD
<<<<<<< HEAD
        # A Regra de Negócio
=======
>>>>>>> parent of ffb60c5 (otimizando)
        if visibilidade >= min_visibilidade and teto >= min_teto:
            resultado_final = f"OPERAÇÃO POR INSTRUMENTOS (IFR) / OPERAÇÃO VISUAL (VFR)"
        else:
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
            resultado_final = f"OPERAÇÃO POR INSTRUMENTOS (IFR) / FECHADO VISUAL (VFR)"
=======
            resultado_final = f"OPERAÇÃO POR INSTRUMENTOS (IFR) / FECHADO PARA VFR"

        # Devolvendo a resposta formatada para a tela HTML
>>>>>>> parent of 4ec4499 (atu)
=======
            resultado_final = f"OPERAÇÃO POR INSTRUMENTOS (IFR) / OPERAÇÃO VISUAL (VFR)"
=======
            resultado_final = f"OPERAÇÃO POR INSTRUMENTOS (IFR) / FECHADO VISUAL (VFR)"


>>>>>>> de09117c527f821658be66c5c1c45ce1060d777c
>>>>>>> parent of ffb60c5 (otimizando)
=======
            resultado_final = f"OPERAÇÃO POR INSTRUMENTOS (IFR) / FECHADO VISUAL (VFR)"
>>>>>>> parent of 8c7d5be (Update metar.py)
        return render_template('index.html', 
                               metar=metar_bruto, 
                               visibilidade=visibilidade, 
                               teto=teto, 
                               resultado=resultado_final)
<<<<<<< HEAD

    # Se ele só acessou a página, exibe o formulário vazio
    return render_template('index.html')

# Ligando o motor do servidor
if __name__ == '__main__':
    app.run(debug=True)
=======
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
<<<<<<< HEAD
>>>>>>> de09117c527f821658be66c5c1c45ce1060d777c
>>>>>>> parent of ffb60c5 (otimizando)
=======
>>>>>>> parent of 8c7d5be (Update metar.py)
        return render_template('index.html', 
                               metar=metar_bruto, 
                               visibilidade=visibilidade, 
                               teto=teto, 
                               resultado=resultado_final)
<<<<<<< HEAD
<<<<<<< HEAD
=======
    return render_template('index.html')
>>>>>>> parent of ffb60c5 (otimizando)
=======
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
>>>>>>> parent of a211472 (otimizando)
=======
>>>>>>> parent of 8c7d5be (Update metar.py)

if __name__ == '__main__':
    app.run(debug=True)