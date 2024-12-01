# Bot para notificação de Lives no Discord

## Como funciona?

O bot tem a função de enviar mensagem em um canal específico do Discord quando ele verificar que um streamer determinado
iniciou uma live.

## O que é necessário?

- Python (versão 3.12 ou superior) instalado e configurado com o pip
- Packages do Discord, Requests e datetime para o funcionamento do bot
- Um editor de texto ou, preferencialmente, uma IDE
- Ter uma conta no discord e Twitch e acesso ao Discord Developer Portal e ao Console da Twitch
- Ter um servidor como comunidade no discord e um canal de texto

## Passo a passo para colocar o bot para funcionar

1. Crie uma pasta e dentro dela:
2. Baixe ou copie todo o conteúdo do arquivo [`Main.py`](Main.py)
3. Na mesma pasta crie um arquivo chamado `logs.txt`, um chamado `credentials.py` e outro chamado `history_ids.json`
4. Crie um app no Discord Developer Portal. Você pode configurá-lo com a permissão de acesso de "Administrador" ou
   definir as permissões. Importante que sejam definidas as permissões necessárias o envio de mensagens e outras (
   verificar os intents no código)
5. [Crie um app no Console da Twitch](https://dev.twitch.tv/docs/authentication/register-app/). É importante que você
   defina o tipo de cliente como "Confidencial" para gerar as credenciais necessárias. Também é importante anotar as
   credenciais informadas no processo de criação/configuração.
6. Adicione o app que você criou no Discord Developer Portal ao servidor que você deseja usá-lo.
4. No arquivo `credentials.py` defina:
   ```python
   credentials = {
     'DISCORD_TOKEN': '#', # token do app do discord (obtido através do portal de desenvolvedor)
     'TWITCH_CLIENT_ID': '123', # obtido através do console de desenvolvedor da twitch
     'TWITCH_CLIENT_SECRET': '123', # obtido através do console de desenvolvedor da twitch
     'TWITCH_USERNAME': 'twitch', # apenas o nickname do streamer
     'DISCORD_CHANNEL_ID': 123 # id do canal do discord, obtido pelo discord mesmo
   }
   ```
5. Coloque o código para rodar a partir do arquivo ``Main.py``. Verifique no console se ocorreu algum erro. Se deu tudo
   certo na conexão deve aparecer:

   ```bash
   [DATETIME] Bot conectado como [BOTNAME#1234]
   # 2024-11-28 15:49:58.280955 Bot conectado como BotAnuncioLive#2498
   ```
   Se o streamer não estiver online deve aparecer:
   ```bash
   O streamer [TWITCH_USERNAME] não está ao vivo.
   # O streamer Twitch não está ao vivo. 
   ```
9. Para deixar o bot rodando em um contâiner do Docker, basta criar o arquivo ``Dockerfile``, para configurar o
   contâiner e ``requirements.txt`` com as dependências necessárias.

   ```txt
   # requirements.txt
   discord.py~=2.4.0
   requests~=2.32.3
   ```
   
   ```Dockerfile
      # Use uma imagem base Python adequada (com a versão que seu projeto precisa)
      FROM python:3.9-slim-buster
      
      # Define o diretório de trabalho dentro do contêiner
      WORKDIR /app
      
      # Copia os arquivos de requisitos (se houver)
      COPY requirements.txt .
      
      # Instala as dependências do projeto
      RUN pip install -r requirements.txt
      
      # Copia o código-fonte do projeto
      COPY . .
      
      # Define a porta que a aplicação irá expor
      EXPOSE 8000
      
      # Comando para executar a aplicação
      CMD ["python", "Main.py"]
   ```
   
## Tecnologias utilizadas

- PyCharm
- Python
- Discord Developer Portal
- Console da Twitch
- Git e GitHub
- Docker