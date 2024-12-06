from json import JSONDecodeError

import discord
from discord.ext import commands, tasks
import requests
from datetime import datetime
import json
import io
from random import random

from credentials import credentials
from messages import messages

DISCORD_CHANNEL_ID = credentials.get('DISCORD_CHANNEL_ID')
TWITCH_USERNAME = credentials.get('TWITCH_USERNAME')
TWITCH_CLIENT_SECRET = credentials.get('TWITCH_CLIENT_SECRET')
TWITCH_CLIENT_ID = credentials.get('TWITCH_CLIENT_ID')
DISCORD_TOKEN = credentials.get('DISCORD_TOKEN')

# Configurar Intents do Discord
intents = discord.Intents.default()
# Habilitar intents para guilds
intents.guilds = True
intents.members = True
# Habilitar intents para mensagens
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Armazenar o ID da última live para evitar notificações repetidas
last_stream_id = None

# Arquivo que armazena os IDs enviados
history_file = "history_ids.json"

# Set de IDs já anunciados
history_lives_annoucement = set()


# Registra os logs
def log_register(message):
  moment = datetime.now()
  print(f"{moment} {message}")
  open("logs.txt", "a").write(f"{moment} {message}\n")


# Carrega os IDs dos lives já anunciados
try:
  with open(history_file, "r") as f:
    history_lives_annoucement = set(json.load(f))
except FileNotFoundError:
  history_lives_annoucement = set()
except JSONDecodeError:
  log_register("JSONDecodeError: provavelmente o arquivo JSON está vazio.")
  history_lives_annoucement = set()


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
@tasks.loop(minutes=0.5)
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
      # Verifica se de id foi persistido no arquivo history_ids.json
      if current_stream_id not in history_lives_annoucement:
        log_register(f"ID da Live atual: {current_stream_id}. O ID atual não estava nos IDs anteriores.")

        if messages:
          message = messages[int(random() * len(messages))]
          if message:
            if message.count("{username}"):
              message = message.format(username=TWITCH_USERNAME)
          else:
            message = f"O canal {TWITCH_USERNAME} está ao vivo! Assista aqui:"
        else:
          message = f"O canal {TWITCH_USERNAME} está ao vivo! Assista aqui:"

        sender = f"@everyone {message} https://twitch.tv/{TWITCH_USERNAME}"
        await channel.send(sender)

        log_register(f"Mensagem: {sender}")
        log_register(f"Mensagem de aviso de Live enviada!")

        # Adiciona o ID da live atual à lista de anunciados
        history_lives_annoucement.add(current_stream_id)

        # Salva a lista atualizada em disco
        buffer = io.StringIO()
        json.dump(list(history_lives_annoucement), buffer)
        with open("history_ids.json", "w") as file:
          file.write(buffer.getvalue())
      else:
        log_register("O ID atual já foi anunciado.")
    else:
      # ...
      log_register(f"ID atual: {current_stream_id}.")
  else:
    print(f"O streamer {TWITCH_USERNAME} não está ao vivo.")


@bot.event
async def on_ready():
  log_register(f"Bot conectado como {bot.user}")
  try:
    # Inicia a tarefa de verificação
    check_stream_status.start()
  except Exception as error:
    log_register(f"Um erro ocorreu: {error}")


# Rodar o bot
try:
  bot.run(DISCORD_TOKEN)
except Exception as e:
  log_register(f"Ocorreu um erro: {str(e)}")
