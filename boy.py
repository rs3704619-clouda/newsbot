import os
import telebot
import requests
from flask import Flask
from threading import Thread

# --- CONFIGURACIÓN ---
# Usa un Token de BotFather diferente al de Remove.bg para que no choquen
TOKEN = os.environ.get("TELEGRAM_TOKEN_NEWS") 
NEWS_KEY = os.environ.get("NEWS_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- SERVER PARA MANTENERLO VIVO ---
@app.route('/')
def home(): return "Hysterix News Bot: Activo 🕵️‍♂️"

def run_flask(): 
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))

# --- COMANDOS ---

@bot.message_handler(commands=['start', 'help'])
def send_help(message):
    texto = (
        "🕵️‍♂️ **Hysterix: Buscador de Historias**\n\n"
        "Usa estos comandos para cazar tu próximo guion:\n\n"
        "• `/noticias [tema]` - Busca cualquier tema (ej: `/noticias ovni`).\n"
        "• `/crimen` - Lo último en notas rojas y sucesos.\n"
        "• `/misterio` - Casos inexplicables y extraños.\n"
        "• `/paranormal` - Fantasmas, apariciones y más.\n\n"
        "🚀 *Busco noticias reales de todo el mundo en español.*"
    )
    bot.reply_to(message, texto, parse_mode="Markdown")

@bot.message_handler(commands=['noticias', 'crimen', 'misterio', 'paranormal'])
def fetch_news(message):
    # Lógica para definir qué buscar
    comando = message.text.split()[0]
    
    if comando == "/noticias":
        query = message.text.replace("/noticias", "").strip()
        if not query:
            return bot.reply_to(message, "⚠️ Escribe qué quieres buscar. Ejemplo: `/noticias tesoros`")
    elif comando == "/crimen": query = "crimen asesinato investigación"
    elif comando == "/misterio": query = "misterio inexplicable hallazgo"
    elif comando == "/paranormal": query = "paranormal fantasma ovni"

    bot.send_chat_action(message.chat.id, 'typing')

    # Llamada a la API (Buscamos noticias en español ordenadas por fecha)
    url = f"https://newsapi.org/v2/everything?q={query}&language=es&sortBy=publishedAt&apiKey={NEWS_KEY}"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        articulos = data.get('articles', [])

        if not articulos:
            return bot.reply_to(message, f"🚫 No encontré noticias recientes sobre '{query}'.")

        # Armamos el mensaje con las 3 noticias más frescas
        reporte = f"🔍 **REPORTES ENCONTRADOS: {query.upper()}**\n\n"
        
        for art in articulos[:3]:
            titulo = art.get('title', 'Sin título')
            url_nota = art.get('url', '#')
            fuente = art.get('source', {}).get('name', 'Fuente desconocida')
            
            reporte += f"📌 *{titulo}*\n🏛️ Fuente: {fuente}\n🔗 [Ver noticia completa]({url_nota})\n\n"

        bot.send_message(message.chat.id, reporte, parse_mode="Markdown", disable_web_page_preview=False)

    except Exception as e:
        bot.reply_to(message, f"☠️ Error al conectar con NewsAPI: {str(e)}")

# --- INICIO ---
if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("Buscador de Hysterix encendido... 🔍")
    bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
