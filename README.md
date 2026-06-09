# 🌍 METAR Weather Dashboard (Bilingual / Bilíngue)

An internationalized Web Application built to decode raw aeronautical meteorological reports (METAR) in real-time. Features a native toggle between English and Portuguese, rendering complex aviation data into a clean, modern UI.

Uma aplicação Web internacionalizada construída para decodificar relatórios meteorológicos aeronáuticos (METAR) em tempo real com alternância nativa de idioma entre Inglês e Português.

---

## 🚀 Live Demo / Demonstração ao Vivo
👉 **[https://app-metar.onrender.com](https://app-metar.onrender.com)**
*(Nota: Por estar em um servidor gratuito, o primeiro carregamento pode demorar alguns segundos para iniciar).*

---

## 💡 Features / Funcionalidades

- **Real-time Data Fetching:** Integrates with CheckWX API for updated global airport reports.
- **Internationalization (i18n):** Native language toggle (PT-BR / EN-US) processed in the backend.
- **Phenomenon Mapping:** Advanced dictionary that maps and translates raw aviation codes (e.g., Heavy Rain to Chuva Forte).
- **Responsive Grid UI:** Modern layout built with CSS Grid tailored for quick data reading.
- **Exception Handling:** Resilient logic for API drops, connection failures, or invalid ICAO codes.

---

## 🛠️ Tech Stack / Tecnologias Utilizadas

- **Backend:** Python, Flask, Requests (HTTP Library), Python-Dotenv
- **Frontend:** HTML5, CSS3 (Pure CSS Grid Layout), Jinja2
- **Infrastructure:** Gunicorn (WSGI Server), Render (Cloud Hosting & CI/CD)
