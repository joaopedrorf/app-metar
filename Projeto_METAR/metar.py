from dotenv import load_dotenv
from flask import Flask, render_template, request

# Carrega o .env antes de importar módulos que leem variáveis de ambiente
load_dotenv()

from briefing import montar_briefing  # noqa: E402
from textos import TEXTOS  # noqa: E402

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    # Detecta o idioma selecionado (padrão 'pt')
    idioma = request.form.get('idioma', 'pt') if request.method == 'POST' else 'pt'
    if idioma not in TEXTOS:
        idioma = 'pt'
    t = TEXTOS[idioma]

    if request.method != 'POST':
        return render_template('index.html', briefing=None, erro=None, idioma=idioma, t=t)

    aeroporto = request.form.get('icao', '').strip().upper()

    # Trocar o idioma com o campo vazio só redesenha a tela, sem erro
    if not aeroporto:
        return render_template('index.html', briefing=None, erro=None, idioma=idioma, t=t)

    if len(aeroporto) != 4 or not aeroporto.isalpha():
        return render_template('index.html', briefing=None, erro=t['icao_invalido'], idioma=idioma, t=t, icao=aeroporto)

    briefing = montar_briefing(aeroporto, idioma, t)
    return render_template('index.html', briefing=briefing, erro=None, idioma=idioma, t=t, icao=aeroporto)


if __name__ == '__main__':
    app.run(debug=True)
