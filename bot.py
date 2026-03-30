import os
import telebot
import requests
from flask import Flask
from threading import Thread

# --- CONFIGURACIÓN ---
# Asegúrate de tener estas variables en Railway -> Settings -> Variables
TOKEN = os.environ.get("TELEGRAM_TOKEN_NEWS") 
NEWS_KEY = os.environ.get("NEWS_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- SERVER PARA RAILWAY ---
@app.route('/')
def home(): 
    return "Hysterix News Bot: Operativo y Filtrando 🕵️‍♂️"

def run_flask():
    # Railway asigna el puerto dinámicamente
    puerto = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=puerto)

# --- COMANDOS ---

@bot.message_handler(commands=['start', 'help'])
def send_help(message):
    texto = (
        "🕵️‍♂️ **Hysterix: Buscador de Historias v2.0**\n\n"
        "He ajustado los filtros para que no te den noticias basura:\n\n"
        "• `/noticias [tema]` - Busca el tema en el TITULO (más preciso).\n"
        "• `/crimen` - Notas rojas e investigaciones fuertes.\n"
        "• `/misterio` - Casos inexplicables y hallazgos raros.\n"
        "• `/paranormal` - Lo más fresco de ovnis y fantasmas.\n\n"
        "🚀 *Tip: Si buscas algo específico, usa una sola palabra clave.*"
    )
    bot.reply_to(message, texto, parse_mode="Markdown")

@bot.message_handler(commands=['noticias', 'crimen', 'misterio', 'paranormal'])
def fetch_news(message):
    comando = message.text.split()[0]
    query = ""
    
    # Configuración de búsqueda según comando
    if comando == "/noticias":
        query = message.text.replace("/noticias", "").strip()
        if not query:
            return bot.reply_to(message, "⚠️ ¿Qué buscamos? Ej: `/noticias naufragio`")
    elif comando == "/crimen": query = "asesinato investigación suceso"
    elif comando == "/misterio": query = "misterio inexplicable hallazgo"
    elif comando == "/paranormal": query = "ovni fantasma paranormal"

    bot.send_chat_action(message.chat.id, 'typing')

    # --- EL CAMBIO MAGICO: qInTitle ---
    # Esto obliga a la API a que la palabra esté a huevo en el título
    url = f"https://newsapi.org/v2/everything?qInTitle={query}&language=es&sortBy=publishedAt&apiKey={NEWS_KEY}"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        articulos = data.get('articles', [])

        if not articulos:
            return bot.reply_to(message, f"🚫 No hay nada nuevo en los titulares sobre '{query}'.")

        reporte = f"🔍 **RESULTADOS FILTRADOS: {query.upper()}**\n\n"
        
        # Solo mandamos las 3 mejores para no saturar
        for art in articulos[:3]:
            titulo = art.get('title', 'Sin título')
            url_nota = art.get('url', '#')
            fuente = art.get('source', {}).get('name', 'Fuente')
            
            reporte += f"📌 *{titulo}*\n🏛️ Fuente: {fuente}\n🔗 [Ver noticia]({url_nota})\n\n"

        bot.send_message(message.chat.id, reporte, parse_mode="Markdown", disable_web_page_preview=False)

    except Exception as e:
        bot.reply_to(message, f"☠️ Error técnico: {str(e)}")

# --- ARRANQUE ---
if __name__ == "__main__":
    # Hilo para el servidor web (Railway Health Check)
    Thread(target=run_flask).start()
    print("Buscador Hysterix v2.0 encendido... 🔍")
    # Polling infinito para Telegram
    bot.infinity_polling(skip_pending=True)
