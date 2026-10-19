# 🌍 Briefing de Aeródromo / Aerodrome Briefing

A bilingual (English/Portuguese) briefing that shows the METAR and TAF of any aerodrome on a single screen, in plain language.

Briefing bilíngue (português/inglês) que mostra METAR e TAF de qualquer aeródromo numa tela só, em linguagem clara.

An internationalized Web Application built to decode raw aeronautical meteorological reports (METAR) in real-time. Features a native toggle between English and Portuguese, rendering complex aviation data into a clean, modern UI.

Uma aplicação Web internacionalizada construída para decodificar relatórios meteorológicos aeronáuticos (METAR) em tempo real com alternância nativa de idioma entre Inglês e Português.

---

## 🚀 Live Demo / Demonstração ao Vivo
👉 **[https://app-metar.onrender.com](https://app-metar.onrender.com)**

<br>*(Note: Hosted on a free server tier, the initial load may take a few seconds).*</br>
<br>*(Nota: Por estar em um servidor gratuito, o primeiro carregamento pode demorar alguns segundos).*</br>

---

## 💡 Features / Funcionalidades

### 🇺🇸 English
- **Real-time Data Fetching:** Integrates with CheckWX API for updated global airport reports.
- **Internationalization (i18n):** Native language toggle (PT-BR / EN-US) processed in the backend.
- **Phenomenon Mapping:** Advanced dictionary that maps and translates raw aviation codes.
- **Responsive Grid UI:** Modern layout built with CSS Grid tailored for quick data reading.
- **Exception Handling:** Resilient logic for API drops, connection failures, or invalid ICAO codes.
- **METAR + TAF:** Current weather report and aerodrome forecast decoded side by side.

### 🇧🇷 Português
- **Dados em Tempo Real:** Integração com a API CheckWX para relatórios atualizados de aeródromos globais.
- **Internacionalização (i18n):** Alternância nativa de idioma (PT-BR / EN-US) processada direto no backend.
- **Mapeamento de Fenômenos:** Dicionário avançado que mapeia e traduz códigos meteorológicos operacionais.
- **Interface Responsiva:** Layout moderno em CSS Grid feito para uma leitura rápida dos dados.
- **Tratamento de Exceções:** Lógica resiliente para quedas de API, falhas de conexão ou ICAO inválido.
- **METAR + TAF:** Boletim atual e previsão do aeródromo decodificados lado a lado.

---

## 🛠️ Tech Stack / Tecnologias Utilizadas

- **Backend:** Python, Flask, Requests, Python-Dotenv
- **Frontend:** HTML5, CSS3 (CSS Grid), Jinja2
- **Infrastructure / Infraestrutura:** Gunicorn, Render (Cloud Hosting & CI/CD)
