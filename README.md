# ✈️ Painel Meteorológico para Tráfego Aéreo

Aplicação web desenvolvida em Python e Flask para decodificação de mensagens meteorológicas aéreas (METAR) via API REST CheckWX. O sistema analisa em tempo real os parâmetros de visibilidade e teto operacionais de aeródromos mundiais, determinando de forma objetiva a liberação ou suspensão de voos visuais (VFR) e por instrumentos (IFR).

## 🚀 Funcionalidades
- **Consulta ICAO Dinâmica:** Processamento e decodificação de dados meteorológicos oficiais de aeródromos.
- **Mínimos Operacionais Inteligentes:** Aplicação automática de restrições com base no tipo de aeronave (Asa Fixa vs. Asa Rotativa).
- **Fraseologia de Tráfego Aéreo:** Retorno direto, preciso e padronizado para mitigar erros de interpretação operacional.
- **Tratamento de Exceções:** Lógica resiliente para lidar com indisponibilidade de API, falhas de conexão ou códigos ICAO inexistentes.

## 🛠️ Tecnologias
- **Backend:** Python, Flask
- **Consumo de Dados:** Requests (API REST)
- **Frontend:** HTML5, CSS3, Jinja2 (Renderização Condicional)
- **Segurança:** Python-Dotenv (Gerenciamento de Variáveis de Ambiente)
