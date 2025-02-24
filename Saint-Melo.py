import discord
import requests
import os
import html
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Configurar intents y crear el bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Función para obtener el versículo del día en español latinoamericano
def obtener_versiculo():
    url = "https://www.bible.com/es/verse-of-the-day"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text

        # Extraer el versículo y la referencia utilizando cadenas de búsqueda específicas
        start_index = data.find('<div class="votd-verse-text">') + len('<div class="votd-verse-text">')
        end_index = data.find('</div>', start_index)
        versiculo_texto = data[start_index:end_index].strip()

        start_index = data.find('<div class="votd-verse-reference">') + len('<div class="votd-verse-reference">')
        end_index = data.find('</div>', start_index)
        referencia = data[start_index:end_index].strip()

        # Decodificar entidades HTML
        versiculo_texto = html.unescape(versiculo_texto)
        referencia = html.unescape(referencia)

        mensaje = f"📖 **{referencia}**\n*{versiculo_texto}*"
        return mensaje

    except Exception as e:
        return f"⚠️ No se pudo obtener el versículo. Error: {e}"

# Tarea programada para enviar el versículo diariamente a las 8 AM
@tasks.loop(hours=24)
async def enviar_versiculo_diario():
    await bot.wait_until_ready()
    canal = bot.get_channel(CHANNEL_ID)
    if canal:
        mensaje = obtener_versiculo()
        await canal.send(mensaje)
    else:
        print("⚠️ Error: No se encontró el canal.")

# Comando para obtener el versículo manualmente
@bot.command(name="versiculo")
async def versiculo(ctx):
    mensaje = obtener_versiculo()
    await ctx.send(mensaje)

# Evento cuando el bot está listo
@bot.event
async def on_ready():
    print(f"✅ {bot.user} está en línea.")
    enviar_versiculo_diario.start()

# Iniciar el bot
bot.run(TOKEN)