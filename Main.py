import discord
from discord.ext import commands, tasks
import requests
from datetime import datetime

from credetials import credetials

DISCORD_CHANNEL_ID = credetials.get('DISCORD_CHANNEL_ID')
TWITCH_USERNAME = credetials.get('TWITCH_USERNAME')
TWITCH_CLIENT_SECRET = credetials.get('TWITCH_CLIENT_SECRET')
TWITCH_CLIENT_ID = credetials.get('TWITCH_CLIENT_ID')
TOKEN = credetials.get('TOKEN')

# Configurar Intents do Discord
intents = discord.Intents.default()
# Habilitar intents para guilds
intents.guilds = True
# Habilitar intents para mensagens
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Armazenar o ID da última live para evitar notificações repetidas
last_stream_id = None

# Registra os logs
def log_register(message):
    moment = datetime.now()
    print(f"{moment} {message}\n")
    open("logs.txt", "a").write(f"{moment} {message}\n")

# Obter o Token de Acesso da Twitch
def get_twitch_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, params=params)
    return response.json().get("access_token")

# Verificar se o canal está ao vivo e retornar o ID da live
def get_stream_id():
    url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USERNAME}"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {get_twitch_access_token()}"
    }
    response = requests.get(url, headers=headers)
    data = response.json().get("data")
    if data and data[0].get("type") == "live":
        return data[0].get("id")  # ID único da live atual
    return None

# Verificar se o canal está ao vivo
def is_stream_live():
    url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USERNAME}"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {get_twitch_access_token()}"
    }
    response = requests.get(url, headers=headers)
    data = response.json().get("data")
    return data and data[0].get("type") == "live"

# Tarefa de Verificação Periódica
@tasks.loop(minutes=1)
async def check_stream_status():
    global last_stream_id
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    current_stream_id = get_stream_id()

    if not channel:
        log_register(f"Canal com ID {DISCORD_CHANNEL_ID} não encontrado.")
        return
    if is_stream_live():
        if current_stream_id:
            # Se a live está ao vivo e o ID é diferente do último, notifique
            if current_stream_id != last_stream_id:
                log_register(f"ID da Live atual: {current_stream_id}. ID Anterior: {last_stream_id}.")
                last_stream_id = current_stream_id
                await channel.send(
                    f"@everyone O canal {TWITCH_USERNAME} está ao vivo! Assista aqui: https://www.twitch.tv/{TWITCH_USERNAME}")
                log_register(f"Mensagem de aviso de Live enviada!")
        else:
            # Se a live terminou, redefina last_stream_id para permitir nova notificação
            log_register(f"Resetando last_stream_id. ID Atual: {current_stream_id}. ID Anterior: {last_stream_id}.")
            last_stream_id = None
    else:
        print(f"O streamer {TWITCH_USERNAME} não está ao vivo.")

@bot.event
async def on_ready():
    log_register(f"Bot conectado como {bot.user}")
    # Inicia a tarefa de verificação
    check_stream_status.start()


# Rodar o bot
try:
    bot.run(TOKEN)
except Exception as e:
    log_register(f"Ocorreu um erro: {str(e)}")