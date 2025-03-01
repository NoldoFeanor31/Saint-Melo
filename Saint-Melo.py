import os
import discord
import requests
import html
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Activar los intents adecuados
intents = discord.Intents.default()
intents.message_content = True  # Necesario para que funcionen los comandos

bot = commands.Bot(command_prefix="!", intents=intents)

async def obtener_versiculo():
    try:
        url = "https://www.biblegateway.com/votd/get/?format=json&version=RVR1960"
        respuesta = requests.get(url)
        data = respuesta.json()

        versiculo = html.unescape(data["votd"]["content"])  # Decodificar caracteres HTML
        referencia = data["votd"]["display_ref"]
        mensaje = f"📖 **{referencia}**\n{versiculo}"

        return mensaje[:4000]  # Asegurar que no exceda el límite de Discord
    except Exception as e:
        return f"⚠️ No se pudo obtener el versículo. Error: {e}"

@tasks.loop(hours=24)
async def enviar_versiculo_diario():
    await bot.wait_until_ready()  # Asegurar que el bot está listo antes de ejecutar la tarea
    canal = bot.get_channel(CHANNEL_ID)
    if canal:
        mensaje = await obtener_versiculo()
        print(f"🔍 Enviando versículo ({len(mensaje)} caracteres)")  # Depuración
        for parte in dividir_mensaje(mensaje):
            await canal.send(parte)

# Función para dividir mensajes largos respetando los límites de Discord
def dividir_mensaje(mensaje, limite=2000):
    partes = []
    while len(mensaje) > limite:
        corte = mensaje.rfind("\n", 0, limite)
        if corte == -1:
            corte = limite
        partes.append(mensaje[:corte])
        mensaje = mensaje[corte:].strip()
    partes.append(mensaje)
    return partes

@bot.event
async def on_ready():
    print(f"✅ {bot.user} está en línea.")
    enviar_versiculo_diario.start()

@bot.command()
async def versiculo(ctx):
    mensaje = await obtener_versiculo()
    for parte in dividir_mensaje(mensaje):
        await ctx.send(parte)

bot.run(TOKEN)
